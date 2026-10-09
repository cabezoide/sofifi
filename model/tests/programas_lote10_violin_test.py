# SPDX-License-Identifier: MIT
"""Violín: cada nota sube desde el silencio y el vibrato espera a que la nota tenga edad.

Las pruebas usan un tono de 196 Hz (sol de la cuerda 3) y solo la salida del
efecto (pot2 = 1). Las ventanas de RMS duran 5 periodos del tono.
"""

from __future__ import annotations

from itertools import pairwise

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, frecuencias, pots, programa, rms, tono

F = 196.0
PERIODOS_5 = 5 / F


def salida(x: Senal, *valores: str) -> tuple[int, ...]:
    return procesar(programa("violin"), x, Controles(pots(*valores))).canales[0]


def test_el_nivel_sube_sin_pua_durante_la_subida() -> None:
    """Con pot0 = 0,5 la rampa dura unos 0,18 s; con pot0 = 1, unos 1,5 s."""
    x = Senal(FS, (tono(F, 0.5, 0.4),))
    rapida, lenta = salida(x, "0.5", "0.3", "1", "0"), salida(x, "1", "0.3", "1", "0")
    tramos = [k * PERIODOS_5 for k in range(8)]  # de 0 a 0,18 s
    niveles = [rms(rapida, t, t + PERIODOS_5) for t in tramos]
    assert all(b > a for a, b in pairwise(niveles))
    final = rms(rapida, 0.3, 0.5)
    assert niveles[0] < 0.02 * final  # medido: 0,000 (y 0,75 a los 0,18 s)
    assert rms(lenta, 0.3, 0.5) < 0.2 * final  # medido: 0,06


def test_el_vibrato_espera_el_retardo_de_pot1() -> None:
    """Con pot1 = 0,5 el vibrato empieza a los 0,55 s; con pot1 = 0, a los 0,1 s."""
    x = Senal(FS, (tono(F, 1.4, 0.4),))

    def desvio(retardo: str, a: float, b: float) -> float:
        f = frecuencias(salida(x, "0.3", retardo, "1", "0.8", "0.3", "0.5"), a, b, 0.02)
        return max(abs(v - F) for v in f)

    assert desvio("0.5", 0.15, 0.5) < 1.0  # medido: 0,17 Hz
    assert desvio("0.5", 1.0, 1.4) > 3.0  # medido: 4,3 Hz
    assert desvio("0", 0.3, 0.5) > 2.0  # medido: 2,8 Hz


def test_nivel_cercano_al_plate() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        y = salida(x, "0.5", "0.3", "1", "0.5", "0.3", "0.5")
        plate = procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0]
        relacion = rms(y, 0, 1.0) / rms(plate, 0, 1.0)
        assert 0.2 < relacion < 2  # medido: 0,64 y 0,72
