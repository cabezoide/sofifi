#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Mide el nivel de los presets de ``presets/banco.toml`` con el modelo bit-exact.

Cuándo: después de añadir presets o de cambiar un programa que tiene presets.
No está en la compuerta: medir los 1 032 presets cuesta unos 1 000 s de CPU
(unos 3 minutos con 6 procesos).

Para cada preset, el modelo procesa un rasgueo de 0,6 s y 0,4 s de cola, con
los mandos del preset. El rasgueo son las seis cuerdas al aire (mi2 a mi4), con
seis armónicos cada una, que entran cada 10 ms y se apagan en unos 0,4 s. Su
pico es 0,5. Una sola nota engaña: un chorus o un flanger tiene un nulo de
peine en una frecuencia, y un wah puede quedar fuera de su banda (F-36).
Con ``--sw``, el pulsador se pisa de 0,05 a 0,5 s. El script compara la salida con la entrada:

- **SATURA:** más del 1 % de las muestras de un canal llegan a |x| ≥ 0,99.
- **FUERTE:** el nivel de salida pasa de +6 dB sobre el de la entrada. El nivel
  es el RMS máximo en ventanas de 50 ms: el RMS de toda la prueba castigaría a
  los efectos que sostienen la nota, que no suenan más fuertes.
- **SILENCIO:** el nivel de salida queda por debajo de −40 dB. Es un aviso, no un
  fallo: un swell lento o un looper sin grabar empiezan en silencio.

Uso::

    .venv/bin/python scripts/medir_presets.py                 # todo el banco
    .venv/bin/python scripts/medir_presets.py plate hall      # solo esos programas
    .venv/bin/python scripts/medir_presets.py --sw freeze     # con el pulsador pisado
    .venv/bin/python scripts/medir_presets.py --todos         # imprime también los que cumplen

Solo lee: no escribe ningún fichero. Salida: 0 si ningún preset da SATURA ni
FUERTE; 1 si alguno los da; 2 si un programa no existe.
"""

from __future__ import annotations

import argparse
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

from sofifi.adapters.archivos import ensamblar_archivo
from sofifi.adapters.presets import leer_banco
from sofifi.domain.aritmetica import FS_WAV, dato
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar

RAIZ = Path(__file__).resolve().parent.parent
FS = FS_WAV
ESCALA = float(1 << 23)
CUERDAS_HZ = (82.41, 110.0, 146.83, 196.0, 246.94, 329.63)
ARMONICOS, NOTA_S, COLA_S, PICO, CAIDA_S, RASGUEO_S = 6, 0.6, 0.4, 0.5, 0.4, 0.01
VENTANA_S = 0.05
SW = (0.05, 0.5)


def nota() -> tuple[int, ...]:
    """El rasgueo de prueba, normalizado a pico PICO, y su cola en silencio."""
    n = int(NOTA_S * FS)
    suma = [0.0] * n
    for c, f in enumerate(CUERDAS_HZ):
        inicio = int(c * RASGUEO_S * FS)
        for k in range(inicio, n):
            t = (k - inicio) / FS
            caida = math.exp(-t / CAIDA_S)
            suma[k] += caida * sum(
                math.sin(2 * math.pi * f * h * t) / h for h in range(1, ARMONICOS + 1)
            )
    escala = PICO / max(abs(v) for v in suma)
    rasgueo = tuple(dato(str(round(escala * v, 6))) for v in suma)
    return rasgueo + (0,) * int(COLA_S * FS)


def _rms(muestras: tuple[int, ...]) -> float:
    """El RMS máximo en ventanas de 50 ms, en fondo de escala."""
    n = int(VENTANA_S * FS)
    return (
        max(
            math.sqrt(sum(v * v for v in muestras[k : k + n]) / n)
            for k in range(0, len(muestras) - n + 1, n)
        )
        / ESCALA
    )


def medir(trabajo: tuple[str, str, tuple[Fraction, ...], bool]) -> tuple[str, list[str]]:
    """Una línea de informe y la lista de avisos de un preset."""
    programa, nombre, valores, sw = trabajo
    x = nota()
    pots = tuple(dato(v) for v in valores)
    tramos = ((int(SW[0] * FS), int(SW[1] * FS)),) if sw else ()
    prog = ensamblar_archivo(RAIZ / "programas" / f"{programa}.sasm")
    y = procesar(prog, Senal(FS, (x,)), Controles(pots, tramos_sw=tramos))
    salida = max(_rms(canal) for canal in y.canales)
    pico = max(abs(v) for canal in y.canales for v in canal) / ESCALA
    satura = max(sum(abs(v) >= 0.99 * ESCALA for v in c) / len(c) for c in y.canales)
    db = 20 * math.log10(salida / _rms(x)) if salida > 0 else -math.inf
    avisos = []
    if satura > 0.01:
        avisos.append("SATURA")
    if db > 6:
        avisos.append("FUERTE")
    if db < -40:
        avisos.append("SILENCIO")
    linea = f"{programa}/{nombre}: {db:+6.1f} dB, pico {pico:.2f}, satura {100 * satura:4.1f} %"
    return linea + ("  " + " ".join(avisos) if avisos else ""), avisos


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("programas", nargs="*", help="solo los presets de estos programas")
    ap.add_argument("--sw", action="store_true", help="pisa el pulsador de 0,05 a 0,5 s")
    ap.add_argument("--todos", action="store_true", help="imprime también los que cumplen")
    args = ap.parse_args(argv)
    banco = leer_banco(RAIZ / "presets" / "banco.toml")
    faltan = [p for p in args.programas if p not in banco]
    if faltan:
        print(f"no hay presets de: {', '.join(faltan)}", file=sys.stderr)
        return 2
    elegidos = args.programas or sorted(banco)
    trabajos = [(p, n, vs, args.sw) for p in elegidos for n, vs in banco[p].items()]
    fallos = 0
    with ProcessPoolExecutor(6) as procesos:
        for linea, avisos in procesos.map(medir, trabajos, chunksize=8):
            fallos += "SATURA" in avisos or "FUERTE" in avisos
            if args.todos or avisos:
                print(linea, flush=True)
    print(f"medir_presets: {len(trabajos)} presets, {fallos} con SATURA o FUERTE")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
