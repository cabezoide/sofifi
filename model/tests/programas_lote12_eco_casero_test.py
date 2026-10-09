# SPDX-License-Identifier: MIT
"""Lote 12 del catálogo: eco_casero, el eco de chip de los pedales caseros.

Las pruebas miden lo que distingue al programa de bbd, cinta y lofi: la
degradación depende del tiempo de eco. Con suciedad, el eco largo pierde
agudos y gana ruido de cuantización; sin suciedad, los dos tiempos suenan
igual. El nivel queda acotado con la realimentación al máximo.
"""

from __future__ import annotations

import math

from sofifi.domain.aritmetica import UNO
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, pots, programa, rms, tono

F = FS / 200  # 244 Hz: periodo de 200 muestras exactas, sin fugas en la DFT
PERIODOS = 30
ANTES = 0.4  # silencio inicial: el tiempo de eco se asienta (el deslizamiento para)


def _retardo(pot0: float) -> float:
    return (1462 + 2 * (16384 + 3600) * pot0) / FS


def _eco(pot0: str, suciedad: str, agudo: float) -> tuple[tuple[int, ...], int]:
    """Ráfaga de F (0,2) más 10·F (amplitud `agudo`); devuelve la salida y el inicio del eco."""
    t = _retardo(float(pot0))
    w = 2 * math.pi * F / FS
    rafaga = tuple(
        int((0.2 * math.sin(w * k) + agudo * math.sin(10 * w * k)) * UNO)
        for k in range(int(0.25 * FS))
    )
    x = Senal(FS, ((0,) * int(ANTES * FS) + rafaga + (0,) * int((t + 0.05) * FS),))
    c = Controles(pots(pot0, "0", "1", suciedad, "0", "0"))
    return procesar(programa("eco_casero"), x, c).canales[0], int((ANTES + t + 0.05) * FS)


def _armonicos(y: tuple[int, ...], i0: int) -> tuple[list[float], float]:
    """Potencia media de cada armónico de F y potencia total, en el mismo tramo exacto."""
    seg = [v / UNO for v in y[i0 : i0 + 200 * PERIODOS]]
    n = len(seg)
    total = sum(v * v for v in seg) / n
    res = []
    for k in range(1, 40):
        w = 2 * math.pi * k / 200
        re = sum(v * math.cos(w * j) for j, v in enumerate(seg))
        im = sum(v * math.sin(w * j) for j, v in enumerate(seg))
        res.append(2 * (re * re + im * im) / n**2)
    return res, total


def _agudos(pot0: str, suciedad: str) -> float:
    p, _ = _armonicos(*_eco(pot0, suciedad, 0.2))
    return p[9] / p[0]


def test_eco_casero_el_eco_largo_es_oscuro_y_ruidoso() -> None:
    """Con suciedad: el eco de 0,77 s pierde agudos y gana ruido frente al de 0,11 s."""
    assert _agudos("0.1", "1") > 5 * _agudos("0.9", "1")  # medido: 0,184 y 0,0175

    def ruido(pot0: str) -> float:
        p, total = _armonicos(*_eco(pot0, "1", 0))
        return 1 - sum(p) / total

    assert ruido("0.9") > 10 * ruido("0.1")  # medido: 5,8e-5 y 1,5e-6


def test_eco_casero_sin_suciedad_el_color_no_cambia() -> None:
    corto, largo = _agudos("0.1", "0"), _agudos("0.9", "0")
    assert abs(corto / largo - 1) < 0.05  # medido: 0,2158 y 0,2153


def test_eco_casero_nivel_comparable_al_plate() -> None:
    """Con la realimentación y la suciedad al máximo, el nivel queda cerca del plate."""
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        izq = procesar(
            programa("eco_casero"), x, Controles(pots("0.2", "1", "1", "1", "1", "0.5"))
        ).canales[0]
        assert 0.2 * plate < rms(izq, 0, 1) < 2 * plate  # medido: ×1,49 (0,1) y ×1,51 (0,5)
        assert max(abs(v) for v in izq) < 0.98 * UNO
