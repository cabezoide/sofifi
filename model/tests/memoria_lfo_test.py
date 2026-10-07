# SPDX-License-Identifier: MIT
"""Memoria circular, interpolación Hermite, LFSR y LFOs (ADR 0008)."""

from __future__ import annotations

from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st
from sofifi.domain.aritmetica import DATO_MAX, UNO, dato
from sofifi.domain.interpolacion import FRACCIONES, coeficientes, tabla_hermite
from sofifi.domain.lfo import (
    FASE_MOD,
    LFSR_SEMILLA,
    ConfigLfo,
    Lfo,
    TipoLfo,
    lfsr_paso,
    triangulo,
    ventana,
)
from sofifi.domain.memoria import PALABRAS_MAX, MemoriaRetardo


def test_lo_escrito_en_a_se_lee_en_a_mas_n_tras_n_muestras() -> None:
    m = MemoriaRetardo(100)
    m.escribir(5, dato("0.5"))
    for _ in range(7):
        m.avanzar()
    assert m.leer(12) == dato("0.5")
    assert m.leer(11) == 0


def test_limites_de_memoria() -> None:
    with pytest.raises(ValueError):
        MemoriaRetardo(PALABRAS_MAX + 1)
    assert MemoriaRetardo(PALABRAS_MAX).palabras == 43008


@given(st.fractions(min_value=0, max_value=Fraction(255, 256)))
def test_hermite_es_particion_de_la_unidad(f: Fraction) -> None:
    assert sum(coeficientes(f)) == 1


def test_tabla_hermite_exacta_en_los_extremos() -> None:
    t = tabla_hermite()
    assert len(t) == FRACCIONES
    assert t[0] == (0, 1 << 16, 0, 0)


def test_interpolacion_reproduce_una_rampa() -> None:
    m = MemoriaRetardo(64)
    for i in range(64):
        m.escribir(0, (i * UNO) // 128)
        m.avanzar()
    # dirección d = muestra escrita hace d (+1) avances: valores decrecientes en d
    v_entero = m.leer_interpolado(10, 10 * 0, tabla_hermite())
    v_medio = m.leer_interpolado(10, 128, tabla_hermite())
    v_siguiente = m.leer(11)
    assert abs(v_medio - (v_entero + v_siguiente) // 2) <= 128


def test_lfsr_no_se_bloquea() -> None:
    s = LFSR_SEMILLA
    vistos = set()
    for _ in range(1000):
        s = lfsr_paso(s)
        vistos.add(s)
    assert 0 not in vistos and len(vistos) == 1000


def test_triangulo_y_ventana() -> None:
    assert triangulo(0) == 0
    assert triangulo(FASE_MOD // 4) == DATO_MAX
    assert ventana(0) == 0
    assert ventana(FASE_MOD // 2) == DATO_MAX


def test_lfo_sin_oscila_dentro_de_la_excursion() -> None:
    lfo = Lfo(ConfigLfo(TipoLfo.SIN, excursion=16))
    valores = []
    for _ in range(2000):
        lfo.avanzar(FASE_MOD // 1000)
        valores.append(lfo.desplazamiento_q8(DATO_MAX))
    assert min(valores) >= 0
    assert max(valores) <= 32 * 256
    assert max(valores) - min(valores) > 30 * 256


def test_lfo_ramp_sube_y_media_fase() -> None:
    lfo = Lfo(ConfigLfo(TipoLfo.RAMP, excursion=4096))
    lfo.avanzar(FASE_MOD // 4)
    assert lfo.desplazamiento_q8(0) == 1024 * 256
    assert lfo.desplazamiento_q8(0, media=True) == 3072 * 256


def test_lfo_rnd_es_determinista_y_acotado() -> None:
    a = Lfo(ConfigLfo(TipoLfo.RND, excursion=8))
    b = Lfo(ConfigLfo(TipoLfo.RND, excursion=8))
    sa, sb = [], []
    for _ in range(5000):
        a.avanzar(FASE_MOD // 500)
        b.avanzar(FASE_MOD // 500)
        sa.append(a.desplazamiento_q8(DATO_MAX))
        sb.append(b.desplazamiento_q8(DATO_MAX))
    assert sa == sb
    assert len(set(sa)) > 100
    assert all(0 <= v <= 16 * 256 for v in sa)


def test_excursion_fuera_de_rango() -> None:
    with pytest.raises(ValueError):
        ConfigLfo(TipoLfo.SIN, excursion=0)
