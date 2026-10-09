# SPDX-License-Identifier: MIT
"""Lote 9 del catálogo: armonico, el trémolo armónico.

El trémolo normal mueve todo el volumen. Este mueve los graves contra los
agudos. Las pruebas miden la contrafase de las dos bandas, su velocidad y el
nivel de la salida.
"""

from __future__ import annotations

import math
from functools import cache

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, potencia, pots, programa, rms, tono

VENTANA = 0.0125


def _correlacion(a: list[float], b: list[float]) -> float:
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    cov = sum((p - ma) * (q - mb) for p, q in zip(a, b, strict=True))
    return cov / math.sqrt(sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b))


def test_armonico_graves_y_agudos_laten_en_contrafase_a_4_hz() -> None:
    """Un tono de 130 Hz y otro de 2 kHz: sus envolventes laten a 4 Hz y al revés."""
    grave, agudo = tono(130, 0.6, 0.3), tono(2000, 0.6, 0.3)
    x = Senal(FS, (tuple(p + q for p, q in zip(grave, agudo, strict=True)),))
    # pot0 = 0,7 → 0,2 + 7,8·0,7² = 4,0 Hz; profundidad 1; cruce a unos 580 Hz.
    y = procesar(programa("armonico"), x, Controles(pots("0.7", "1", "0", "0.5"))).canales[0]
    tramos = [0.05 + k * VENTANA for k in range(40)]  # 0,5 s: dos periodos
    eg = [potencia(y, 130, t, t + VENTANA) ** 0.5 for t in tramos]
    ea = [potencia(y, 2000, t, t + VENTANA) ** 0.5 for t in tramos]
    assert _correlacion(eg, ea) < -0.8  # medido: −0,98
    # A 4 Hz, la envolvente se repite cada 0,25 s (20 ventanas) y va al revés a 0,125 s.
    assert _correlacion(eg[:20], eg[20:]) > 0.9  # medido: 1,00
    assert _correlacion(eg[:30], eg[10:]) < -0.8  # medido: −0,99
    assert max(eg) > 10 * min(eg)  # medido: ×149; cada banda llega casi al silencio
    # El nivel medio cambia poco: la ganancia 1 + prof/2 compensa.
    assert 0.6 < rms(y, 0.05, 0.55) / rms(x.canales[0], 0.05, 0.55) < 1.3  # medido: 0,81


@cache
def _plate(amplitud: float) -> float:
    x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
    return rms(procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1)


def test_armonico_nivel_razonable_frente_al_plate() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        c = Controles(pots("0.5", "0.7", "0.4", "0.5", "0.3", "0.5"))
        nivel = rms(procesar(programa("armonico"), x, c).canales[0], 0, 1)
        assert 0.2 * _plate(amplitud) < nivel < 2 * _plate(amplitud)  # medido: ×0,65 y ×0,77
