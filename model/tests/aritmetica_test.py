# SPDX-License-Identifier: MIT
"""Aritmética de punto fijo (ADR 0008): unitarias y propiedades."""

from __future__ import annotations

from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st
from sofifi.domain.aritmetica import (
    ACC_BITS,
    DATO_MAX,
    DATO_MIN,
    FS_EXACTA,
    acc_a_dato,
    coef,
    curva_suave,
    dato,
    dato_a_acc,
    dato_a_memoria,
    mac,
    redondear,
    saturar,
)

datos = st.integers(DATO_MIN, DATO_MAX)


def test_fs_es_exacta() -> None:
    assert Fraction(48828125, 1000) == FS_EXACTA


def test_redondeo_medio_hacia_arriba_y_floor_en_negativos() -> None:
    assert redondear(3, 1) == 2  # 1,5 → 2
    assert redondear(-3, 1) == -1  # -1,5 → -1 (half up)
    assert redondear(5, 0) == 5


def test_coeficientes_s1_16() -> None:
    assert coef("0.5") == 1 << 15
    assert coef("-2") == -(1 << 17)
    with pytest.raises(ValueError, match="fuera de rango"):
        coef("2")


def test_dato_satura_uno() -> None:
    assert dato(1) == DATO_MAX
    assert dato("-1") == DATO_MIN


@given(datos)
def test_ida_y_vuelta_acc(x: int) -> None:
    assert acc_a_dato(dato_a_acc(x)) == x


@given(st.integers(-(1 << 60), 1 << 60))
def test_acc_a_dato_siempre_en_rango(acc: int) -> None:
    assert DATO_MIN <= acc_a_dato(acc) <= DATO_MAX


@given(datos, st.integers(-(1 << 17), (1 << 17) - 1), st.integers(-(1 << 47), (1 << 47) - 1))
def test_mac_satura_el_acumulador(x: int, c: int, acc: int) -> None:
    r = mac(acc, x, c)
    assert -(1 << (ACC_BITS - 1)) <= r <= (1 << (ACC_BITS - 1)) - 1


@given(datos)
def test_memoria_de_18_bit_alineada_y_cercana(x: int) -> None:
    m = dato_a_memoria(x)
    assert m & 0x3F == 0
    assert DATO_MIN <= m <= DATO_MAX
    assert abs(m - x) <= 64


@given(datos, datos)
def test_curva_suave_monotona(a: int, b: int) -> None:
    lo, hi = min(a, b), max(a, b)
    assert curva_suave(lo) <= curva_suave(hi)


@given(datos)
def test_curva_suave_acotada_y_casi_impar(x: int) -> None:
    y = curva_suave(x)
    assert DATO_MIN <= y <= DATO_MAX
    if x > DATO_MIN:
        assert abs(y + curva_suave(-x)) <= 2


def test_curva_suave_extremos_y_pendiente() -> None:
    assert curva_suave(DATO_MAX) == DATO_MAX
    assert curva_suave(DATO_MIN) == DATO_MIN
    assert curva_suave(1000) == 1500


def test_saturar() -> None:
    assert saturar(1 << 30, 24) == DATO_MAX
    assert saturar(-(1 << 30), 24) == DATO_MIN
