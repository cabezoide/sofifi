# SPDX-License-Identifier: MIT
"""Lote 9 del catálogo: mosaico, un bucle sonido sobre sonido a ½×, 1× y 2×.

Lo que distingue al mosaico de un looper: la misma nota suena a la vez una
octava abajo y una octava arriba, y la realimentación decide cuánto dura el pad.
"""

from __future__ import annotations

from functools import cache

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, potencia, pots, programa, rms, tono

F = 330.0
X = Senal(FS, (tono(F, 0.25, 0.3) + (0,) * int(1.2 * FS),))


@cache
def tocar(octavas: str, realimentacion: str) -> tuple[int, ...]:
    """pot0 y pot3 = `octavas`, voz 1× y mezcla a 1, sin difusión."""
    c = Controles(pots(octavas, "1", "1", octavas, realimentacion, "0"))
    return procesar(programa("mosaico"), Senal(FS, X.canales), c).canales[0]


def test_mosaico_suena_una_octava_abajo_y_otra_arriba() -> None:
    """Antes de la primera vuelta (0,67 s) solo suenan las voces ½× y 2×, en f/2 y en 2f."""
    sin, con = tocar("0", "0"), tocar("0.8", "1")
    assert rms(sin, 0.3, 0.6) == 0  # pot0 = pot3 = 0: el pad calla hasta la vuelta
    assert rms(con, 0.3, 0.6) > 0.03  # medido: 0,073
    nota = potencia(con, F, 0.3, 0.6)
    assert potencia(con, F / 2, 0.3, 0.6) > 1000 * nota  # medido: ×40 000
    assert potencia(con, 2 * F, 0.3, 0.6) > 1000 * nota  # medido: ×35 000


def test_mosaico_la_realimentacion_alarga_el_pad() -> None:
    """La nota (la voz 1×) vuelve cada 0,67 s; la segunda vuelta depende de pot4."""

    def segunda_sobre_primera(y: tuple[int, ...]) -> float:
        return potencia(y, F, 1.37, 1.45) / potencia(y, F, 0.70, 0.78)

    corta, larga = segunda_sobre_primera(tocar("0", "0")), segunda_sobre_primera(tocar("0.8", "1"))
    assert larga > 0.5 and larga > 4 * corta  # medido: 0,95 y 0,089


def test_mosaico_nivel_parecido_al_plate() -> None:
    for amplitud, cola in ((0.1, 0.4), (0.5, 0.6)):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(cola * FS),))
        y = procesar(
            programa("mosaico"), x, Controles(pots("0.6", "0.6", "0.6", "0.6", "0.6", "0.5"))
        )
        p = procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1")))
        n = x.muestras / FS
        r = rms(y.canales[0], 0, n) / rms(p.canales[0], 0, n)
        assert 0.2 < r < 2.0  # medido: 0,39 y 0,41
