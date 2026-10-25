# SPDX-License-Identifier: MIT
"""Palabras de memoria de 12 bit (Fase 14, ADR 0008 actualizado el 2026-10-25).

Un programa pide `palabra 12` y tiene 1,5 veces más tiempo de retardo. Sin la
directiva, 18 bit: lo que hay hoy. Estas pruebas vigilan el contrato con el RTL:
el tamaño, el límite de palabras, el redondeo y la saturación.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from sofifi.domain.aritmetica import (
    DATO_FRAC,
    DATO_MAX,
    DATO_MIN,
    MEM_BITS,
    MEM_BITS_CORTO,
    dato,
    dato_a_memoria,
)
from sofifi.domain.coste import ciclos_rtl
from sofifi.domain.ensamblador import ErrorEnsamblado, ensamblar
from sofifi.domain.memoria import MemoriaRetardo, palabras_max

FS = 100_000_000 / 2048


def test_el_tope_de_palabras_sale_del_tamano() -> None:
    assert palabras_max(MEM_BITS) == 43_008  # 42 bloques × 1 024
    assert palabras_max(MEM_BITS_CORTO) == 64_512  # 42 bloques × 1 536
    assert palabras_max(MEM_BITS_CORTO) == 3 * palabras_max(MEM_BITS) // 2
    with pytest.raises(ValueError, match="solo"):
        palabras_max(9)


def test_el_tiempo_de_retardo_crece_una_vez_y_media() -> None:
    corto = palabras_max(MEM_BITS) / FS
    largo = palabras_max(MEM_BITS_CORTO) / FS
    assert math.isclose(corto, 0.881, abs_tol=0.001)
    assert math.isclose(largo, 1.321, abs_tol=0.001)


def test_una_palabra_de_12_bit_redondea_y_satura() -> None:
    perdida = DATO_FRAC + 1 - MEM_BITS_CORTO  # 12 bit
    # Alineada a dato: los 12 bit bajos quedan a cero.
    for valor in (0, dato("0.5"), dato("-0.5"), 12345, -98765):
        guardado = dato_a_memoria(valor, MEM_BITS_CORTO)
        assert guardado % (1 << perdida) == 0
        assert abs(guardado - valor) <= (1 << perdida) // 2
    # Redondeo de medio LSB hacia arriba, como en 18 bit.
    assert dato_a_memoria(1 << (perdida - 1), MEM_BITS_CORTO) == 1 << perdida
    # Saturación: nunca envuelve.
    assert dato_a_memoria(DATO_MAX, MEM_BITS_CORTO) <= DATO_MAX
    assert dato_a_memoria(DATO_MIN, MEM_BITS_CORTO) >= DATO_MIN


def test_la_memoria_de_12_bit_guarda_con_su_tamano() -> None:
    m = MemoriaRetardo(10, bits=MEM_BITS_CORTO)
    assert m.bits == MEM_BITS_CORTO
    m.escribir(0, dato("0.3"))
    assert m.leer(0) == dato_a_memoria(dato("0.3"), MEM_BITS_CORTO)
    assert m.leer(0) != dato_a_memoria(dato("0.3"), MEM_BITS)  # 18 bit es más fino

    larga = MemoriaRetardo(64_512, bits=MEM_BITS_CORTO)
    assert larga.palabras == 64_512
    with pytest.raises(ValueError, match="fuera de"):
        MemoriaRetardo(64_512)  # con 18 bit no cabe


def test_la_directiva_cambia_el_limite_del_programa() -> None:
    cuerpo = "mem larga 60000\nrda larga#, 1.0\nwra larga, 0\n"
    programa = ensamblar("palabra 12\n" + cuerpo, "larga12")
    assert programa.bits_memoria == MEM_BITS_CORTO
    assert programa.palabras_memoria == 60_001
    with pytest.raises(ErrorEnsamblado, match="palabras de 18 bit"):
        ensamblar(cuerpo, "larga18")


def test_sin_la_directiva_nada_cambia() -> None:
    programa = ensamblar("mem l 100\nrda l#, 1.0\nwra l, 0\n", "corto")
    assert programa.bits_memoria == MEM_BITS


@pytest.mark.parametrize("linea", ["palabra 9", "palabra", "palabra doce", "palabra 12 13"])
def test_la_directiva_rechaza_lo_que_no_es(linea: str) -> None:
    with pytest.raises(ErrorEnsamblado):
        ensamblar(f"{linea}\nmem l 10\nrda l#, 1.0\n", "malo")


def test_escribir_en_12_bit_cuesta_mas_ciclos() -> None:
    """Tres muestras de 12 bit ocupan dos palabras: escribir lee antes la pareja.

    Es una cota declarada (coste.ESCRITURA_12_BIT), no una medida: el PR 2 de la
    Fase 14 la sustituye por los ciclos de la simulación (ADR 0014).
    """
    cuerpo = "mem l 1000\nrda l#, 1.0\nwra l, 0\n"
    assert ciclos_rtl(ensamblar("palabra 12\n" + cuerpo, "a")) > ciclos_rtl(ensamblar(cuerpo, "b"))


def test_la_senal_senal_ruido_de_una_linea_de_12_bit() -> None:
    """Una línea de 12 bit da 60 dB o más con una señal de nivel normal.

    Es el criterio de la fase: con 9 bit no llega (37 dB medidos en un tanque).
    """
    azar = np.random.default_rng(11)
    x = azar.uniform(-0.3, 0.3, 20_000) * (1 << DATO_FRAC)
    guardado = np.array([dato_a_memoria(int(v), MEM_BITS_CORTO) for v in x], dtype=float)
    ruido = guardado - x
    snr = 10 * np.log10(np.mean(x**2) / np.mean(ruido**2))
    assert snr > 60.0, f"{snr:.1f} dB"
