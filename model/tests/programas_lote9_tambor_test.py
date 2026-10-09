# SPDX-License-Identifier: MIT
"""Lote 9 del catálogo: tambor, el eco de tambor magnético de cuatro cabezas.

Lo que distingue a tambor de bruma y del delay: los ecos salen solo en los
tiempos de las cabezas elegidas, y con las cuatro cabezas y el swell al máximo
la realimentación no se desboca. La última prueba mide el nivel.
"""

from __future__ import annotations

from functools import cache
from itertools import pairwise

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, impulso, maximos, pots, programa, rms, tono

# pot0 = 0,5 → depth = 0 desde la primera muestra: sin deslizamiento del tiempo.
# La cabeza k lee a k·(1221 + 4096) muestras (P = 0,44 s).
CUARTO = 1221 + 4096


def _ecos(cabezas: str) -> list[int]:
    """Posiciones de los ecos de un impulso, sin realimentación y solo con ecos."""
    c = Controles(pots("0.5", "0", "1", cabezas, "0", "1"))
    y = procesar(programa("tambor"), impulso(0.45), c).canales[0]
    return maximos(y, 0.05)


def test_tambor_los_ecos_salen_solo_en_las_cabezas_elegidas() -> None:
    """Con las cabezas 1+2+4, los ecos están en P/4, P/2 y P, y no en 3P/4."""
    esperado = [k * CUARTO for k in (1, 2, 4)]
    ecos = _ecos("0.85")  # zona 9: cabezas 1+2+4
    assert len(ecos) == 3  # medido: 5315, 10631 y 21262
    assert all(abs(e - k) < 0.001 * k for e, k in zip(ecos, esperado, strict=True))


def test_tambor_con_las_cuatro_cabezas_y_swell_maximo_no_se_desboca() -> None:
    """La realimentación es la media de las cabezas: la cola baja aunque se sumen cuatro."""
    x = Senal(FS, (tono(196, 0.1, 0.5) + (0,) * int(0.8 * FS),))
    # pot0 = 1: vuelta de 0,1 s; el bucle más corto (cabeza 1) da 36 vueltas en 0,9 s.
    c = Controles(pots("1", "1", "1", "0.95", "0", "1"))
    y = procesar(programa("tambor"), x, c).canales[0]
    tramos = [rms(y, t / 10, t / 10 + 0.1) for t in range(1, 9)]
    assert all(b < a for a, b in pairwise(tramos[1:]))  # la cola baja en cada tramo
    assert tramos[-1] < 0.3 * max(tramos)  # medido: ×0,17
    assert max(abs(v) for v in y) < 0.9 * 2**23  # sin llegar al CLIP; medido: 0,68


@cache
def _plate(amplitud: float) -> float:
    x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
    return rms(procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1)


def test_tambor_nivel_razonable_frente_al_plate() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        c = Controles(pots("0.5", "0.5", "0.5", "0.95", "0.3", "0.6"))
        nivel = rms(procesar(programa("tambor"), x, c).canales[0], 0, 1)
        assert 0.2 * _plate(amplitud) < nivel < 2 * _plate(amplitud)  # medido: ×0,43 y ×0,49
