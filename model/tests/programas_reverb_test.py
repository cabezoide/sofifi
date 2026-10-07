# SPDX-License-Identifier: MIT
"""Reverbs de la Fase 06, lote 3: blackhole, infinite, bloom, spring, gated y reverb inversa.

Cada prueba mide lo que distingue al programa de un plate: un decay mucho más
largo, una capa que no se apaga, una cola que crece tarde, la dispersión del
muelle, o una cola que se corta de golpe.
"""

from __future__ import annotations

import math

from sofifi.domain.aritmetica import dato
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, impulso, pots, programa, rms, tono


def t60(v: tuple[int, ...]) -> float:
    """T60 en segundos, por la caída entre 0,3-0,5 s y 1,1-1,3 s."""
    return 60 * 0.8 / (20 * math.log10(rms(v, 0.3, 0.5) / rms(v, 1.1, 1.3)))


def nota(segundos: float, inicio: float, caida: float) -> Senal:
    """Nota pulsada de 196 Hz que empieza en `inicio` y cae con la constante `caida`."""
    x = [0] * int(segundos * FS)
    k0 = int(inicio * FS)
    for i in range(len(x) - k0):
        v = 0.4 * math.exp(-i / FS / caida) * math.sin(2 * math.pi * 196 * i / FS)
        x[k0 + i] = dato(str(round(v, 6)))
    return Senal(FS, (tuple(x),))


def test_blackhole_decae_mucho_mas_que_el_hall() -> None:
    c = Controles(pots("1", "0", "1"))
    hall = procesar(programa("hall"), impulso(1.3), c).canales[0]
    agujero = procesar(programa("blackhole"), impulso(1.3), c).canales[0]
    assert t60(agujero) > 20 and t60(agujero) > 3 * t60(hall)  # medido: 49 s y 9,2 s


def test_infinite_sostiene_con_pot0_a_cero_y_se_vacia_con_pot0_a_uno() -> None:
    x = Senal(FS, (tono(330, 0.3, 0.4) + (0,) * int(2.7 * FS),))
    lleno = procesar(programa("infinite"), x, Controles(pots("0", "0.3", "1"))).canales[0]
    vacio = procesar(programa("infinite"), x, Controles(pots("1", "0.3", "1"))).canales[0]
    assert rms(lleno, 2.0, 3.0) > 0.8 * rms(lleno, 0.4, 1.0)  # medido: 0,91
    assert rms(vacio, 2.0, 3.0) < 0.5 * rms(vacio, 0.4, 1.0)  # medido: 0,32


def test_bloom_empieza_en_silencio_y_crece() -> None:
    x = nota(1.0, 0.2, 0.3)
    c = Controles(pots("0.8", "0.3", "1", "0.3"))
    plate = procesar(programa("plate"), x, c).canales[0]
    bloom = procesar(programa("bloom"), x, c).canales[0]
    assert rms(bloom, 0.2, 0.3) < 0.2 * rms(plate, 0.2, 0.3)
    assert rms(bloom, 0.5, 0.6) > 3 * rms(bloom, 0.2, 0.3)


def test_spring_los_agudos_llegan_antes_que_los_graves() -> None:
    """Ráfagas de 4 ms: el centro de energía de 3 kHz llega ~160 muestras antes que el de 300 Hz."""

    def llegada(f: float) -> float:
        x = [0] * int(0.1 * FS)
        n = int(0.004 * FS)
        for k in range(n):
            v = 0.4 * math.sin(2 * math.pi * f * k / FS) * math.sin(math.pi * k / n)
            x[1000 + k] = dato(str(round(v, 6)))
        c = Controles(pots("0", "0", "1"))
        y = procesar(programa("spring"), Senal(FS, (tuple(x),)), c).canales[0]
        e = [v * v for v in y[1000:2600]]
        return sum(i * w for i, w in enumerate(e)) / sum(e)

    assert llegada(300) - llegada(3000) > 100  # medido: 383 y 225


def test_gated_y_reverb_inversa_cortan_la_cola() -> None:
    """pot3 = 0,4: duración de 0,118 s. Después del corte, el plate suena y estas dos no."""
    x = nota(1.0, 0.2, 0.08)
    c = Controles(pots("0.8", "0.3", "1", "0.4"))
    plate = procesar(programa("plate"), x, c).canales[0]
    gated = procesar(programa("gated"), x, c).canales[0]
    inversa = procesar(programa("reverb_inversa"), x, c).canales[0]
    assert rms(gated, 0.5, 0.9) < 0.01 * rms(plate, 0.5, 0.9)
    assert rms(inversa, 0.5, 0.9) < 0.01 * rms(plate, 0.5, 0.9)
    # La inversa crece hasta el corte; la gated empieza ya abierta.
    assert rms(inversa, 0.205, 0.235) < 0.6 * rms(inversa, 0.27, 0.30)
    assert rms(gated, 0.22, 0.27) > 0.8 * rms(plate, 0.22, 0.27)
