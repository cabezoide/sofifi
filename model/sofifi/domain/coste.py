# SPDX-License-Identifier: MIT
"""Ciclos que gasta el núcleo RTL por muestra: el presupuesto real de un programa.

El ADR 0009 cuenta 1 ciclo por instrucción (``Programa.ciclos``). El RTL gasta
más. Desde el ADR 0014 el núcleo va segmentado en orden y el coste de una
instrucción depende de las anteriores. Este módulo reproduce el secuenciador
de ``rtl/nucleo/nucleo.v`` ciclo a ciclo:

1. La decodificación toma una instrucción en un ciclo (estado E_LEER). La
   ejecución empieza en el ciclo siguiente y dura ``DURACION`` ciclos.
2. La instrucción que deja un producto en la línea de retiro escribe el ACC
   unos ciclos después de su último ciclo de ejecución.
3. Una instrucción que lee el ACC no se decodifica hasta que el retiro está
   vacío (``RETIRO`` ciclos). Una que lee el banco de registros espera
   ``TRAS_WRAX`` ciclos tras un WRAX.
4. Un ``SKP`` que salta vacía la cola del microcódigo: la siguiente decodificación
   llega ``TRAS_SALTO`` ciclos después (uno más si lee el banco: sus candidatos
   se registran un ciclo después de que llegue la cabeza).

La prueba ``igual_al_modelo`` de ``sim/nucleo/nucleo_test.py`` exige que el RTL
gaste exactamente ``ciclos_rtl`` en los programas sin ``SKP`` y no más en el resto.
``ciclos_rtl`` es una cota superior con ``SKP``: cuenta todas las instrucciones,
también las que un salto evita, y cada ``SKP`` como si saltara.
"""

from __future__ import annotations

from collections.abc import Sequence

from sofifi.domain.aritmetica import CICLOS_POR_MUESTRA
from sofifi.domain.isa import Cho, Instruccion, Op, Programa
from sofifi.domain.lfo import ConfigLfo, TipoLfo

PRIMERA_DECODIFICACION = 28  # el arranque y el avance de los LFO (26 ciclos)
RETIRO = 7  # del último ciclo de ejecución a la decodificación que lee el ACC
TRAS_WRAX = 3  # del WRAX a la decodificación que lee el banco
TRAS_SALTO = 8  # de un SKP que salta a la siguiente decodificación
FIN = 1  # el estado E_FIN

# Ciclos de ejecución (E_EJEC) de cada instrucción. LAT = 5 (multiplicador) y
# LAT_MEM = 9 (memoria de retardo segmentada).
DURACION: dict[Op, int] = {
    Op.NOP: 1,
    Op.LDAX: 1,
    Op.CLR: 1,
    Op.ABSA: 1,
    Op.RDAX: 1,
    Op.WRAX: 1,
    Op.WRA: 1,
    Op.WRAP: 1,
    Op.MAXX: 1,
    Op.MULX: 1,
    Op.SOF: 1,
    Op.WRAA: 1,
    Op.RDFX: 2,  # a24 − R se registra antes de multiplicar
    Op.SKP: 1,
    Op.RDA: 10,  # la lectura y LAT_MEM ciclos de espera
    Op.CLIP: 12,  # dos productos y la curva suave
    Op.RDAA: 18,  # dos lecturas, la diferencia por la fracción y el producto por C
    Op.CHO: 43,  # con LFO SIN; ver DURACION_CHO
}
DURACION_CHO = {TipoLfo.SIN: 43, TipoLfo.RND: 32, TipoLfo.RAMP: 27}
DURACION_CHO_NA = 5  # la ventana del pitch shifter es un producto más

LEE_ACC = frozenset(
    {Op.WRA, Op.WRAP, Op.WRAX, Op.RDFX, Op.MULX, Op.SOF, Op.CLIP, Op.SKP, Op.WRAA, Op.MAXX, Op.ABSA}
)
LEE_REGISTRO = frozenset({Op.RDAX, Op.MAXX, Op.RDFX, Op.MULX, Op.LDAX, Op.RDAA, Op.WRAA, Op.CHO})
SIN_RETIRO = frozenset({Op.NOP, Op.SKP, Op.CLIP})  # CLIP escribe el ACC él mismo


def duracion(ins: Instruccion, lfos: Sequence[ConfigLfo | None] = ()) -> int:
    """Ciclos de ejecución. Sin la configuración del LFO, el CHO cuenta como SIN (la cota)."""
    if ins.op is not Op.CHO:
        return DURACION[ins.op]
    config = lfos[ins.reg] if ins.reg < len(lfos) else None
    base = DURACION_CHO[config.tipo] if config is not None else DURACION_CHO[TipoLfo.SIN]
    return base + (DURACION_CHO_NA if ins.flags & Cho.NA else 0)


def ciclos_secuencia(
    instrucciones: Sequence[Instruccion], lfos: Sequence[ConfigLfo | None] = ()
) -> int:
    """Ciclos de una muestra, de `tick` a `fin`, con todas las instrucciones."""
    libre = PRIMERA_DECODIFICACION  # primer ciclo en que E_LEER puede decodificar
    libre_reg = libre  # lo mismo para quien lee el banco: tras un salto, un ciclo más
    retiro = 0  # primer ciclo con el retiro vacío
    banco = 0  # primer ciclo con el banco escrito tras el último WRAX
    for ins in instrucciones:
        x = libre
        if ins.op in LEE_ACC:
            x = max(x, retiro)
        if ins.op in LEE_REGISTRO:
            x = max(x, libre_reg, banco)
        ultimo = x + duracion(ins, lfos)
        if ins.op not in SIN_RETIRO:
            retiro = ultimo + RETIRO
        if ins.op is Op.WRAX:
            banco = ultimo + TRAS_WRAX
        libre = ultimo + (TRAS_SALTO if ins.op is Op.SKP else 1)
        libre_reg = libre + (ins.op is Op.SKP)
    return max(libre, retiro, banco) + FIN


def ciclos_rtl(programa: Programa) -> int:
    """Cota superior de los ciclos por muestra del programa en el núcleo RTL."""
    return ciclos_secuencia(programa.instrucciones, programa.lfos)


def cabe_en_el_rtl(programa: Programa) -> bool:
    return ciclos_rtl(programa) <= CICLOS_POR_MUESTRA
