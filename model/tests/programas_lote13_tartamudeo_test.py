# SPDX-License-Identifier: MIT
"""Lote 13 del catálogo: tartamudeo, repeticiones disparadas por el ataque.

Las pruebas miden lo que distingue al programa de slicer y sostenido: tras un
ataque, la salida repite el mismo trozo con periodo igual a su duración, y
cada repetición es más baja que la anterior. Sin ataques por encima del
umbral no hay repeticiones. El nivel queda acotado.
"""

from __future__ import annotations

import math
from itertools import pairwise

from sofifi.domain.aritmetica import UNO
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, pots, programa, rms, tono

ANTES = 0.1  # silencio antes de la nota (s)


def _pulsacion(amplitud: float, segundos: float) -> Senal:
    """Una nota de 330 Hz que se apaga en ~50 ms, después de ANTES de silencio."""
    w = 2 * math.pi * 330 / FS
    nota = tuple(
        int(amplitud * math.exp(-k / (0.05 * FS)) * math.sin(w * k) * UNO)
        for k in range(int(segundos * FS))
    )
    return Senal(FS, ((0,) * int(ANTES * FS) + nota,))


def _largo(pot1: float) -> int:
    """Duración del trozo en muestras: 1 465 a 9 766 (30 a 200 ms)."""
    return round((0.0447 + 0.2533 * pot1) * 32768)


def test_tartamudeo_repite_el_trozo_cada_vez_mas_bajo() -> None:
    """Con pot1 = 0,3 y 0,6: la primera repetición llega a L, y cada una es la anterior × 0,645."""
    for pot1 in ("0.3", "0.6"):
        n = _largo(float(pot1))
        x = _pulsacion(0.5, 5 * n / FS)
        c = Controles(pots("0.3", pot1, "1", "0.5", "0", "0"))
        y = procesar(programa("tartamudeo"), x, c).canales[0]
        i0 = int(ANTES * FS)
        inicio = next(k for k in range(i0, len(y)) if abs(y[k]) > 0.02 * UNO)
        # La pasada muda dura un trozo. Detector y ventana añaden unas 260 muestras.
        assert n < inicio - i0 < n + 400  # medido: 3 955 + 257 y 6 445 + 257 muestras
        reps = [y[inicio - 50 + j * n : inicio - 50 + (j + 1) * n] for j in range(3)]
        energia = [sum(v * v for v in r) for r in reps]
        # Mismo trozo: la segunda repetición es la primera escalada.
        cruz = sum(a * b for a, b in zip(reps[0], reps[1], strict=True))
        assert cruz / math.sqrt(energia[0] * energia[1]) > 0.98  # medido: 0,99999 en los dos
        for a, b in pairwise(energia):
            assert 0.55 < math.sqrt(b / a) < 0.75  # medido: 0,645 en las cuatro


def test_tartamudeo_sin_ataque_no_repite() -> None:
    """Una nota suave dispara con pot0 = 0, pero no con pot0 = 1."""
    x = _pulsacion(0.05, 0.6)

    def cola(umbral: str) -> float:
        c = Controles(pots(umbral, "0.3", "1", "0.5", "0", "0"))
        return rms(procesar(programa("tartamudeo"), x, c).canales[0], 0.15, 0.7)

    sensible, sordo = cola("0"), cola("1")
    assert sensible > 0.005  # medido: 0,0096
    assert sordo < 0.0005  # medido: 2,8e-6 (solo el seco a −60 dB)


def test_tartamudeo_nivel_comparable_al_plate() -> None:
    """Con repeticiones casi sin fin y el tono abierto, el nivel queda cerca del plate."""
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        izq = procesar(
            programa("tartamudeo"), x, Controles(pots("0", "1", "1", "1", "0.9", "0"))
        ).canales[0]
        assert 0.2 * plate < rms(izq, 0, 1) < 2 * plate  # medido: ×1,15 (0,1) y ×1,34 (0,5)
        assert max(abs(v) for v in izq) < 0.98 * UNO
