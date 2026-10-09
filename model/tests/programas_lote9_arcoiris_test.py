# SPDX-License-Identifier: MIT
"""Lote 9 del catálogo, pitch: arcoiris.

Las pruebas miden lo que distingue al programa: la voz A sube o baja el tono de
forma continua, y la regeneración alarga la estela sin que el pico se desboque.
"""

from __future__ import annotations

from functools import cache

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, potencia, pots, programa, rms, tono

# pot0 intervalo · pot1 segunda voz · pot2 mezcla · pot3 tiempo · pot4 regeneración · pot5 tono
SIN_B = "0.5"


def test_arcoiris_la_voz_a_transpone_el_tono() -> None:
    """Un tono a f sale a f·razón: +7 con pot0 = 0,79 y −12 con pot0 = 0."""
    f = 330.0
    x = Senal(FS, (tono(f, 0.3, 0.3),))
    for p0, razon, minimo in (("0.79", 1.49831, 500), ("0", 0.5, 2000)):
        c = Controles(pots(p0, SIN_B, "1", "0", "0", "1"))
        y = procesar(programa("arcoiris"), x, c).canales[0]
        assert potencia(y, f * razon, 0.15, 0.3) > minimo * potencia(y, f, 0.15, 0.3)
        # medido: ×2 518 (+7) y ×13 159 (−12)


def test_arcoiris_la_regeneracion_alarga_la_estela_y_el_pico_queda_acotado() -> None:
    """A a +7 y B a −12: sin regeneración la estela muere; con el pedal pisado, autooscila."""
    x = Senal(FS, (tono(330, 0.2, 0.3) + (0,) * int(0.9 * FS),))
    mandos = pots("0.79", "0", "1", "0.3", "0", "0.6")
    seca = procesar(programa("arcoiris"), x, Controles(mandos)).canales[0]
    pisado = Controles(mandos, tramos_sw=((0, len(x.canales[0])),))
    viva = procesar(programa("arcoiris"), x, pisado).canales[0]
    assert rms(seca, 0.7, 1.1) < 0.001  # medido: 0,00001
    assert rms(viva, 0.7, 1.1) > 0.2  # medido: 0,46
    assert max(abs(v) for v in viva) / (1 << 23) < 0.95  # medido: 0,85


@cache
def _plate(amplitud: float) -> float:
    x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
    return rms(procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1)


def test_arcoiris_nivel_razonable_frente_al_plate() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        c = Controles(pots("0.79", "0.25", "0.5", "0.3", "0.5", "0.6"))
        nivel = rms(procesar(programa("arcoiris"), x, c).canales[0], 0, 1)
        assert 0.2 * _plate(amplitud) < nivel < 2 * _plate(amplitud)  # medido: ×0,62 y ×0,70
