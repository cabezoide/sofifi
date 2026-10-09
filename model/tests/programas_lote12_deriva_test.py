# SPDX-License-Identifier: MIT
"""Lote 12 del catálogo: deriva, eco cuyo tiempo salta al azar y llega con glide.

Las pruebas miden lo que distingue a deriva de cinta: el tono del eco de un
tono fijo se aparta mucho y a saltos, solo si hay profundidad. Con pot4 en la
zona de semitonos, el eco suena a un semitono exacto. Con glide lento, el tono
se mueve poco entre ventanas cortas.
"""

from __future__ import annotations

from itertools import pairwise

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, frecuencias, pots, programa, rms, tono

F = 500.0
X = Senal(FS, (tono(F, 2.5, 0.3),))


def _relativas(
    profundidad: str, glide: str, velocidad: str = "1", ventana: float = 0.05
) -> list[float]:
    """Frecuencia del eco / F por ventanas, desde 0,6 s (solo eco, sin realimentación)."""
    c = Controles(pots("0.3", profundidad, "1", velocidad, glide, "0"))
    y = procesar(programa("deriva"), X, c).canales[0]
    return [f / F for f in frecuencias(y, 0.6, 2.5, ventana)]


def test_deriva_el_tono_del_eco_salta_solo_con_profundidad() -> None:
    r = _relativas("1", "0")
    assert min(r) < 0.75 and max(r) > 1.3  # medido: 0,55 y 1,49 (glide rápido)
    # Saltos: entre dos ventanas de 50 ms, el tono cambia mucho alguna vez.
    assert max(abs(b - a) for a, b in pairwise(r)) > 0.1  # medido: 0,29
    fijo = _relativas("0", "0")
    assert all(abs(v - 1) < 0.002 for v in fijo)  # medido: ±0,0004


def test_deriva_semitonos_exactos_y_glide_lento_gradual() -> None:
    semitono = 2 ** (1 / 12)
    r = _relativas("1", "0.6", "0.5")
    # Donde el tono se para (dos ventanas iguales), está en un semitono exacto.
    quietas = [b for a, b in pairwise(r) if abs(b - a) < 0.001]
    assert len(quietas) > 0.3 * len(r)  # medido: 0,42 de las ventanas
    # Error medido: ≤ 0,0008 (1,4 cents). Con glide libre (pot4 = 0,27) es 0,055.
    assert all(min(abs(v - n) for n in (1 / semitono, 1, semitono)) < 0.002 for v in quietas)
    assert min(r) < 0.947 and max(r) > 1.055  # medido: 0,943 y 1,059 (diseño: 0,944 y 1,059)
    # Glide lento: entre ventanas de 20 ms el tono apenas cambia.
    lento = _relativas("1", "0.45", "0.5", 0.02)
    assert max(lento) - min(lento) > 0.02  # medido: 0,028: el tono se mueve
    assert max(abs(b - a) for a, b in pairwise(lento)) < 0.008  # medido: 0,0054


def test_deriva_nivel() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        c = Controles(pots("0.3", "0.5", "0.5", "0.5", "0", "0.5"))
        nivel = rms(procesar(programa("deriva"), x, c).canales[0], 0, 1)
        assert 0.2 * plate < nivel < 2 * plate  # medido: ×0,78 y ×0,89
