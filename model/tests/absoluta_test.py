# SPDX-License-Identifier: MIT
"""RDAA y WRAA: la región absoluta de 32 768 palabras (ADR 0009, actualización de la Fase 07)."""

from __future__ import annotations

import pytest
from sofifi.domain.aritmetica import DATO_FRAC, dato, dato_a_memoria
from sofifi.domain.coste import DURACION
from sofifi.domain.ensamblador import ErrorEnsamblado, ensamblar
from sofifi.domain.isa import Instruccion, Op
from sofifi.domain.memoria import PALABRAS_ABSOLUTAS, MemoriaRetardo
from sofifi.domain.nucleo import Nucleo

UNA_MUESTRA = 1 << 8  # en R, la parte entera empieza en el bit 8


def test_toda_instruccion_tiene_coste_en_el_rtl() -> None:
    assert set(DURACION) == set(Op)


def test_escribir_y_leer_en_la_misma_posicion() -> None:
    m = MemoriaRetardo(10, absoluta=True)
    m.escribir_absoluta(0, 5 * UNA_MUESTRA, dato("0.3"))
    assert m.leer_absoluta(0, 5 * UNA_MUESTRA) == dato_a_memoria(dato("0.3"))
    assert m.leer_absoluta(5, 0) == dato_a_memoria(dato("0.3"))  # el origen se suma


def test_la_lectura_interpola_linealmente() -> None:
    m = MemoriaRetardo(10, absoluta=True)
    m.escribir_absoluta(0, 7 * UNA_MUESTRA, dato("0.2"))
    m.escribir_absoluta(0, 8 * UNA_MUESTRA, dato("0.6"))
    a, b = dato_a_memoria(dato("0.2")), dato_a_memoria(dato("0.6"))
    assert m.leer_absoluta(0, 7 * UNA_MUESTRA + 128) == a + (((b - a) * 128) >> 8)
    assert m.leer_absoluta(0, 7 * UNA_MUESTRA + 64) == a + (((b - a) * 64) >> 8)


def test_la_region_se_cierra_sobre_si_misma() -> None:
    m = MemoriaRetardo(10, absoluta=True)
    m.escribir_absoluta(PALABRAS_ABSOLUTAS - 1, UNA_MUESTRA, dato("0.5"))  # i = 32 768 → 0
    assert m.leer_absoluta(0, 0) == dato_a_memoria(dato("0.5"))
    m.escribir_absoluta(0, -UNA_MUESTRA, dato("0.25"))  # R negativo: solo cuentan 23 bit
    assert m.leer_absoluta(0, (1 << 23) - UNA_MUESTRA) == dato_a_memoria(dato("0.25"))


def test_un_bucle_graba_y_reproduce_lo_mismo() -> None:
    """Graba 100 muestras con WRAA y las repite con RDAA: la región no avanza sola."""
    p = ensamblar(
        """
        equ  pos  reg0
        rdax adcl, 1.0
        wraa pos, 0
        rdaa pos, 1.0
        wrax dacl, 0
        rdax pos, 1.0
        sof  1.0, 1/32768            ; una muestra más (2^-15 = 1 << 8 en R)
        wrax pos, 0
        """
    )
    n = Nucleo(p)
    entrada = [dato(f"{(k % 7 - 3) / 10}") for k in range(100)]
    salida = [n.procesar(x, 0)[0] for x in entrada]
    assert salida == [dato_a_memoria(x) for x in entrada]
    m = n.memoria
    assert [m.leer_absoluta(0, k * UNA_MUESTRA) for k in range(100)] == salida


def test_validaciones_de_la_region_absoluta() -> None:
    with pytest.raises(ErrorEnsamblado, match="región absoluta"):
        ensamblar("mem d 20000\nrdaa reg0, 1.0\nwra d, 0\n")
    with pytest.raises(ErrorEnsamblado, match="fuera de la región absoluta"):
        ensamblar("rdaa reg0, 1.0, 40000\n")
    p = ensamblar("rdaa reg3, 0.5, 100\nwraa reg4, -1.0\n")
    assert p.usa_absoluta
    assert p.instrucciones[0] == Instruccion(Op.RDAA, reg=3, coef=1 << 15, addr=100)
    assert not ensamblar("rdax adcl, 1.0\n").usa_absoluta
    assert DATO_FRAC == 23
