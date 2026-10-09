# SPDX-License-Identifier: MIT
"""Lote 11 del catálogo: aureo, ecos en la serie de Fibonacci.

Las pruebas miden lo que distingue al programa: los ecos caen en F_k·u y
alternan de canal, la tabla corta cambia u, la realimentación multiplica los
ecos con el tiempo y el nivel queda acotado con la realimentación al máximo.
"""

from __future__ import annotations

from sofifi.domain.aritmetica import UNO
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, impulso, pots, programa, rms, tono

FIBONACCI = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89)


def test_aureo_ecos_en_fibonacci_y_alternados() -> None:
    """Sin difusión ni realimentación: cada eco cae en F_k·u, por el lado que le toca."""
    base = int(0.1 * FS)
    x = impulso(0.25, base)
    mandos = pots("0.5", "0", "1", "1", "1", "0")
    for u, tramos in ((67, ()), (29, ((0, len(x.canales[0])),))):
        izq, der = procesar(programa("aureo"), x, Controles(mandos, tramos_sw=tramos)).canales
        for k, f in enumerate(FIBONACCI):
            n = base + f * u
            suena, calla = (izq, der) if k % 2 == 0 else (der, izq)
            # medido: 0,25 en la primera toma y 0,13 en la décima; el otro lado, < 1e-6
            assert abs(suena[n]) > 0.1 * UNO, (u, f)
            assert abs(calla[n]) < 0.001 * UNO, (u, f)
            assert max(abs(v) for v in suena[n - 8 : n + 9]) == abs(suena[n])


def test_aureo_los_ecos_se_espesan() -> None:
    """Con realimentación, cada vuelta suma tiempos de Fibonacci: hay más ecos al final."""
    c = Controles(pots("0.5", "0.9", "1", "1", "1", "0"))
    izq = procesar(programa("aureo"), impulso(2.0), c).canales[0]

    def ecos(a: float) -> int:
        seg = [abs(v) for v in izq[int(a * FS) : int((a + 0.5) * FS)]]
        return sum(1 for v in seg if v > 0.1 * max(seg))

    assert ecos(1.5) > 3 * ecos(0)  # medido: 45 frente a 11


def test_aureo_nivel_comparable_al_plate() -> None:
    """Con la realimentación al máximo, el nivel queda cerca del plate y sin picos."""
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        izq = procesar(
            programa("aureo"), x, Controles(pots("0.5", "1", "1", "1", "1", "0.5"))
        ).canales[0]
        assert 0.2 * plate < rms(izq, 0, 1) < 2 * plate  # medido: ×0,40 (0,1) y ×0,46 (0,5)
        assert max(abs(v) for v in izq) < 0.98 * UNO
