# SPDX-License-Identifier: MIT
"""Lote 13 del catálogo: resbalon, cabeza de velocidad libre sobre un búfer que graba siempre.

Las pruebas miden lo que distingue a resbalon de looper y de granular: la
velocidad continua cambia la altura sin pulsar nada, con velocidad negativa
un barrido sale al revés, y las costuras de las dos cabezas no hacen clics.
"""

from __future__ import annotations

import math
from itertools import pairwise

from sofifi.domain.aritmetica import UNO, dato
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, frecuencias, potencia, pots, programa, rms, tono

# pot0 para cada velocidad: 0 → −2×, 0,2333 → −1×, 0,5833 → ½×, 0,75 → 1×, 1 → 2×.
V_MENOS_2, V_MENOS_1, V_MEDIO, V_1, V_2 = "0", "0.2333", "0.5833", "0.75", "1"


def _salida(x: Senal, *mandos: str) -> tuple[int, ...]:
    return procesar(programa("resbalon"), x, Controles(pots(*mandos))).canales[0]


def test_resbalon_la_velocidad_cambia_la_altura() -> None:
    """Con un tono f, v = 2 da 2f y v = ½ da f/2: la energía se va a la nueva altura."""
    f = 440.0
    x = Senal(FS, (tono(f, 0.8, 0.3),))
    rapido = _salida(x, V_2, "0", "1", "0.3")
    lento = _salida(x, V_MEDIO, "0", "1", "0.3")
    assert potencia(rapido, 2 * f, 0.4, 0.8) > 100 * potencia(rapido, f, 0.4, 0.8)  # ×1 076
    assert potencia(lento, f / 2, 0.4, 0.8) > 100 * potencia(lento, f, 0.4, 0.8)  # ×1 413


def test_resbalon_al_reves_y_sin_clics() -> None:
    """Con v = −1, un barrido que sube sale bajando dentro de cada ventana.

    Las costuras no hacen clics: el salto mayor entre dos muestras es el de un
    seno puro a la nueva altura.
    """
    n = int(1.0 * FS)
    barrido = tuple(
        dato(str(round(0.3 * math.sin(2 * math.pi * (1000 * k / FS + 500 * (k / FS) ** 2)), 6)))
        for k in range(n)
    )
    x = Senal(FS, (barrido,))

    def bajan(velocidad: str) -> float:
        fr = frecuencias(_salida(x, velocidad, "0", "1", "1"), 0.3, 1.0, 0.01)
        d = [b - a for a, b in pairwise(fr)]
        return sum(1 for v in d if v < 0) / len(d)

    assert bajan(V_MENOS_1) > 0.6  # medido: 0,71
    assert bajan(V_1) < 0.05  # medido: 0,0

    f, a = 196.0, 0.5
    x = Senal(FS, (tono(f, 0.6, a),))
    pendiente = 2 * math.pi * (2 * f) / FS * a  # la de un seno a 2f
    for velocidad in (V_2, V_MENOS_2):
        y = _salida(x, velocidad, "0", "1", "0")[int(0.3 * FS) :]
        salto = max(abs(q - p) for p, q in pairwise(y)) / UNO
        assert salto < 1.1 * pendiente  # medido: ×1,000 y ×0,999


def test_resbalon_nivel() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        for mandos in (
            (V_MENOS_2, "1", "1", "1", "0", "0.5"),  # medido: ×1,02 y ×1,14
            ("0.5", "0.3", "0.5", "0.5"),  # mandos de la huella; medido: ×0,55 y ×0,63
        ):
            assert 0.2 * plate < rms(_salida(x, *mandos), 0, 1) < 2 * plate
