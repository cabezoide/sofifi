# SPDX-License-Identifier: MIT
"""Lote 9 del catálogo: desplazador, un eco con desplazamiento de frecuencia.

Lo que lo distingue de un eco: cada eco sale d Hz más arriba (o más abajo) que
el anterior. La banda contraria queda muy baja: la red de Hilbert funciona.
"""

from __future__ import annotations

from functools import cache

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, potencia, pots, programa, rms, tono

F = 440.0
D = 16.0  # pot0 = 0,9: u = 0,8 y d = 25·u² = 16 Hz


def test_desplazador_el_primer_eco_sale_en_f_mas_d() -> None:
    """Primer eco (355 ms) de un tono de 440 Hz: a la izquierda en f + d; a la derecha, en f − d."""
    x = Senal(FS, (tono(F, 0.55, 0.3) + (0,) * int(0.15 * FS),))
    c = Controles(pots("0.9", "0.5", "1", "0", "1", "1"))
    izq, der = procesar(programa("desplazador"), x, c).canales

    def banda(v: tuple[int, ...], f: float) -> float:
        return potencia(v, f, 0.4, 0.65)

    assert banda(izq, F + D) > 100 * banda(izq, F - D)  # medido: ×2,3·10⁶ (64 dB)
    assert banda(der, F - D) > 100 * banda(der, F + D)  # medido: ×4,3·10⁶ (66 dB)
    # Con el footswitch pisado, la izquierda desplaza al revés.
    pisado = Controles(c.pots, ((0, x.muestras),))
    izq_sw = procesar(programa("desplazador"), x, pisado).canales[0]
    assert banda(izq_sw, F - D) > 100 * banda(izq_sw, F + D)  # medido: ×6,9·10⁶ (68 dB)


def test_desplazador_cada_vuelta_suma_d_otra_vez() -> None:
    """Con realimentación, el segundo eco (510 ms) ya está en f + 2d: la cola sube en espiral."""
    x = Senal(FS, (tono(F, 0.15, 0.3) + (0,) * int(0.55 * FS),))
    c = Controles(pots("0.9", "0.35", "1", "0.85", "1", "0"))
    izq = procesar(programa("desplazador"), x, c).canales[0]
    p = {n: potencia(izq, F + n * D, 0.53, 0.65) for n in (0, 1, 2)}
    assert p[2] > 30 * p[1] and p[2] > 30 * p[0]  # medido: ×1 800 y ×940


@cache
def _plate(amplitud: float) -> float:
    x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
    return rms(procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1)


def test_desplazador_nivel_razonable_frente_al_plate() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        c = Controles(pots("0.7", "0.4", "0.5", "0.5", "0.7", "0.5"))
        nivel = rms(procesar(programa("desplazador"), x, c).canales[0], 0, 1)
        assert 0.2 * _plate(amplitud) < nivel < 2 * _plate(amplitud)  # medido: ×0,58 y ×0,68
