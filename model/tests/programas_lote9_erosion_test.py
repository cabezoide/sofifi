# SPDX-License-Identifier: MIT
"""Erosión: un bucle que pierde agudos y nivel en cada vuelta.

Se graba un ruido de 0,1 s con el footswitch pisado. Con pot5 = 0 el bucle
tiene 8 192 muestras y la lectura va una muestra por delante: cada vuelta dura
8 191 muestras. La salida es solo el bucle (pot2 = 1).
"""

from __future__ import annotations

import math
import random
from itertools import pairwise

from sofifi.domain.aritmetica import UNO
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, pots, programa, rms, tono

VUELTA = 8191
GRABA = 4883  # 0,1 s


def ruido(n: int, semilla: int = 3) -> tuple[int, ...]:
    azar = random.Random(semilla)
    return tuple(azar.randrange(-(1 << 21), 1 << 21) for _ in range(n))


def vueltas(erosion: str, n: int) -> list[tuple[float, float]]:
    """(RMS, agudos/RMS) de las vueltas 1 a n. Agudos: RMS de la primera diferencia."""
    x = ruido(GRABA) + (0,) * (VUELTA * n)
    c = Controles(pots(erosion, "0.5", "1", "0.5", "1", "0"), tramos_sw=((0, GRABA),))
    y = procesar(programa("erosion"), Senal(FS, (x,)), c).canales[0]
    res = []
    for k in range(1, n + 1):
        seg = y[k * VUELTA + 200 : k * VUELTA + 4600]
        r = math.sqrt(sum((s / UNO) ** 2 for s in seg) / len(seg))
        d = math.sqrt(sum(((a - b) / UNO) ** 2 for a, b in zip(seg[1:], seg, strict=False)))
        res.append((r, d / math.sqrt(len(seg)) / r))
    return res


def test_erosion_cero_mantiene_el_bucle() -> None:
    v = vueltas("0", 2)
    assert v[0] == v[1]  # medido: idénticas (RMS 0,140, agudos 1,42)


def test_cada_vuelta_pierde_agudos_y_mas_erosion_pierde_mas_nivel() -> None:
    suave, fuerte = vueltas("0.3", 3), vueltas("0.7", 3)
    for v in (suave, fuerte):
        agudos = [a for _, a in v]
        assert all(b < 0.9 * a for a, b in pairwise(agudos))
    # medido, agudos/RMS: 1,27 → 1,01 → 0,84 y 1,21 → 0,87 → 0,66
    caida_suave = suave[2][0] / suave[0][0]
    caida_fuerte = fuerte[2][0] / fuerte[0][0]
    assert caida_fuerte < 0.8 * caida_suave  # medido: 0,39 y 0,58


def test_nivel_cercano_al_plate() -> None:
    """Se graba un tono de 0,4 s y se deja sonar el bucle 0,6 s más."""
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        c = Controles(pots("0.3", "0.4", "0.5", "0.5", "1", "0.5"), tramos_sw=((0, int(0.4 * FS)),))
        y = procesar(programa("erosion"), x, c).canales[0]
        plate = procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0]
        relacion = rms(y, 0, 1.0) / rms(plate, 0, 1.0)
        assert 0.2 < relacion < 2  # medido: 0,65 y 0,75
