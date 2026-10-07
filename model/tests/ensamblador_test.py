# SPDX-License-Identifier: MIT
"""Ensamblador: sintaxis, errores con línea, y equivalencia con la semántica FV-1."""

from __future__ import annotations

import pytest
from sofifi.domain.aritmetica import UNO, coef, dato
from sofifi.domain.ensamblador import MNEMONICOS, ErrorEnsamblado, ensamblar
from sofifi.domain.isa import DACL, Cho, Instruccion, Op, Skp
from sofifi.domain.lfo import TipoLfo
from sofifi.domain.nucleo import Nucleo


def test_todo_opcode_tiene_mnemonico() -> None:
    assert set(MNEMONICOS.values()) == set(Op)


def test_mem_equ_y_sufijos() -> None:
    p = ensamblar(
        """
        ; comentario
        equ  k    0.5
        equ  kr   reg3
        mem  ap   100
        mem  d    10
        rda  ap#, k
        wrap ap, -k
        wra  d^, 0
        wrax kr, 1.0
        """
    )
    assert p.palabras_memoria == 101 + 11
    assert p.instrucciones[0] == Instruccion(Op.RDA, coef=coef("0.5"), addr=100)
    assert p.instrucciones[1] == Instruccion(Op.WRAP, coef=coef("-0.5"), addr=0)
    assert p.instrucciones[2] == Instruccion(Op.WRA, addr=101 + 5)
    assert p.instrucciones[3] == Instruccion(Op.WRAX, reg=3, coef=coef(1))


def test_expresiones_exactas_y_redondeo_de_direcciones() -> None:
    p = ensamblar("mem d 1000\nrda d + 266 * 1.6406, (1 - 0.0005) / 2\n")
    ins = p.instrucciones[0]
    assert ins.addr == 436  # 436,4 → 436
    assert ins.coef == coef("0.49975")


def test_skp_por_etiqueta_y_lfo_y_cho() -> None:
    p = ensamblar(
        """
        lfo 1 ramp 4096
        mem pit 4100
        skp run, inicio
        clr
        inicio:
        cho pit, 1.0, lfo1, na|media
        sof 0.5, -0.25
        """
    )
    assert p.instrucciones[0] == Instruccion(Op.SKP, flags=int(Skp.RUN), addr=1)
    assert p.lfos[1] is not None and p.lfos[1].tipo is TipoLfo.RAMP
    assert p.instrucciones[2].flags == int(Cho.NA | Cho.MEDIA)
    assert p.instrucciones[3].addr == (-(1 << 13)) & ((1 << 18) - 1)


@pytest.mark.parametrize(
    ("texto", "mensaje"),
    [
        ("rdax foo, 1.0", "registro desconocido"),
        ("rda nada, 1.0", "símbolo desconocido"),
        ("rdax adcl, 2.5", "fuera de rango"),
        ("wrax pot0, 0", "solo lectura"),
        ("wlds sin0, 12, 100", "es del FV-1"),
        ("frobnicate", "desconocida"),
        ("rdax adcl", "espera 2 operandos"),
        ("a:\nskp run, a", "hacia delante"),
        ("rdax adcl, __import__", "símbolo desconocido"),
        ("rdax adcl, 1 +", "incompleta"),
        ("rdax adcl, 1/0", "división por cero"),
        ("lfo 7 sin 4", "fuera de 0..3"),
        ("cho 0, 1.0, lfo0", "no está declarado"),
    ],
)
def test_errores_con_numero_de_linea(texto: str, mensaje: str) -> None:
    with pytest.raises(ErrorEnsamblado, match=mensaje):
        ensamblar(texto)


def test_error_indica_la_linea() -> None:
    with pytest.raises(ErrorEnsamblado, match="línea 3"):
        ensamblar("clr\n\nrdax nope, 1\n")


INCLUIDOS = {
    "comun/decl.sasm": "equ k 0.5\nmem d 10\ninclude comun/hoja.sasm\n",
    "comun/hoja.sasm": "equ g reg4\n",
    "comun/malo.sasm": "clr\nrdax nope, 1\n",
    "a.sasm": "include b.sasm\n",
    "b.sasm": "include a.sasm\n",
}


def test_include_inserta_el_texto_en_su_sitio() -> None:
    con = ensamblar(
        "include comun/decl.sasm ; anidado\nrdax adcl, k\nwra d, 0\nwrax g, 0\n",
        incluir=INCLUIDOS.__getitem__,
    )
    sin = ensamblar("equ k 0.5\nmem d 10\nequ g reg4\nrdax adcl, k\nwra d, 0\nwrax g, 0\n")
    assert con == sin


@pytest.mark.parametrize(
    ("texto", "mensaje"),
    [
        ("clr\ninclude comun/malo.sasm", "comun/malo.sasm, línea 2: registro desconocido"),
        ("include a.sasm", "b.sasm, línea 1: include en ciclo: 'a.sasm'"),
        ("include", "uso: include"),
        ("include nada.sasm", "no se puede leer 'nada.sasm'"),
    ],
)
def test_errores_de_include(texto: str, mensaje: str) -> None:
    def incluir(nombre: str) -> str:
        if nombre not in INCLUIDOS:
            raise FileNotFoundError(nombre)
        return INCLUIDOS[nombre]

    with pytest.raises(ErrorEnsamblado, match=mensaje):
        ensamblar(texto, incluir=incluir)


def test_include_sin_funcion_de_lectura() -> None:
    with pytest.raises(ErrorEnsamblado, match="sin función para leer ficheros"):
        ensamblar("include comun/decl.sasm")


FV1 = """
; programa en sintaxis SpinASM: allpass + delay con realimentación
equ   fb    reg0
mem   ap1   156
mem   del   3000
rdax  adcl, 0.5
rdax  adcr, 0.5
rda   ap1#, 0.5
wrap  ap1, -0.5
rdax  fb, 0.6
wra   del, 0
rda   del#, 1.0
wrax  fb, 1.0
wrax  dacl, 0
"""


def _referencia_float(x: list[float]) -> list[float]:
    """La misma red en coma flotante con la semántica del FV-1."""
    ap = [0.0] * 157
    dl = [0.0] * 3001
    fb = 0.0
    salida = []
    for n, v in enumerate(x):
        acc = v
        fin_ap = ap[(n - 156) % 157]
        acc += fin_ap * 0.5
        ap[n % 157] = acc
        acc = acc * -0.5 + fin_ap
        acc += fb * 0.6
        dl[n % 3001] = acc
        acc = dl[(n - 3000) % 3001]
        fb = acc
        salida.append(acc)
    return salida


def test_programa_fv1_suena_equivalente_a_su_semantica() -> None:
    p = ensamblar(FV1, "fv1")
    nucleo = Nucleo(p)
    x = [0.0] * 10000
    x[0] = 0.5
    x[4000] = -0.3
    y = [nucleo.procesar(dato(str(v)), dato(str(v)))[0] / UNO for v in x]
    ref = _referencia_float(x)
    assert max(abs(a - b) for a, b in zip(y, ref, strict=True)) < 1e-4
    assert DACL == 34
