# SPDX-License-Identifier: MIT
"""Delays del catálogo: delay, ping-pong, lluvia, BBD y ducking.

Cada prueba mide cuándo y dónde llegan los ecos, o cómo suenan: el tiempo que
dice pot0, el lado que alterna, los seis taps, los agudos que pierde el BBD o
los ecos que se apartan mientras se toca.
"""

from __future__ import annotations

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, impulso, maximos, pots, programa, rms, tono

ENTRADA = int(0.6 * FS)


def ecos(v: tuple[int, ...], umbral: float, signo: int = 1, desde: int = 0) -> list[float]:
    return [round((k - desde) / FS, 3) for k in maximos(v, umbral, signo)]


def test_delay_el_eco_llega_cuando_dice_pot0() -> None:
    for tiempo, esperado in (("0", 0.020), ("1", 0.691)):
        c = Controles(pots(tiempo, "0", "1", "1"))
        y = procesar(programa("delay"), impulso(1.5, ENTRADA), c).canales[0]
        assert ecos(y, 0.05, desde=ENTRADA) == [esperado]


def test_pingpong_alterna_los_lados() -> None:
    c = Controles(pots("1", "0.5", "1"))
    izq, der = procesar(programa("pingpong"), impulso(1.9, ENTRADA), c).canales
    assert ecos(izq, 0.02, desde=ENTRADA) == [0.418, 1.255]
    assert ecos(der, 0.02, desde=ENTRADA) == [0.836]


def test_lluvia_reparte_seis_taps_entre_los_lados() -> None:
    izq, der = procesar(programa("lluvia"), impulso(0.7), Controles(pots("0", "0", "1"))).canales
    assert ecos(izq, 0.05) == [0.09, 0.47] and ecos(izq, 0.05, -1) == [0.25]
    assert ecos(der, 0.05) == [0.16, 0.6] and ecos(der, 0.05, -1) == [0.36]


def test_bbd_es_mas_oscuro_que_el_delay() -> None:
    x = Senal(FS, (tono(4000, 0.05, 0.4) + (0,) * int(0.6 * FS),))
    limpio = procesar(programa("delay"), x, Controles(pots("0.1", "0", "1", "1"))).canales[0]
    bbd = procesar(programa("bbd"), x, Controles(pots("0.3", "0", "1", "0"))).canales[0]
    assert rms(bbd, 0.06, 0.45) < 0.5 * rms(limpio, 0.06, 0.45)  # medido: 0,027 y 0,088


def test_ducking_aparta_los_ecos_mientras_se_toca() -> None:
    x = Senal(FS, (tono(330, 1.0, 0.4) + (0,) * int(1.0 * FS),))
    libre = procesar(programa("ducking"), x, Controles(pots("0.2", "0.5", "1", "0"))).canales[0]
    aparte = procesar(programa("ducking"), x, Controles(pots("0.2", "0.5", "1", "1"))).canales[0]
    assert rms(aparte, 0.5, 0.9) < 0.2 * rms(libre, 0.5, 0.9)  # tocando: −20 dB
    assert rms(aparte, 1.4, 1.8) > 0.8 * rms(libre, 1.4, 1.8)  # al callar, vuelven
