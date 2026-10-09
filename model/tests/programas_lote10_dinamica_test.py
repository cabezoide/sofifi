# SPDX-License-Identifier: MIT
"""Lote 10 del catálogo: dinamica, un plate cuyo decay y damping siguen a la fuerza.

La misma nota a 0,1 y a 0,5 de amplitud da colas distintas. El sentido sigue a
pot3: con pot3 = 1, tocar fuerte acorta la cola; con pot3 = 0, la alarga; con
pot3 = 0,5, el programa es casi un plate.
"""

from __future__ import annotations

from functools import cache

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, pots, programa, rms, tono

SUAVE, FUERTE = 0.1, 0.5


@cache
def _salida(amplitud: float, p3: str, nota: float, cola: float, nombre: str) -> tuple[int, ...]:
    x = Senal(FS, (tono(196, nota, amplitud) + (0,) * int(cola * FS),))
    c = Controles(pots("0.7", "0.3", "1", p3))
    return procesar(programa(nombre), x, c).canales[0]


def _caida(amplitud: float, p3: str, nombre: str = "dinamica") -> float:
    """Nota de 0,2 s. Cola entre 0,75 y 1 s dividida por la cola entre 0,3 y 0,45 s."""
    y = _salida(amplitud, p3, 0.2, 0.8, nombre)
    return rms(y, 0.75, 1.0) / rms(y, 0.3, 0.45)


def test_dinamica_el_sentido_lo_da_la_profundidad() -> None:
    # pot3 = 1: fuerte da una cola mucho más corta (medido: 0,80 y 0,127, ×6,3).
    assert _caida(SUAVE, "1") > 4 * _caida(FUERTE, "1")
    # pot3 = 0: fuerte da una cola más larga (medido: 0,95 y 1,49, ×1,6).
    assert _caida(FUERTE, "0") > 1.3 * _caida(SUAVE, "0")


def test_dinamica_sin_profundidad_es_casi_un_plate() -> None:
    """Con pot3 = 0,5, la caída fuerte es la del plate (medido: 0,842 y 0,826)."""
    din, plate = _caida(FUERTE, "0.5"), _caida(FUERTE, "0.5", "plate")
    assert abs(din - plate) < 0.1 * plate


def test_dinamica_nivel_como_el_plate() -> None:
    """Con pot3 = 0 (la cola más larga), el RMS queda cerca del plate (medido: ×1,05 y ×1,17)."""
    for a in (SUAVE, FUERTE):
        din = rms(_salida(a, "0", 0.4, 0.6, "dinamica"), 0, 1.0)
        plate = rms(_salida(a, "0", 0.4, 0.6, "plate"), 0, 1.0)
        assert 0.2 * plate < din < 2 * plate
