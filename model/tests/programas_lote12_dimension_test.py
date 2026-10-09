# SPDX-License-Identifier: MIT
"""Lote 12 del catálogo: dimension, un chorus espacial sin vibrato audible.

Las pruebas miden lo que lo distingue del chorus: los dos canales se separan,
pero en la suma L + R la desviación de tono casi desaparece. Con el cruce al
máximo, la suma es solo el seco. El nivel queda acotado.
"""

from __future__ import annotations

import math

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, frecuencias, pots, programa, rms, tono


def _correlacion(a: tuple[int, ...], b: tuple[int, ...]) -> float:
    num = sum(x * y for x, y in zip(a, b, strict=True))
    return num / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))


def _desvio(v: tuple[int, ...]) -> float:
    f = frecuencias(v, 0.2, 1.6, 0.1)
    return max(f) - min(f)


def test_dimension_ensancha_y_la_suma_no_ondula() -> None:
    """Modo 4 a 1,6 Hz (dos periodos): L y R se separan; L + R casi no cambia de tono."""
    x = Senal(FS, (tono(440, 1.6, 0.3),))
    izq, der = procesar(programa("dimension"), x, Controles(pots("0.9", "1", "0.5", "1"))).canales
    suma = tuple((a + b) >> 1 for a, b in zip(izq, der, strict=True))
    lado = tuple((a - b) >> 1 for a, b in zip(izq, der, strict=True))
    tramo = slice(int(0.2 * FS), int(1.6 * FS))
    assert rms(lado, 0.2, 1.6) > 0.3 * rms(izq, 0.2, 1.6)  # medido: 0,49
    assert _correlacion(izq[tramo], der[tramo]) < 0.8  # medido: 0,56 (la entrada: 1)
    assert _desvio(suma) < 0.5 * _desvio(izq)  # medido: 1,75 Hz frente a 4,3 Hz


def test_dimension_con_cruce_maximo_la_suma_es_el_seco() -> None:
    """Con k = 1, A − B y B − A se anulan en L + R: compatible con mono."""
    x = Senal(FS, (tono(440, 0.5, 0.3),))
    c = Controles(pots("0.9", "1", "0.5", "1", "1", "1"))
    izq, der = procesar(programa("dimension"), x, c).canales
    suma = tuple((a + b) >> 1 for a, b in zip(izq, der, strict=True))
    lado = tuple((a - b) >> 1 for a, b in zip(izq, der, strict=True))
    seco = tuple(s >> 1 for s in x.canales[0])  # kdry ≈ 0,5 con pot2 = 0,5
    resto = tuple(a - b for a, b in zip(suma, seco, strict=True))
    assert rms(resto, 0.1, 0.5) < 0.01 * rms(suma, 0.1, 0.5)  # medido: 0,002
    assert rms(lado, 0.1, 0.5) > 0.3 * rms(suma, 0.1, 0.5)  # medido: 1,05


def test_dimension_nivel_acotado() -> None:
    plate = programa("plate")
    dim = programa("dimension")
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        ref = rms(procesar(plate, x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1.0)
        c = Controles(pots("0.4", "0.5", "0.5", "0.5", "0.5", "0.5"))
        for canal in procesar(dim, x, c).canales:
            nivel = rms(canal, 0, 1.0)
            assert 0.2 * ref < nivel < 2 * ref  # medido: de 0,27 a 0,41 del plate
