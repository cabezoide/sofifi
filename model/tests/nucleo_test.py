# SPDX-License-Identifier: MIT
"""ISA e intérprete (ADR 0009): semántica por instrucción y contratos de despacho."""

from __future__ import annotations

from itertools import pairwise

import pytest
from hypothesis import given
from hypothesis import strategies as st
from sofifi.domain.aritmetica import DATO_MAX, DATO_MIN, UNO, acc_a_dato, coef, curva_suave, dato
from sofifi.domain.isa import (
    BITS_PALABRA,
    CICLOS,
    DACL,
    DACR,
    LFO_BASE,
    MAX_INSTRUCCIONES,
    POT_BASE,
    Cho,
    Instruccion,
    Op,
    Programa,
    Skp,
    codificar,
    decodificar,
)
from sofifi.domain.lfo import NUM_LFOS, ConfigLfo, TipoLfo
from sofifi.domain.nucleo import MANEJADORES, Nucleo

Ins = Instruccion
UNO_C = coef(1)


def prog(
    *ins: Instruccion, mem: int = 64, lfos: tuple[ConfigLfo | None, ...] | None = None
) -> Programa:
    return Programa("t", tuple(ins), mem, lfos or (None,) * NUM_LFOS)


def correr(p: Programa, entradas: list[int], pots: tuple[int, ...] = ()) -> list[int]:
    n = Nucleo(p)
    return [n.procesar(x, 0, pots)[0] for x in entradas]


# ── contratos ────────────────────────────────────────────────────────────


def test_toda_instruccion_tiene_manejador_y_ciclos() -> None:
    assert set(MANEJADORES) == set(Op)
    assert set(CICLOS) == set(Op)


def test_la_palabra_mide_54_bit() -> None:
    assert BITS_PALABRA == 54


@given(
    st.sampled_from(list(Op)),
    st.integers(0, 63),
    st.integers(0, 63),
    st.integers(-(1 << 17), (1 << 17) - 1),
    st.integers(0, (1 << 18) - 1),
)
def test_codificacion_ida_y_vuelta(op: Op, reg: int, flags: int, c: int, addr: int) -> None:
    ins = Instruccion(op, reg, flags, c, addr)
    palabra = codificar(ins)
    assert palabra < 1 << 54
    assert decodificar(palabra) == ins


def test_codificar_rechaza_campos_que_no_caben() -> None:
    with pytest.raises(ValueError):
        codificar(Instruccion(Op.RDAX, reg=64))
    with pytest.raises(ValueError):
        codificar(Instruccion(Op.RDAX, coef=1 << 17))


# ── validación de programas ──────────────────────────────────────────────


def test_programa_rechaza_limites() -> None:
    with pytest.raises(ValueError, match="instrucciones"):
        prog(*[Ins(Op.NOP)] * (MAX_INSTRUCCIONES + 1))
    with pytest.raises(ValueError, match="ciclos"):
        prog(*[Ins(Op.CHO, reg=0)] * 600, lfos=(ConfigLfo(TipoLfo.SIN, 4), None, None, None))
    with pytest.raises(ValueError, match="solo lectura"):
        prog(Ins(Op.WRAX, reg=POT_BASE))
    with pytest.raises(ValueError, match="no está declarado"):
        prog(Ins(Op.CHO, reg=1))
    with pytest.raises(ValueError, match="fuera del programa"):
        prog(Ins(Op.SKP, flags=Skp.RUN, addr=5))
    with pytest.raises(ValueError, match="fuera de la memoria"):
        prog(Ins(Op.RDA, addr=64), mem=64)
    # CHO SIN con E = 4 sobre 0 lee hasta 0 + 2·4 + 1 = 9: con 9 palabras no cabe.
    sin4 = (ConfigLfo(TipoLfo.SIN, 4), None, None, None)
    with pytest.raises(ValueError, match="CHO lee hasta la dirección 9"):
        prog(Ins(Op.CHO, reg=0), lfos=sin4, mem=9)
    prog(Ins(Op.CHO, reg=0), lfos=sin4, mem=10)


# ── semántica ────────────────────────────────────────────────────────────


def test_paso_directo_rdax_wrax() -> None:
    p = prog(Ins(Op.RDAX, reg=32, coef=UNO_C), Ins(Op.WRAX, reg=DACL))
    assert correr(p, [dato("0.25"), dato("-0.5")]) == [dato("0.25"), dato("-0.5")]


def test_ganancia_y_saturacion() -> None:
    p = prog(
        Ins(Op.RDAX, reg=32, coef=coef("1.5")),
        Ins(Op.RDAX, reg=32, coef=coef("1.5")),
        Ins(Op.WRAX, reg=DACL),
    )
    assert correr(p, [dato("0.5")]) == [DATO_MAX]
    assert correr(p, [dato("-0.5")]) == [DATO_MIN]


def test_delay_con_wra_y_rda() -> None:
    # escribe la entrada en 0 y lee en 3: tres muestras de retardo
    p = prog(
        Ins(Op.RDAX, reg=32, coef=UNO_C),
        Ins(Op.WRA, addr=0),
        Ins(Op.RDA, addr=3, coef=UNO_C),
        Ins(Op.WRAX, reg=DACL),
    )
    x = [dato("0.5"), 0, 0, 0, 0]
    assert correr(p, x) == [0, 0, 0, dato("0.5"), 0]


def test_allpass_es_energeticamente_neutro() -> None:
    k = coef("0.5")
    p = prog(
        Ins(Op.RDAX, reg=32, coef=UNO_C),
        Ins(Op.RDA, addr=7, coef=k),
        Ins(Op.WRAP, addr=0, coef=-k),
        Ins(Op.WRAX, reg=DACL),
    )
    y = correr(p, [dato("0.5")] + [0] * 400)
    energia_x = (dato("0.5") / UNO) ** 2
    energia_y = sum((v / UNO) ** 2 for v in y)
    assert abs(energia_y - energia_x) / energia_x < 1e-3


def test_rdfx_es_paso_bajo() -> None:
    # y = y + C·(x − y) con el estado en reg0
    p = prog(
        Ins(Op.RDAX, reg=32, coef=UNO_C),
        Ins(Op.RDFX, reg=0, coef=coef("0.1")),
        Ins(Op.WRAX, reg=0, coef=UNO_C),
        Ins(Op.WRAX, reg=DACL),
    )
    y = correr(p, [dato("0.5")] * 200)
    # 0,1 se cuantiza a 6554/65536: la primera salida es exactamente 0,5 · ese coeficiente
    assert y[0] == acc_a_dato(dato("0.5") * coef("0.1"))
    assert y[-1] == pytest.approx(dato("0.5"), abs=64)
    assert all(a <= b for a, b in pairwise(y))


def test_mulx_multiplica_por_registro() -> None:
    p = prog(Ins(Op.RDAX, reg=32, coef=UNO_C), Ins(Op.MULX, reg=POT_BASE), Ins(Op.WRAX, reg=DACL))
    assert correr(p, [dato("0.5")], pots=(dato("0.5"),)) == [dato("0.25")]


def test_sof_escala_y_desplaza() -> None:
    # D = 0.25 en S2.15 → 0.25·2^15
    p = prog(
        Ins(Op.RDAX, reg=32, coef=UNO_C),
        Ins(Op.SOF, coef=coef("0.5"), addr=1 << 13),
        Ins(Op.WRAX, reg=DACL),
    )
    assert correr(p, [dato("0.5")]) == [dato("0.5")]


def test_sof_con_d_negativo() -> None:
    d = (-(1 << 14)) & ((1 << 18) - 1)  # -0.5
    p = prog(Ins(Op.CLR), Ins(Op.SOF, coef=0, addr=d), Ins(Op.WRAX, reg=DACL))
    assert correr(p, [0]) == [dato("-0.5")]


def test_clip_maxx_absa_ldax() -> None:
    p = prog(Ins(Op.RDAX, reg=32, coef=UNO_C), Ins(Op.CLIP), Ins(Op.WRAX, reg=DACL))
    assert correr(p, [dato("0.5")]) == [curva_suave(dato("0.5"))]
    p = prog(Ins(Op.RDAX, reg=32, coef=UNO_C), Ins(Op.ABSA), Ins(Op.WRAX, reg=DACL))
    assert correr(p, [dato("-0.5")]) == [dato("0.5")]
    p = prog(Ins(Op.LDAX, reg=POT_BASE), Ins(Op.MAXX, reg=32, coef=UNO_C), Ins(Op.WRAX, reg=DACL))
    assert correr(p, [dato("-0.75")], pots=(dato("0.25"),)) == [dato("0.75")]


def test_skp_run_ejecuta_la_inicializacion_solo_una_vez() -> None:
    p = prog(
        Ins(Op.SKP, flags=Skp.RUN, addr=2),
        Ins(Op.SOF, coef=0, addr=1 << 14),  # ACC = 0.5
        Ins(Op.WRAX, reg=0),  # reg0 = 0.5 solo la primera vez
        Ins(Op.LDAX, reg=0),
        Ins(Op.SOF, coef=coef("0.5")),
        Ins(Op.WRAX, reg=0, coef=UNO_C),  # reg0 se reduce a la mitad cada muestra
        Ins(Op.WRAX, reg=DACL),
    )
    assert correr(p, [0, 0, 0]) == [dato("0.25"), dato("0.125"), dato("0.0625")]


def test_skp_condiciones_de_signo() -> None:
    def con(flags: Skp, x: int) -> int:
        p = prog(
            Ins(Op.RDAX, reg=32, coef=UNO_C),
            Ins(Op.SKP, flags=flags, addr=1),
            Ins(Op.CLR),
            Ins(Op.WRAX, reg=DACL),
        )
        return correr(p, [x])[0]

    assert con(Skp.NEG, dato("-0.5")) == dato("-0.5")
    assert con(Skp.NEG, dato("0.5")) == 0
    assert con(Skp.GEZ, dato("0.5")) == dato("0.5")
    assert con(Skp.ZRO, 0) == 0


def test_cho_con_lfo_quieto_es_un_delay_de_e_muestras() -> None:
    lfos = (ConfigLfo(TipoLfo.SIN, excursion=4), None, None, None)
    p = prog(
        Ins(Op.RDAX, reg=32, coef=UNO_C),
        Ins(Op.WRA, addr=0),
        Ins(Op.CHO, reg=0, coef=UNO_C, addr=0),
        Ins(Op.WRAX, reg=DACL),
        lfos=lfos,
    )
    y = correr(p, [dato("0.5")] + [0] * 8)
    assert y[4] == dato("0.5")
    assert sum(1 for v in y if v) == 1


def test_cho_rampa_con_ventana_fundida_sube_una_octava() -> None:
    """Dos taps en rampa + ventanas complementarias: un tono puro sube una octava."""
    import math

    w = 1024
    lfos = (ConfigLfo(TipoLfo.RAMP, excursion=w), None, None, None)
    rate = -(1 << 24) // w  # el retardo baja 1 muestra por muestra → ×2
    p = prog(
        Ins(Op.SKP, flags=Skp.RUN, addr=2),
        Ins(Op.SOF, coef=0, addr=0),
        Ins(Op.NOP),
        Ins(Op.RDAX, reg=32, coef=UNO_C),
        Ins(Op.WRA, addr=0),
        Ins(Op.CHO, reg=0, flags=Cho.NA, coef=UNO_C, addr=1),
        Ins(Op.CHO, reg=0, flags=Cho.NA | Cho.MEDIA, coef=UNO_C, addr=1),
        Ins(Op.WRAX, reg=DACL),
        mem=w + 8,
        lfos=lfos,
    )
    n = Nucleo(p)
    n.regs[LFO_BASE] = rate
    f, fs, total = 400.0, 48828.125, 8192
    x = [dato(str(round(0.4 * math.sin(2 * math.pi * f * k / fs), 6))) for k in range(total)]
    y = [n.procesar(v, 0)[0] / UNO for v in x][2048:]

    def potencia(freq: float) -> float:
        re = sum(v * math.cos(2 * math.pi * freq * k / fs) for k, v in enumerate(y))
        im = sum(v * math.sin(2 * math.pi * freq * k / fs) for k, v in enumerate(y))
        return re * re + im * im

    assert potencia(2 * f) > 20 * potencia(f)


def test_registros_de_salida_estereo() -> None:
    p = prog(
        Ins(Op.RDAX, reg=32, coef=UNO_C), Ins(Op.WRAX, reg=DACL, coef=UNO_C), Ins(Op.WRAX, reg=DACR)
    )
    assert Nucleo(p).procesar(dato("0.5"), 0) == (dato("0.5"), dato("0.5"))
