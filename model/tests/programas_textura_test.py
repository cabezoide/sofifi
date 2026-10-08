# SPDX-License-Identifier: MIT
"""Textura y color: ring modulator, slicer, ancho, chorale, resonador y granular.

Cada prueba mide dónde sale la energía (frecuencias nuevas, formantes, notas
de los resonadores), cuánto tiempo pasa abierta la puerta del slicer o cuánto
se parecen los dos canales.
"""

from __future__ import annotations

import math
import random
from itertools import pairwise

from sofifi.domain.aritmetica import dato
from sofifi.domain.nucleo import Nucleo
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, frecuencias, impulso, potencia, pots, programa, rms, tono


def ruido(segundos: float, semilla: int = 5) -> tuple[int, ...]:
    azar = random.Random(semilla)
    return tuple(azar.randrange(-(1 << 21), 1 << 21) for _ in range(int(segundos * FS)))


def test_ringmod_da_la_suma_y_la_diferencia() -> None:
    """440 Hz por una portadora de 1 kHz: salen 560 y 1 440 Hz; no 440 ni 1 000."""
    x = Senal(FS, (tono(440, 1.0, 0.4),))
    y = procesar(programa("ringmod"), x, Controles(pots("0.48718", "0", "1"))).canales[0]
    nuevas = min(potencia(y, f, 0.2, 1.0) for f in (560, 1440))
    viejas = max(potencia(y, f, 0.2, 1.0) for f in (440, 1000))
    assert nuevas > 1000 * viejas
    assert abs(rms(y, 0.8, 1.0) / rms(y, 0.2, 0.4) - 1) < 0.02  # el oscilador no deriva


def test_slicer_abre_el_tiempo_que_dice_el_ciclo() -> None:
    x = Senal(FS, (tuple(dato("0.5") for _ in range(FS)),))
    for ciclo, esperado in (("0", 0.1), ("0.5", 0.5), ("1", 0.9)):
        c = Controles(pots("0.2", "1", ciclo, "0"))
        y = procesar(programa("slicer"), x, c).canales[0][2000:]
        abierta = [v > dato("0.25") for v in y]
        assert abs(sum(abierta) / len(abierta) - esperado) < 0.03
        assert sum(1 for a, b in pairwise(abierta) if a != b) in (7, 8)  # 4 pulsos/s


def test_ancho_separa_los_canales_y_el_tilt_inclina() -> None:
    x = Senal(FS, (ruido(0.5),))

    def correlacion(ancho: str) -> float:
        izq, der = procesar(programa("ancho"), x, Controles(pots(ancho, "0.5"))).canales
        return sum(a * b for a, b in zip(izq, der, strict=True)) / math.sqrt(
            sum(a * a for a in izq) * sum(b * b for b in der)
        )

    assert correlacion("0") > 0.999 and correlacion("1") < 0.5  # medido: 0,35

    def ganancia(tilt: str, f: float) -> float:
        y = procesar(programa("ancho"), Senal(FS, (tono(f, 0.3, 0.3),)), Controles(pots("0", tilt)))
        return rms(y.canales[0], 0.1, 0.3) / (0.3 / math.sqrt(2))

    assert ganancia("0", 150) > 1.5 > 0.5 > ganancia("0", 5000)  # oscuro
    assert ganancia("1", 5000) > 1.5 > 0.5 > ganancia("1", 150)  # brillante
    assert abs(ganancia("0.5", 150) - 1) < 0.05 and abs(ganancia("0.5", 5000) - 1) < 0.05


def test_chorale_mueve_los_formantes_de_la_a_a_la_i() -> None:
    """El segundo formante: 1 090 Hz en la «a», 2 290 Hz en la «i»."""

    def bandas(vocal: str) -> tuple[float, float]:
        c = Controles(pots("0.6", "0.2", "1", vocal))
        y = procesar(programa("chorale"), Senal(FS, (ruido(0.6),)), c).canales[0]

        def banda(f: float) -> float:
            return sum(potencia(y, f + d, 0.2, 0.6) for d in (-60, -30, 0, 30, 60))

        return banda(1090), banda(2290)

    a1, a2 = bandas("0")
    i1, i2 = bandas("1")
    assert a1 > 3 * a2 and i2 > 3 * i1


def test_resonador_suena_en_sus_cuatro_notas() -> None:
    def notas(afinacion: str, frecuencias: tuple[float, ...]) -> bool:
        c = Controles(pots("1", "1", "1", afinacion))
        y = procesar(programa("resonador"), impulso(1.0), c).canales[0]
        minimo = min(potencia(y, f, 0.2, 1.0) for f in frecuencias)
        return minimo > 50 * max(potencia(y, f, 0.2, 1.0) for f in (100, 145, 190))

    assert notas("0", (82.41, 123.47, 164.81, 207.65))  # mi mayor
    assert notas("1", (41.2, 61.7, 82.4, 103.8))  # una octava abajo


def test_granular_ganancia_constante_y_generador_exacto() -> None:
    """Las ventanas de cada pareja suman 1: una entrada constante sale constante."""
    n = Nucleo(programa("granular"))
    xs = []
    for _ in range(500):
        n.procesar(0, 0, (0,) * 6, 0)
        xs.append(n.regs[3])
    c = n.regs[2]
    assert c & 1 and all(b == (5 * a + c) % (1 << 23) for a, b in pairwise(xs))
    dc = Senal(FS, (tuple(dato("0.4") for _ in range(FS)),))
    y = procesar(programa("granular"), dc, Controles(pots("0.3", "0.5", "0.5", "1"))).canales[0]
    assert max(y[FS // 2 :]) - min(y[FS // 2 :]) == 0 and abs(y[-1] - dato("0.4")) < 1 << 14


def test_granular_pitch_en_octavas() -> None:
    x = Senal(FS, (tono(440, 1.5, 0.5),))
    for intervalo, f in (("0", 220), ("0.5", 440), ("1", 880)):
        c = Controles(pots("0.5", "0.3", intervalo, "1"))
        medidas = frecuencias(procesar(programa("granular"), x, c).canales[0], 0.6, 1.5)
        assert all(abs(m / f - 1) < 0.1 for m in medidas), (intervalo, medidas)
        assert abs(sum(medidas) / len(medidas) / f - 1) < 0.02


def test_granular_granos_dentro_de_la_ventana_declarada() -> None:
    """Con 1×, un impulso vuelve con un retardo entre dmin y dmin + difusión."""
    t0, u = 2000, 1 / 32768
    x = Senal(FS, (tuple(dato("0.8") if k == t0 else 0 for k in range(FS)),))
    y = procesar(programa("granular"), x, Controles(pots("0.2", "0.5", "0.5", "1"))).canales[0]
    ecos = [k - t0 for k, v in enumerate(y) if v != 0 and k != t0]  # en t0, el seco (kdry = −0,001)
    dmin, difusion = round(0.004 / u), round(0.125 / u)
    assert len(ecos) >= 4 and dmin - 1 <= min(ecos) and max(ecos) <= dmin + difusion + 1
    assert max(abs(v) for v in y) <= dato("0.4") + 2  # cada eco pasa por una ventana ≤ 1


def test_granular_freeze_congela_el_bufer() -> None:
    """Con sw, la entrada nueva (880 Hz) no entra: siguen sonando los 440 Hz."""
    x = Senal(FS, (tono(440, 0.8, 0.5) + tono(880, 0.8, 0.5),))
    c = Controles(pots("0.5", "0.3", "0.5", "1"), tramos_sw=((int(0.8 * FS), 2 * FS),))
    y = procesar(programa("granular"), x, c).canales[0]
    medidas = frecuencias(y, 1.1, 1.6)
    assert abs(sum(medidas) / len(medidas) / 440 - 1) < 0.02
