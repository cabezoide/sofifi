# SPDX-License-Identifier: MIT
"""Guitarra sintética (domain/estimulo.py): determinista y con huella fija.

La huella la comparten las demos y la pista de la microSD. Si cambia, cambian
todas las demos: hay que regenerarlas con scripts/generar_demos.py.
"""

from __future__ import annotations

import hashlib

from sofifi.domain.aritmetica import DATO_MAX, DATO_MIN, FS_WAV
from sofifi.domain.estimulo import DURACION_S, guitarra

HUELLA = "a16732bfd761048c"


def _huella(muestras: tuple[int, ...]) -> str:
    crudo = b"".join(int(v).to_bytes(4, "big", signed=True) for v in muestras)
    return hashlib.sha256(crudo).hexdigest()[:16]


def test_huella_estable() -> None:
    senal = guitarra()
    assert senal.muestras == int(FS_WAV * DURACION_S)
    assert _huella(senal.canales[0]) == HUELLA, "si cambia, regenera las demos"


def test_determinista() -> None:
    assert guitarra(duracion_s=0.05).canales == guitarra(duracion_s=0.05).canales


def test_dentro_del_rango_y_con_nivel() -> None:
    muestras = guitarra(duracion_s=1.0).canales[0]
    assert min(muestras) >= DATO_MIN
    assert max(muestras) <= DATO_MAX
    assert max(abs(v) for v in muestras) > DATO_MAX // 100  # suena, no es silencio
