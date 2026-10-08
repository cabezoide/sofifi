# SPDX-License-Identifier: MIT
"""Lote 8 del catálogo, ambient: shimmer grave, marea, ensemble, sostenido, shoegaze y bruma.

Cada prueba mide lo que distingue al programa del plate o del eco del que sale:
la octava de abajo, olas en contrafase, una cola más ancha en frecuencia, un
acorde que se congela solo, una cola que se comprime y ecos que se difuminan.
"""

from __future__ import annotations

from sofifi.domain.aritmetica import DATO_MAX
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, impulso, potencia, pots, programa, rms, tono


def test_shimmer_grave_anade_la_octava_inferior() -> None:
    f = 330.0
    x = Senal(FS, (tono(f, 0.25, 0.3) + (0,) * int(0.9 * FS),))

    def octava_baja(cantidad: str) -> float:
        y = procesar(programa("shimmer_grave"), x, Controles(pots("0.6", "0.3", "1", cantidad)))
        return potencia(y.canales[0], f / 2, 0.45, 1.1) / potencia(y.canales[0], f, 0.45, 1.1)

    assert octava_baja("0.8") > 50 * octava_baja("0")  # medido: ×167


def test_marea_las_olas_van_en_contrafase() -> None:
    """La cola izquierda sube cuando la derecha baja: las envolventes van en contrafase."""
    x = Senal(FS, (tono(330, 0.3, 0.4) + (0,) * int(2.7 * FS),))
    izq, der = procesar(programa("marea"), x, Controles(pots("0.95", "0.3", "1", "0.3"))).canales
    tramos = [k / 20 for k in range(8, 58)]
    el = [rms(izq, t, t + 0.05) for t in tramos]
    er = [rms(der, t, t + 0.05) for t in tramos]
    ml, mr = sum(el) / len(el), sum(er) / len(er)
    cov = sum((a - ml) * (b - mr) for a, b in zip(el, er, strict=True))
    norma = (sum((a - ml) ** 2 for a in el) * sum((b - mr) ** 2 for b in er)) ** 0.5
    assert cov / norma < -0.3
    assert max(el) > 4 * min(el)  # la ola llega casi al silencio


def test_ensemble_ensancha_la_cola_en_frecuencia() -> None:
    """Con un tono fijo, el coro saca energía de la nota: a 1,5-5 Hz de ella."""
    f = 330.0
    x = Senal(FS, (tono(f, 2.5, 0.3),))
    desvios = [k / 2 for k in range(-10, 11)]

    def fuera(ensemble: str) -> float:
        y = procesar(programa("ensemble"), x, Controles(pots("0.6", "0.3", "1", ensemble)))
        p = {d: potencia(y.canales[0], f + d, 0.5, 2.5) for d in desvios}
        return sum(v for d, v in p.items() if abs(d) >= 1.5) / sum(p.values())

    assert fuera("1") > 0.5 and fuera("1") > 3 * fuera("0")  # medido: 0,84 y 0,16


def test_sostenido_congela_cada_acorde_y_lo_reemplaza() -> None:
    """Sin footswitch: el primer acorde se sostiene; con pot0 = 0, el segundo lo reemplaza."""
    a = tono(196, 0.3, 0.4)
    b = tono(262, 0.3, 0.4)
    x = Senal(FS, ((0,) * int(0.1 * FS) + a + (0,) * int(1.4 * FS) + b + (0,) * int(1.2 * FS),))

    def salida(capas: str) -> tuple[int, ...]:
        c = Controles(pots(capas, "0.3", "1", "0.3"))
        return procesar(programa("sostenido"), x, c).canales[0]

    reemplaza, suma = salida("0"), salida("1")
    plate = procesar(programa("plate"), x, Controles(pots("0.95", "0.3", "1"))).canales[0]
    assert rms(reemplaza, 1.4, 1.7) > 0.7 * rms(reemplaza, 0.6, 0.9)
    assert rms(reemplaza, 1.4, 1.7) > 1.5 * rms(plate, 1.4, 1.7)

    def g_sobre_c(v: tuple[int, ...]) -> float:
        return potencia(v, 196, 2.4, 3.0) / potencia(v, 262, 2.4, 3.0)

    assert g_sobre_c(reemplaza) < 0.05
    assert g_sobre_c(suma) > 0.2


def test_shoegaze_comprime_la_cola() -> None:
    """Con saturación, cuatro veces más entrada da mucho menos que cuatro veces más cola."""

    def razon(saturacion: str) -> float:
        def cola(amplitud: float) -> float:
            x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
            c = Controles(pots("0.7", "0.3", "1", saturacion))
            return rms(procesar(programa("shoegaze"), x, c).canales[0], 0.5, 0.9)

        return cola(0.4) / cola(0.1)

    assert razon("0") > 2.5  # medido: 3,1
    assert razon("1") < 1.6  # medido: 1,3


def test_bruma_elige_cabezas_y_difumina_los_ecos() -> None:
    x = impulso(1.7)

    def salida(difusion: str, realimentacion: str, cabezas: str) -> tuple[tuple[int, ...], ...]:
        c = Controles(pots(difusion, realimentacion, "1", cabezas))
        return procesar(programa("bruma"), x, c).canales

    def eco(v: tuple[int, ...], t: float) -> float:
        return rms(v, t - 0.005, t + 0.005)

    cuarta, todas = salida("0", "0.5", "0"), salida("0", "0.5", "1")
    assert eco(cuarta[0], 0.18) == 0 and eco(cuarta[0], 0.74) > 0
    assert eco(todas[0], 0.18) > 0 and eco(todas[1], 0.37) > 0 and eco(todas[0], 0.37) == 0

    def cresta(v: tuple[int, ...]) -> float:
        tramo = v[int(1.4 * FS) : int(1.6 * FS)]
        return max(abs(s) for s in tramo) / DATO_MAX / rms(v, 1.4, 1.6)

    assert cresta(salida("0", "0.9", "0")[0]) > 2 * cresta(salida("1", "0.9", "0")[0])
