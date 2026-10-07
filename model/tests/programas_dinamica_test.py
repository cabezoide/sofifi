# SPDX-License-Identifier: MIT
"""Dinámica, filtros y textura: compresor, puerta, autowah, filtro y saturación.

Cada prueba mide la relación entre la entrada y la salida que define al
efecto: cuánto sube la salida cuando sube la entrada, qué pasa con el ruido,
cómo se mueve un filtro o cuántos armónicos aparecen.
"""

from __future__ import annotations

import math

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, potencia, pots, programa, rms, tono


def nivel(nombre: str, amplitud: float, controles: tuple[str, ...], f: float = 330) -> float:
    x = Senal(FS, (tono(f, 0.6, amplitud),))
    y = procesar(programa(nombre), x, Controles(pots(*controles))).canales[0]
    return rms(y, 0.3, 0.6)


def test_compresor_reduce_la_diferencia_de_nivel() -> None:
    """Entrada ×8: sin compresión, la salida sube ×8; con compresión 1, ×3,2."""

    def razon(comp: str) -> float:
        c = ("0.2", comp, "1", "0")
        return nivel("compresor", 0.8, c) / nivel("compresor", 0.1, c)

    assert 7.9 < razon("0") < 8.1
    assert 2.0 < razon("1") < 4.0  # medido: 3,22


def test_puerta_calla_el_ruido_y_deja_pasar_la_nota() -> None:
    assert nivel("puerta", 0.005, ("0.3", "0.3")) < 0.01 * 0.005 / math.sqrt(2)
    assert nivel("puerta", 0.3, ("0.3", "0.3")) > 0.99 * 0.3 / math.sqrt(2)


def test_autowah_abre_el_filtro_cuando_se_toca_fuerte() -> None:
    """2 kHz: si se toca suave, el filtro está abajo; si se toca fuerte, sube hasta él."""
    suave = nivel("autowah", 0.02, ("1", "0.6", "1"), 2000) / (0.02 / math.sqrt(2))
    fuerte = nivel("autowah", 0.5, ("1", "0.6", "1"), 2000) / (0.5 / math.sqrt(2))
    assert fuerte > 2.5 * suave  # medido: 0,98 y 0,28


def test_filtro_barre_con_el_lfo() -> None:
    def niveles(prof: str) -> list[float]:
        x = Senal(FS, (tono(1500, 2.0, 0.3),))
        y = procesar(programa("filtro"), x, Controles(pots("0.3", "0.5", "1", prof))).canales[0]
        return [rms(y, t / 20, (t + 1) / 20) for t in range(4, 40)]

    quieto, barrido = niveles("0"), niveles("1")
    assert max(quieto) < 1.01 * min(quieto)
    assert max(barrido) > 5 * min(barrido)  # medido: 19,9


def test_saturacion_crea_armonicos() -> None:
    def tercero(ganancia: str) -> float:
        x = Senal(FS, (tono(220, 0.5, 0.3),))
        c = Controles(pots(ganancia, "1", "1", "1"))
        y = procesar(programa("saturacion"), x, c).canales[0]
        return potencia(y, 660, 0.1, 0.5) / potencia(y, 220, 0.1, 0.5)

    assert tercero("1") > 5 * tercero("0")  # medido: 0,110 y 0,007
