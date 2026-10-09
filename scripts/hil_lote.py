# SPDX-License-Identifier: MIT
"""Prueba en la placa una lista de programas y cadenas, uno detrás de otro.

Cuándo: al añadir un lote de programas al catálogo, o para repetir la prueba
de todo el catálogo en el silicio.

Uso::

    .venv/bin/python scripts/hil_lote.py --todos          # todo lo que cabe en hil_nucleo
    .venv/bin/python scripts/hil_lote.py marea "Eco y muelle"

Para cada nombre ejecuta ``make hil HIL=NOMBRE`` (ROM, síntesis, carga en SRAM y
comparación con el modelo) y escribe una fila en ``build/hil_lote.csv``:
nombre, resultado, muestras iguales, ciclos por muestra en la placa y MHz que
da nextpnr. Cada nombre tarda unos 4 minutos. Los que no caben en la memoria de
hil_nucleo se saltan con ``--todos``.

Si un nombre pasa de 20 minutos, el script mata su ``make`` con todos sus
procesos, escribe «TIEMPO AGOTADO» en su fila y sigue con el siguiente. Si eso
pasa, el puente UART del BL616 puede quedar colgado: reconecta el USB (F-02).

Necesita la placa, la UART en ``/dev/ttyUSB1`` y la cadena EDA del ``.venv``.
Salida: 0 si todos son iguales al modelo; 1 si alguno no lo es o se agota.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

from sofifi.adapters.cadenas import leer_cadenas, programa_o_cadena

RAIZ = Path(__file__).resolve().parent.parent
PROGRAMAS = RAIZ / "programas"
CADENAS = RAIZ / "presets" / "cadenas.toml"
PALABRAS_HIL = 38_912  # el mismo límite que `sofifi rom`
SALIDA = RAIZ / "build" / "hil_lote.csv"
LIMITE_S = 1200  # un nombre normal tarda unos 4 minutos


def caben() -> list[str]:
    """Programas y cadenas que caben en la memoria de retardo de hil_nucleo."""
    nombres = [r.stem for r in sorted(PROGRAMAS.glob("*.sasm"))]
    nombres += [c.nombre for c in leer_cadenas(CADENAS)]
    lista = []
    for n in nombres:
        try:
            programa = programa_o_cadena(n, PROGRAMAS, CADENAS)
        except ValueError:  # cadena que no compone: le faltan registros o LFOs
            continue
        if programa.palabras_memoria <= PALABRAS_HIL:
            lista.append(n)
    return lista


def ejecutar(orden: list[str], limite_s: float) -> str | None:
    """La salida estándar de ``orden``, o None si pasa de ``limite_s`` segundos.

    La orden corre en un grupo de procesos propio. Si se agota el tiempo, el
    grupo entero muere: también yosys, nextpnr o el cargador que lance make.
    """
    with subprocess.Popen(
        orden,
        cwd=RAIZ,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        start_new_session=True,
    ) as proceso:
        try:
            salida, _ = proceso.communicate(timeout=limite_s)
        except subprocess.TimeoutExpired:
            os.killpg(proceso.pid, signal.SIGKILL)
            proceso.communicate()
            return None
    return salida


def probar(nombre: str) -> dict[str, str]:
    salida = ejecutar(["make", "-s", "hil", f"HIL={nombre}"], LIMITE_S)
    if salida is None:
        return {
            "nombre": nombre,
            "resultado": "TIEMPO AGOTADO",
            "iguales": f"más de {LIMITE_S} s",
            "ciclos_placa": "",
            "mhz_nextpnr": "",
        }
    iguales = re.search(r"hil: (\d+) muestras recibidas, (\d+) iguales", salida)
    ciclos = re.search(r"máximo (\d+) ciclos/muestra", salida)
    mhz = re.search(r'"alcanzada_mhz": ([\d.]+)', salida)
    correcto = (
        iguales is not None and iguales[1] == iguales[2] == "4096" and "CRC correcto" in salida
    )
    return {
        "nombre": nombre,
        "resultado": "igual" if correcto else "DISTINTO",
        "iguales": f"{iguales[2]}/{iguales[1]}" if iguales else "sin respuesta",
        "ciclos_placa": ciclos[1] if ciclos else "",
        "mhz_nextpnr": mhz[1] if mhz else "",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "nombres",
        nargs="*",
        help="programas (programas/NOMBRE.sasm) o cadenas (presets/cadenas.toml)",
    )
    ap.add_argument("--todos", action="store_true", help="todo lo que cabe en hil_nucleo")
    args = ap.parse_args(argv)
    nombres = caben() if args.todos else args.nombres
    SALIDA.parent.mkdir(exist_ok=True)
    fallos = 0
    with SALIDA.open("w", newline="", encoding="utf-8") as f:
        campos = ["nombre", "resultado", "iguales", "ciclos_placa", "mhz_nextpnr"]
        escritor = csv.DictWriter(f, campos, delimiter=";")
        escritor.writeheader()
        for k, nombre in enumerate(nombres, 1):
            inicio = time.monotonic()
            fila = probar(nombre)
            escritor.writerow(fila)
            f.flush()
            fallos += fila["resultado"] != "igual"
            print(
                f"[{k}/{len(nombres)}] {nombre}: {fila['resultado']} ({fila['iguales']}, "
                f"{fila['ciclos_placa']} ciclos, {time.monotonic() - inicio:.0f} s)",
                flush=True,
            )
    print(f"hil_lote: {len(nombres) - fallos} de {len(nombres)} iguales al modelo → {SALIDA}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
