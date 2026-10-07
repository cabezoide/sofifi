# SPDX-License-Identifier: MIT
"""Regenera ``demo_examples/``: una guitarra sintética y su paso por cada programa.

La guitarra es un arpegio de Em9 con cuerdas Karplus-Strong y semilla fija. El
núcleo es bit-exact y no hay remuestreo (la señal ya está a 48 828 Hz), así que
el audio es determinista.

Las demos se guardan en Ogg Vorbis (ADR 0001, actualización): unas 10 veces
menos que un WAV. El códec da el mismo audio cada vez, pero el fichero cambia
en su número de serie. Por eso un ``.ogg`` solo se reescribe si su audio cambia:
regenerar sin cambios no toca git.

Uso: ``.venv/bin/python scripts/generar_demos.py``  (unos 4 min; necesita
``pip install -e '.[demos]'``)
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile  # type: ignore[import-untyped]
from sofifi.adapters.archivos import ensamblar_archivo
from sofifi.adapters.wav import a_pcm16
from sofifi.domain.aritmetica import DATO_MAX, DATO_MIN, FS_WAV, dato
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar

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
    ("lofi", {0: "0.6", 1: "0.7", 2: "0.7", 3: "0.4"}, (), 1.0),
    ("swell", {0: "0.7", 1: "0.3", 2: "0.5", 3: "0.4"}, (), 4.0),
    ("chorus", {0: "0.3", 1: "0.6", 2: "0.5"}, (), 1.0),
    ("flanger", {0: "0.15", 1: "0.8", 2: "0.5", 3: "0.6"}, (), 1.0),
    ("phaser", {0: "0.2", 1: "0.9", 2: "0.5", 3: "0.5"}, (), 1.0),
    ("tremolo", {0: "0.3", 1: "0.7", 2: "0.6"}, (), 1.0),
    ("vibrato", {0: "0.4", 1: "0.5", 2: "1"}, (), 1.0),
)
# Calidad de Vorbis: 0 es la mejor. Con 0,3, una demo de 8 s ocupa unos 190 kB.
COMPRESION = 0.3


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


def escribir_ogg(ruta: Path, senal: Senal) -> bool:
    """Escribe ``ruta`` si su audio cambia. Devuelve True si la ha escrito."""
    with tempfile.TemporaryDirectory() as tmp:
        nuevo = Path(tmp) / ruta.name
        soundfile.write(
            nuevo,
            a_pcm16(senal),
            senal.fs_hz,
            format="OGG",
            subtype="VORBIS",
            compression_level=COMPRESION,
        )
        if ruta.exists():
            antes = soundfile.read(ruta, dtype="int16")[0]
            despues = soundfile.read(nuevo, dtype="int16")[0]
            if antes.shape == despues.shape and np.array_equal(antes, despues):
                return False
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_bytes(nuevo.read_bytes())
    return True


def main() -> int:
    seca = guitarra()
    destino = DESTINO / "demo_guitarra.ogg"
    print(
        f"seca → {destino.relative_to(ROOT)}" + ("" if escribir_ogg(destino, seca) else " (igual)")
    )
    for nombre, pots, tramos, cola in DEMOS:
        controles = Controles(
            tuple(dato(pots.get(i, "0")) for i in range(6)),
            tuple((round(a * FS_WAV), round(b * FS_WAV)) for a, b in tramos),
        )
        programa = ensamblar_archivo(ROOT / "programas" / f"{nombre}.sasm")
        salida = procesar(programa, seca, controles, round(cola * FS_WAV))
        destino = DESTINO / f"demo_{nombre}.ogg"
        escrita = escribir_ogg(destino, salida)
        print(f"{nombre} → {destino.relative_to(ROOT)}" + ("" if escrita else " (igual)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
