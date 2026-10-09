# SPDX-License-Identifier: MIT
"""Lote 11 del catálogo: probabilidad, ocho ecos que suenan o callan por sorteo.

Las pruebas miden lo que distingue al programa: con probabilidad 1 suenan las
ocho tomas y con 0 ninguna; con 0,5 cada nota da otra respuesta y suena la
mitad de la energía; con el footswitch pisado, la respuesta queda fija. Al
final, el nivel.
"""

from __future__ import annotations

import math
from functools import cache
from itertools import pairwise

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, pots, programa, rms, tono

Tramos = tuple[tuple[int, int], ...]

# Razones de las tomas (probabilidad.sasm) y T con pot0 = 0,3: (0,045 + 0,93·0,3)·32 768 muestras.
RAZONES = (0.127, 0.229, 0.311, 0.443, 0.523, 0.683, 0.797, 0.997)
T = (0.045 + 0.93 * 0.3) * 32768 / FS  # 0,217 s
SEPARACION = 0.25  # entre notas: T más la difusión de los allpass
INICIO = 0.5  # las compuertas valen pot1 al arrancar; tras ~8 sorteos ya son 0 o 1


def _notas(inicios: list[float], segundos: float) -> Senal:
    x = [0] * int(segundos * FS)
    for t in inicios:
        x[int(t * FS)] = 1 << 22  # impulso de 0,5
    return Senal(FS, (tuple(x),))


def _salida(probabilidad: str, x: Senal, tramos_sw: Tramos = ()) -> tuple[int, ...]:
    # Mezcla 1, sin realimentación, tono limpio y compuerta rápida.
    c = Controles(pots("0.3", probabilidad, "1", "0", "1", "0"), tramos_sw=tramos_sw)
    return procesar(programa("probabilidad"), x, c).canales[0]


def _respuestas(y: tuple[int, ...], inicios: list[float]) -> list[tuple[int, ...]]:
    return [y[int(t * FS) : int((t + SEPARACION) * FS)] for t in inicios]


def _energia(v: tuple[int, ...]) -> float:
    return float(sum(s * s for s in v))


def _correlacion(a: tuple[int, ...], b: tuple[int, ...]) -> float:
    return sum(p * q for p, q in zip(a, b, strict=True)) / math.sqrt(_energia(a) * _energia(b))


@cache
def _referencia() -> float:
    """Energía de la respuesta a una nota con probabilidad 1."""
    return _energia(_respuestas(_salida("1", _notas([0.01], 0.3)), [0.01])[0])


def test_con_probabilidad_1_suenan_las_ocho_tomas_y_con_0_ninguna() -> None:
    y = _salida("1", _notas([0.01], 0.3))
    golpes = [rms(y, 0.01 + k * T - 0.001, 0.01 + k * T + 0.004) for k in RAZONES]
    entre = rms(y, 0.01 + 0.05 * T, 0.01 + 0.11 * T)  # antes de la primera toma
    assert entre == 0  # medido: 0, el primer eco aún no ha llegado
    assert min(golpes) > 0.001  # medido: de 0,0015 a 0,0037 (impulso de 0,5)
    # Con probabilidad 0 no suena ninguna toma. Con mezcla 1, kdry vale 2^-23:
    # el seco deja como mucho 1 LSB, y el resto es cero.
    assert max(abs(v) for v in _salida("0", _notas([0.01], 0.3))) <= 1  # medido: 1, en el impulso


def test_con_probabilidad_media_cada_nota_suena_distinta_y_sw_la_congela() -> None:
    inicios = [INICIO + SEPARACION * n for n in range(10)]
    r = _respuestas(_salida("0.5", _notas(inicios, inicios[-1] + SEPARACION)), inicios)
    # En media suena la mitad de la energía de las ocho tomas.
    media = sum(_energia(v) for v in r) / len(r) / _referencia()
    assert 0.35 < media < 0.7  # medido: 0,52
    # Dos notas seguidas e iguales no dan la misma respuesta: el patrón cambia.
    parecido = max(_correlacion(a, b) for a, b in pairwise(r))
    assert parecido < 0.85  # medido: 0,72 como máximo; 0,21 como mínimo
    # Con sw pisado, el patrón queda fijo: tres notas dan la misma respuesta.
    inicios = [INICIO + SEPARACION * n for n in range(3)]
    sw = ((int((INICIO - 0.02) * FS), 10 * FS),)
    r = _respuestas(_salida("0.5", _notas(inicios, inicios[-1] + SEPARACION), sw), inicios)
    assert min(_correlacion(a, b) for a, b in pairwise(r)) > 0.99  # medido: 0,9997


@cache
def _plate(amplitud: float) -> float:
    x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
    return rms(procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1)


def test_probabilidad_nivel_razonable_frente_al_plate() -> None:
    """Probabilidad 1, solo ecos y realimentación alta: el caso más fuerte."""
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        c = Controles(pots("0.1", "1", "1", "0.9", "1", "0"))
        nivel = rms(procesar(programa("probabilidad"), x, c).canales[0], 0, 1)
        assert 0.2 * _plate(amplitud) < nivel < 2 * _plate(amplitud)  # medido: ×1,47 y ×0,90
