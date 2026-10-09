# SPDX-License-Identifier: MIT
"""Lote 10 del catálogo: arco, sustain de tipo eBow.

Las pruebas miden lo que distingue a arco del compresor: el AGC mantiene una
nota que decae a nivel fijo, el modo armónico la lleva a su octava con el
tiempo y la puerta no sube el ruido (salvo con el footswitch pisado).
"""

from __future__ import annotations

import math

from sofifi.domain.aritmetica import dato
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, potencia, pots, programa, rms, tono


def _nota(segundos: float, tau: float) -> tuple[int, ...]:
    """Tono de 196 Hz con amplitud 0,4 y decaimiento exponencial de constante tau."""
    w = 2 * math.pi * 196 / FS
    return tuple(
        dato(str(round(0.4 * math.exp(-k / FS / tau) * math.sin(w * k), 6)))
        for k in range(int(segundos * FS))
    )


def test_arco_sostiene_una_nota_que_decae() -> None:
    x = _nota(2.5, 0.8)
    y = procesar(programa("arco"), Senal(FS, (x,)), Controles(pots("0.8", "0.3", "1"))).canales[0]
    entrada = rms(x, 2.0, 2.5) / rms(x, 0.5, 1.0)
    salida = rms(y, 2.0, 2.5) / rms(y, 0.5, 1.0)
    assert entrada < 0.2 and salida > 0.9  # medido: 0,15 y 1,00
    assert 0.08 < rms(y, 1.0, 2.5) < 0.2  # medido: 0,125 (pico ≈ objetivo 0,2)


def test_arco_modo_armonico_pasa_a_la_octava() -> None:
    x = Senal(FS, (_nota(2.2, 0.8),))
    y = procesar(programa("arco"), x, Controles(pots("0.8", "0.3", "1", "1"))).canales[0]

    def octava(a: float) -> float:
        return potencia(y, 392, a, a + 0.3) / potencia(y, 196, a, a + 0.3)

    assert octava(0.2) < 0.1 and octava(1.8) > 5  # medido: 0,013 y ~20


def test_arco_puerta_y_nivel() -> None:
    """Ruido bajo: la puerta lo deja en silencio; con el footswitch, el AGC lo sube."""
    ruido = tuple(dato(str(round(0.001 * math.sin(k * k * 0.37), 6))) for k in range(FS // 2))

    def nivel_ruido(sw: bool) -> float:
        c = Controles(pots("1", "0.3", "1"), tramos_sw=((0, len(ruido)),) if sw else ())
        return rms(procesar(programa("arco"), Senal(FS, (ruido,)), c).canales[0], 0.25, 0.5)

    entrada = rms(ruido, 0.25, 0.5)  # 7e-4
    assert nivel_ruido(False) < 0.1 * entrada  # medido: 7e-7
    assert nivel_ruido(True) > 10 * entrada  # medido: 1,8e-2 (×25)
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        c = Controles(pots("0.7", "0.4", "0.7", "0.5", "0.3", "0.3"))
        nivel = rms(procesar(programa("arco"), x, c).canales[0], 0, 1)
        assert 0.2 * plate < nivel < 2 * plate  # medido: ×1,06 y ×0,41
