# SPDX-License-Identifier: MIT
"""Programas de modulación: trémolo, chorus, flanger, phaser y vibrato.

Cada prueba mide la propiedad que define al efecto: la ganancia que sube y baja,
el retardo que se mueve, los peines, las muescas que se desplazan o el tono que
oscila. La huella y «cabe en el núcleo» están en programas_test.py.
"""

from __future__ import annotations

from itertools import pairwise

from sofifi.domain.aritmetica import UNO, dato
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, frecuencias, invariante, pots, programa, rms, tono


def test_tremolo_sube_y_baja_la_ganancia_y_hace_autopan() -> None:
    """Con continua a la entrada, la salida es la ganancia."""
    x = tuple(dato("0.5") for _ in range(FS))
    mono = procesar(programa("tremolo"), Senal(FS, (x,)), Controles(pots("0.326", "1", "0")))
    izq = [v / UNO / 0.5 for v in mono.canales[0]]
    assert min(izq) < 0.01 and max(izq) > 0.99  # profundidad 1: del silencio al nivel
    medio = (max(izq) + min(izq)) / 2
    assert sum(1 for a, b in pairwise(izq) if a < medio <= b) == 4  # 4,25 Hz
    diferencia = max(abs(a - b) for a, b in zip(*mono.canales, strict=True))
    assert diferencia < dato("0.001")  # kpan = 0,99997: el mismo trémolo en los dos lados
    pan = procesar(programa("tremolo"), Senal(FS, (x,)), Controles(pots("0.326", "1", "1")))
    suma = [a + b for a, b in zip(pan.canales[0], pan.canales[1], strict=True)]
    assert max(suma) - min(suma) < dato("0.01")  # autopan: lo que baja a un lado sube al otro


def test_chorus_mueve_el_retardo_de_sus_voces() -> None:
    quieto = Controles(pots("0.5", "0", "1"))
    y = procesar(programa("chorus"), Senal(FS, (tuple([dato("0.5")] + [0] * 2000),)), quieto)
    assert [k for k, v in enumerate(y.canales[0]) if abs(v) > dato("0.05")] == [977]  # 20 ms
    assert invariante("chorus", quieto, 4000, 6000)
    assert not invariante("chorus", Controles(pots("0.5", "1", "1")), 4000, 6000)


def test_flanger_hace_un_peine() -> None:
    """Retardo quieto de 122 muestras y mezcla 0,5: muesca a 200 Hz, máximo a 400 Hz."""
    c = Controles(pots("0", "0", "0.5", "0"))
    muesca = procesar(programa("flanger"), Senal(FS, (tono(200.1, 0.3, 0.5),)), c).canales[0]
    pico = procesar(programa("flanger"), Senal(FS, (tono(400.2, 0.3, 0.5),)), c).canales[0]
    assert rms(muesca, 0.1, 0.3) < 0.01 * rms(pico, 0.1, 0.3)  # medido: 0,0004 frente a 0,353


def test_phaser_mueve_sus_muescas() -> None:
    """Un tono de 1 kHz: su nivel cambia con el barrido y no cambia sin él."""

    def niveles(prof: str) -> list[float]:
        c = Controles(pots("0.3", prof, "0.5", "0"))
        y = procesar(programa("phaser"), Senal(FS, (tono(1000, 2.0, 0.5),)), c).canales[0]
        return [rms(y, t / 20, (t + 1) / 20) for t in range(4, 40)]

    quieto, barrido = niveles("0"), niveles("1")
    assert max(quieto) < 1.01 * min(quieto)
    assert max(barrido) > 4 * min(barrido)  # medido: 8,3


def test_vibrato_hace_oscilar_el_tono() -> None:
    """1 kHz a ±1,2 ms y 2 Hz: el tono se mueve un ±1,5 %."""

    def desviacion(prof: str) -> float:
        c = Controles(pots("0", prof, "1"))
        y = procesar(programa("vibrato"), Senal(FS, (tono(1000, 1.0, 0.5),)), c).canales[0]
        f = frecuencias(y, 0.1, 1.0)
        return (max(f) - min(f)) / 1000

    assert desviacion("0") < 0.003
    assert desviacion("1") > 0.015
