# SPDX-License-Identifier: MIT
"""Lote 12 del catálogo: orilla, chorus aleatorio con una puerta de paso bajo (LPG).

Las pruebas miden lo que distingue a orilla de chorus y de autowah:
- la LPG oscurece la nota mientras decae, mucho más de lo que se oscurece la entrada;
- la modulación de tono es aleatoria, no periódica, y el suavizado la hace más lenta;
- el nivel queda acotado frente al plate.
"""

from __future__ import annotations

import math
from itertools import pairwise

from sofifi.domain.aritmetica import dato
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, frecuencias, potencia, pots, programa, rms, tono


def _nota(segundos: float) -> tuple[int, ...]:
    """Nota de 220 Hz con un armónico de 1 760 Hz, que decae con τ = 0,3 s."""
    w1, w2 = 2 * math.pi * 220 / FS, 2 * math.pi * 1760 / FS
    return tuple(
        dato(
            str(
                round(
                    0.5
                    * math.exp(-k / FS / 0.3)
                    * (0.7 * math.sin(w1 * k) + 0.3 * math.sin(w2 * k)),
                    6,
                )
            )
        )
        for k in range(int(segundos * FS))
    )


def test_orilla_la_lpg_oscurece_la_nota_al_decaer() -> None:
    """Brillo (1 760 Hz frente a 220 Hz) al principio de la nota y 0,75 s después."""
    x = Senal(FS, (_nota(0.9),))

    def caida(v: tuple[int, ...]) -> float:
        def brillo(a: float) -> float:
            return potencia(v, 1760, a, a + 0.1) / potencia(v, 220, a, a + 0.1)

        return brillo(0.05) / brillo(0.8)

    def salida(puerta: str) -> tuple[int, ...]:
        # Mezcla 0: solo seco, sin el desplazamiento Doppler del chorus.
        c = Controles(pots("0.5", "0.3", "0", "0.5", puerta, "0.5"))
        return procesar(programa("orilla"), x, c).canales[0]

    assert 0.9 < caida(x.canales[0]) < 1.1  # la entrada no se oscurece
    assert 0.9 < caida(salida("0")) < 1.1  # medido: 1,00, la LPG abierta no filtra
    abierta, cerrada = salida("0"), salida("1")
    assert caida(cerrada) > 30  # medido: ×104
    # El VCA también cierra: la cola baja mucho más que con la LPG abierta.
    assert rms(cerrada, 0.8, 0.9) < 0.5 * rms(abierta, 0.8, 0.9)  # medido: ×0,29


def _desvio(suavizado: str) -> list[float]:
    """Desvío de tono (Hz) por ventanas de 20 ms de un tono de 1 kHz, solo la voz modulada."""
    x = Senal(FS, (tono(1000, 1.8, 0.3),))
    c = Controles(pots("0.5", "1", "1", suavizado, "0", "0"))
    y = procesar(programa("orilla"), x, c).canales[0]
    return [f - 1000 for f in frecuencias(y, 0.2, 1.8, 0.02)]


def test_orilla_modulacion_aleatoria_y_suavizado_lento() -> None:
    nervioso, ondulante = _desvio("0"), _desvio("1")

    def paso_medio(d: list[float]) -> float:
        return sum(abs(b - a) for a, b in pairwise(d)) / (len(d) - 1)

    # Cada salto del azar da una cresta de desvío. Un LFO periódico daría
    # crestas iguales; aquí la mayor es muchas veces la menor.
    a = [abs(v) for v in nervioso]
    crestas = [
        a[k] for k in range(1, len(a) - 1) if a[k] > 5 and a[k] > a[k - 1] and a[k] >= a[k + 1]
    ]
    assert len(crestas) >= 5  # medido: 7 crestas en 1,6 s
    assert max(crestas) > 3 * min(crestas)  # medido: 64 y 6,7 Hz
    assert max(crestas) > 30  # medido: 64 Hz, unos 110 cents
    # Con el suavizado al máximo, el tono cambia mucho más despacio.
    assert paso_medio(ondulante) < 0.2 * paso_medio(nervioso)  # medido: ×0,085


def test_orilla_nivel() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        c = Controles(pots("0.5", "0.5", "0.5", "0.3", "0.5", "0.5"))
        nivel = rms(procesar(programa("orilla"), x, c).canales[0], 0, 1)
        assert 0.2 * plate < nivel < 2 * plate  # medido: ×0,63 y ×0,74
