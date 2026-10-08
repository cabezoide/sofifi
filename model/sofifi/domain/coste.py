# SPDX-License-Identifier: MIT
"""Ciclos que gasta el núcleo RTL por muestra: el presupuesto real de un programa.

El ADR 0009 cuenta 1 ciclo por instrucción (``Programa.ciclos``). El RTL
multiciclo gasta más: cada instrucción espera a su resultado (Fase 06). Esta
tabla da el coste de cada instrucción en el RTL. La prueba
``coste_de_cada_instruccion`` de ``sim/nucleo/nucleo_test.py`` la mide en
simulación y falla si el RTL cambia y la tabla no.

``ciclos_rtl`` es una cota superior: cuenta todas las instrucciones, también
las que un ``SKP`` puede saltar, y cada ``SKP`` como si saltara.
"""

from __future__ import annotations

from sofifi.domain.aritmetica import CICLOS_POR_MUESTRA
from sofifi.domain.isa import Cho, Instruccion, Op, Programa

CICLOS_FIJOS_RTL = 34  # arranque, avance de los LFO, primera lectura y fin (cota)
CICLOS_RTL: dict[Op, int] = {
    Op.NOP: 6,
    Op.LDAX: 6,
    Op.CLR: 6,
    Op.ABSA: 6,
    Op.RDAX: 10,
    Op.WRAX: 10,
    Op.WRA: 10,
    Op.WRAP: 10,
    Op.MAXX: 10,
    Op.MULX: 10,
    Op.SOF: 10,
    Op.RDFX: 11,
    Op.CLIP: 14,
    Op.RDA: 19,
    Op.CHO: 52,
    Op.SKP: 8,  # si salta: vuelve a leer el microcódigo
    Op.RDAA: 27,  # dos lecturas, la diferencia por la fracción y el producto por C
    Op.WRAA: 10,
}
CICLOS_SKP_SIN_SALTO = 6
CICLOS_CHO_NA = 5  # la ventana del pitch shifter es una multiplicación más


def ciclos_instruccion_rtl(ins: Instruccion) -> int:
    extra = CICLOS_CHO_NA if ins.op is Op.CHO and ins.flags & Cho.NA else 0
    return CICLOS_RTL[ins.op] + extra


def ciclos_rtl(programa: Programa) -> int:
    """Cota superior de los ciclos por muestra del programa en el núcleo RTL."""
    return CICLOS_FIJOS_RTL + sum(ciclos_instruccion_rtl(i) for i in programa.instrucciones)


def cabe_en_el_rtl(programa: Programa) -> bool:
    return ciclos_rtl(programa) <= CICLOS_POR_MUESTRA
