# SPDX-License-Identifier: MIT
"""Lote 11 del catálogo: dados, cuatro ecos con tiempos y octavas al azar.

Las pruebas miden lo que distingue al programa de un eco con varias tomas:
los cuatro tiempos son distintos y caben en el máximo de pot0, una pisada de
sw los cambia, y con pot3 = 1 los ecos salen a una octava de distancia.
"""

from __future__ import annotations

from itertools import pairwise

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, impulso, maximos, potencia, pots, programa, rms, tono

# pot0 = 0,5: tiempo máximo = (0,15 + 0,8·0,5) · 32 768 muestras.
MAXIMO = 0.55 * 32768 / FS
EN = int(0.2 * FS)  # el impulso llega a los 0,2 s


def _ecos(tramos_sw: tuple[tuple[int, int], ...] = ()) -> list[float]:
    """Tiempos (s) de los ecos de un impulso: sin realimentación, sin octavas."""
    c = Controles(pots("0.5", "0", "1", "0", "1", "0"), tramos_sw=tramos_sw)
    y = procesar(programa("dados"), impulso(0.6, EN), c).canales[0]
    picos: list[int] = []
    for k in maximos(y, 0.08):
        if not picos or k - picos[-1] > 50:  # una toma entre dos muestras da dos máximos
            picos.append(k)
    return [(k - EN) / FS for k in picos]


def test_dados_cuatro_ecos_distintos_y_una_pisada_los_cambia() -> None:
    antes = _ecos()
    despues = _ecos(((int(0.05 * FS), int(0.1 * FS)),))
    # medido: 0,079 · 0,122 · 0,280 · 0,312 s; tras la pisada, 0,038 · 0,197 · 0,212 · 0,364 s
    for t in (antes, despues):
        assert len(t) == 4
        assert all(b - a > 0.01 for a, b in pairwise(t))
        assert t[0] > 0 and t[-1] < MAXIMO
    assert sum(abs(a - b) > 0.005 for a, b in zip(antes, despues, strict=True)) >= 3


def test_dados_con_probabilidad_1_los_ecos_salen_a_una_octava() -> None:
    f = 330.0
    x = Senal(FS, (tono(f, 0.3, 0.3) + (0,) * int(0.5 * FS),))

    def octavas(probabilidad: str) -> float:
        c = Controles(pots("0.5", "0", "1", probabilidad, "1", "0"))
        y = procesar(programa("dados"), x, c).canales[0]
        fuera = potencia(y, 2 * f, 0.35, 0.8) + potencia(y, f / 2, 0.35, 0.8)
        return fuera / potencia(y, f, 0.35, 0.8)

    # medido: 0,013 con pot3 = 0 y ≈ 4·10⁵ con pot3 = 1
    assert octavas("0") < 0.05
    assert octavas("1") > 100


def test_dados_nivel_comparable_al_plate() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        c = Controles(pots("0.5", "0.5", "1", "0.5", "0.5", "0.5"))
        y = rms(procesar(programa("dados"), x, c).canales[0], 0, 1)
        assert 0.2 * plate < y < 2 * plate  # medido: ×0,66 (0,1) y ×0,77 (0,5)
