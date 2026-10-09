# SPDX-License-Identifier: MIT
"""Lote 14 del catálogo: arpegio.

Con un tono fijo, el programa toca un arpegio: en cada paso suena otra nota.
Las pruebas miden que cada nota llega en su paso, que el modo menor baja la
tercera y que el nivel queda cerca del plate.
"""

from __future__ import annotations

from functools import cache

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, potencia, pots, programa, rms, tono

F = 330.0
PASO = 0.6  # segundos por paso con pot0 = 0


def _banda(y: tuple[int, ...], fc: float, a: float, b: float) -> float:
    """Energía en ±12 Hz de fc: el shifter de dos tomas corre la línea unos hercios."""
    return sum(potencia(y, fc + d, a, b) for d in range(-12, 13, 3))


@cache
def _arpegio(pot3: str) -> tuple[int, ...]:
    """Cuatro pasos de un tono de 330 Hz, con cuatro notas, lento y solo efecto."""
    x = Senal(FS, (tono(F, 4 * PASO, 0.3),))
    return procesar(programa("arpegio"), x, Controles(pots("0", "1", "1", pot3))).canales[0]


def _energia(pot3: str, semitonos: int, paso: int) -> float:
    """Energía de una nota en la parte abierta de un paso."""
    a = paso * PASO + 0.06
    return _banda(_arpegio(pot3), F * 2 ** (semitonos / 12), a, a + 0.3)


def test_arpegio_toca_cada_nota_en_su_paso() -> None:
    """Con cuatro notas (1-3-5-8), cada nota tiene su máximo en un paso distinto."""
    for paso, s in enumerate((0, 4, 7, 12)):
        e = [_energia("0", s, k) for k in range(4)]
        otras = max(v for k, v in enumerate(e) if k != paso)
        # medido: la nota propia vale 1,47× (la quinta) o más que su eco del paso siguiente
        assert e[paso] > 1.3 * otras, (s, e)


def test_modo_menor_baja_la_tercera() -> None:
    """En el paso 2 suena la tercera mayor (+4) o la menor (+3) según pot3."""
    assert _energia("0", 4, 1) > 10 * _energia("0", 3, 1)  # medido: ×48
    assert _energia("1", 3, 1) > 10 * _energia("1", 4, 1)  # medido: ×101


def test_nivel_acotado_frente_al_plate() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        y = procesar(programa("arpegio"), x, Controles(pots("0.7", "0.3", "1"))).canales[0]
        p = procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0]
        r = rms(y, 0, 1.0) / rms(p, 0, 1.0)
        assert 0.2 < r < 2, (amplitud, r)  # medido: 0,50 y 0,58
