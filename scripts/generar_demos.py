# SPDX-License-Identifier: MIT
"""Regenera ``demo_examples/``: una guitarra sintética y su paso por cada programa.

La guitarra es un arpegio de Em9 con cuerdas Karplus-Strong y semilla fija, así
que todo es determinista: el núcleo es bit-exact y no hay remuestreo (la
señal ya está a 48 828 Hz). Volver a correrlo debe dar los mismos bytes.

Uso: ``.venv/bin/python scripts/generar_demos.py``  (unos 3 min)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from sofifi.adapters.archivos import FuenteProgramaArchivo
from sofifi.adapters.wav import FuenteWav, SumideroWav
from sofifi.domain.aritmetica import DATO_MAX, DATO_MIN, FS_WAV, dato
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import renderizar

ROOT = Path(__file__).resolve().parent.parent
DESTINO = ROOT / "demo_examples"
NOTAS_HZ = (82.41, 123.47, 164.81, 185.00, 246.94, 293.66, 369.99)  # Em9
SEPARACION_S = 0.22
DURACION_S = 4.0
SEMILLA = 7

# (programa, pots, tramos de freeze en segundos, cola en segundos)
DEMOS: tuple[tuple[str, dict[int, str], tuple[tuple[float, float], ...], float], ...] = (
    ("plate", {0: "0.7", 1: "0.3", 2: "0.45"}, (), 4.0),
    ("shimmer", {0: "0.75", 1: "0.25", 2: "0.55", 3: "0.6"}, (), 6.0),
    ("freeze", {0: "0.6", 1: "0.3", 2: "0.5"}, ((2.5, 8.0),), 6.0),
    ("hall", {0: "0.75", 1: "0.35", 2: "0.45"}, (), 5.0),
    ("cloud", {0: "0.7", 1: "0.3", 2: "0.55", 3: "0.6"}, (), 6.0),
    ("cinta", {0: "0.45", 1: "0.55", 2: "0.4", 3: "0.5"}, (), 5.0),
    ("reverse", {0: "0.6", 1: "0.4", 2: "0.5"}, (), 3.0),
)
# PCM de 16 bit: para escuchar no se pierde nada, y las demos caben en los
# 16 MiB que admite la compuerta secrets. El render es bit-exact en 24 bit.
BITS_DEMO = 16


def guitarra() -> Senal:
    rng = np.random.default_rng(SEMILLA)
    y = np.zeros(int(FS_WAV * DURACION_S))
    for i, f in enumerate(NOTAS_HZ):
        inicio = int(i * SEPARACION_S * FS_WAV)
        periodo = int(FS_WAV / f)
        cuerda = rng.uniform(-1, 1, periodo)
        salida = np.zeros(len(y) - inicio)
        for k in range(len(salida)):
            j = k % periodo
            salida[k] = cuerda[j]
            cuerda[j] = 0.996 * 0.5 * (cuerda[j] + cuerda[(k + 1) % periodo])
        y[inicio:] += 0.12 * salida
    # Cuantizada a 16 bit (como una grabación típica) y alineada a S.23.
    pcm16 = np.trunc(np.clip(y, -1, 1) * 32767).astype(np.int64)
    muestras = np.clip(pcm16 << 8, DATO_MIN, DATO_MAX)
    return Senal(FS_WAV, (tuple(int(v) for v in muestras),))


def main() -> int:
    seca = DESTINO / "demo_guitarra.wav"
    SumideroWav(seca, BITS_DEMO).escribir(guitarra())
    print(f"seca → {seca.relative_to(ROOT)}")
    for nombre, pots, tramos, cola in DEMOS:
        controles = Controles(
            tuple(dato(pots.get(i, "0")) for i in range(6)),
            tuple((round(a * FS_WAV), round(b * FS_WAV)) for a, b in tramos),
        )
        salida = DESTINO / f"demo_{nombre}.wav"
        renderizar(
            FuenteProgramaArchivo(ROOT / "programas" / f"{nombre}.sasm"),
            FuenteWav(seca),
            SumideroWav(salida, BITS_DEMO),
            controles,
            round(cola * FS_WAV),
        )
        print(f"{nombre} → {salida.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
