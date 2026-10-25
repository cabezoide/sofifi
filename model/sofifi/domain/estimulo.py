# SPDX-License-Identifier: MIT
"""Estímulo de prueba: una guitarra sintética determinista.

Es la entrada de las demos (``scripts/generar_demos.py``) y de la pista de la
microSD (``sofifi pista --sintetica``, Fase 13). Así, lo que suena en la placa y
lo que suena en el PC salen de la misma señal.

La guitarra es un arpegio de Em9 con cuerdas Karplus-Strong y semilla fija. No
hay remuestreo, porque la señal ya está a fs. El resultado es el mismo en
cualquier máquina: el generador de azar de numpy lleva semilla y la salida se
cuantiza a 16 bit, como una grabación.
"""

from __future__ import annotations

import numpy as np

from sofifi.domain.aritmetica import DATO_MAX, DATO_MIN, FS_WAV
from sofifi.domain.senal import Senal

NOTAS_HZ = (82.41, 123.47, 164.81, 185.00, 246.94, 293.66, 369.99)  # Em9
SEPARACION_S = 0.22
DURACION_S = 4.0
SEMILLA = 7
AMPLITUD = 0.12


def guitarra(
    duracion_s: float = DURACION_S,
    separacion_s: float = SEPARACION_S,
    notas_hz: tuple[float, ...] = NOTAS_HZ,
    semilla: int = SEMILLA,
) -> Senal:
    """Arpegio de cuerdas Karplus-Strong, en dato S.23 y a fs."""
    rng = np.random.default_rng(semilla)
    y = np.zeros(int(FS_WAV * duracion_s))
    for i, f in enumerate(notas_hz):
        inicio = int(i * separacion_s * FS_WAV)
        if inicio >= len(y):
            break  # con una duración corta no entran todas las notas
        periodo = int(FS_WAV / f)
        cuerda = rng.uniform(-1, 1, periodo)
        salida = np.zeros(len(y) - inicio)
        for k in range(len(salida)):
            j = k % periodo
            salida[k] = cuerda[j]
            cuerda[j] = 0.996 * 0.5 * (cuerda[j] + cuerda[(k + 1) % periodo])
        y[inicio:] += AMPLITUD * salida
    # Cuantizada a 16 bit (como una grabación típica) y alineada a S.23.
    pcm16 = np.trunc(np.clip(y, -1, 1) * 32767).astype(np.int64)
    muestras = np.clip(pcm16 << 8, DATO_MIN, DATO_MAX)
    return Senal(FS_WAV, (tuple(int(v) for v in muestras),))
