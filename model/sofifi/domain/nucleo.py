# SPDX-License-Identifier: MIT
"""Intérprete bit-exact del núcleo SOFIFI (ADR 0003, ADR 0009).

Por muestra:

1. Se cargan ``adcl``/``adcr``, los potenciómetros y ``sw``.
2. Cada LFO avanza con sus registros ``lfoN_rate`` de la muestra anterior.
3. ``ACC = 0``, ``LR = 0`` y se ejecuta el programa de principio a fin.
4. La memoria avanza y la salida es ``(dacl, dacr)``.

El despacho es una tabla ``Op → manejador``. Añadir una instrucción es una
entrada en ``MANEJADORES``; el test-contrato comprueba que no falte ninguna.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from sofifi.domain.aritmetica import (
    DATO_FRAC,
    acc_a_dato,
    curva_suave,
    dato_a_acc,
    saturar_acc,
)
from sofifi.domain.interpolacion import tabla_hermite
from sofifi.domain.isa import (
    ADCL,
    ADCR,
    DACL,
    DACR,
    LFO_BASE,
    NUM_POTS,
    NUM_REGISTROS,
    POT_BASE,
    SW,
    Cho,
    Instruccion,
    Op,
    Programa,
    Skp,
    addr_con_signo,
)
from sofifi.domain.lfo import Lfo
from sofifi.domain.memoria import MemoriaRetardo

DESPLAZAMIENTO_MULX = 2 * DATO_FRAC - (DATO_FRAC + 16)  # f46 → f39
DESPLAZAMIENTO_SOF_D = DATO_FRAC + 16 - 15  # D en S2.15 → f39


class Nucleo:
    def __init__(self, programa: Programa) -> None:
        self.programa = programa
        self.memoria = MemoriaRetardo(programa.palabras_memoria, programa.usa_absoluta)
        self.lfos = [Lfo(c) if c is not None else None for c in programa.lfos]
        self.regs = [0] * NUM_REGISTROS
        self.acc = 0
        self.lr = 0
        self.primera = True
        self._tabla = tabla_hermite()
        self._codigo = programa.instrucciones
        # El despacho se resuelve una vez: (manejador, instrucción) por paso.
        self._pasos = [(MANEJADORES[i.op], i) for i in programa.instrucciones]

    def procesar(
        self,
        entrada_l: int,
        entrada_r: int,
        pots: Sequence[int] = (),
        sw: int = 0,
        traza: list[tuple[int, int]] | None = None,
    ) -> tuple[int, int]:
        """Procesa una muestra. Con `traza`, añade (pc siguiente, ACC) tras cada instrucción.

        La traza sirve para localizar en el silicio la primera instrucción que
        falla (scripts/hil_nucleo.py --traza; fails.md, F-15).
        """
        regs = self.regs
        regs[ADCL] = entrada_l
        regs[ADCR] = entrada_r
        for i in range(NUM_POTS):
            regs[POT_BASE + i] = pots[i] if i < len(pots) else 0
        regs[SW] = sw
        for n, lfo in enumerate(self.lfos):
            if lfo is not None:
                lfo.avanzar(regs[LFO_BASE + 2 * n])
        self.acc = 0
        self.lr = 0
        pc = 0
        pasos = self._pasos
        fin = len(pasos)
        while pc < fin:
            manejador, ins = pasos[pc]
            pc += 1 + manejador(self, ins)
            if traza is not None:
                traza.append((pc, self.acc))
        self.memoria.avanzar()
        self.primera = False
        return regs[DACL], regs[DACR]

    @property
    def a24(self) -> int:
        return acc_a_dato(self.acc)


Manejador = Callable[[Nucleo, Instruccion], int]


def _nop(n: Nucleo, i: Instruccion) -> int:
    return 0


def _rda(n: Nucleo, i: Instruccion) -> int:
    v = n.memoria.leer(i.addr)
    n.lr = v
    n.acc = saturar_acc(n.acc + v * i.coef)
    return 0


def _wra(n: Nucleo, i: Instruccion) -> int:
    a = n.a24
    n.memoria.escribir(i.addr, a)
    n.acc = saturar_acc(a * i.coef)
    return 0


def _wrap(n: Nucleo, i: Instruccion) -> int:
    a = n.a24
    n.memoria.escribir(i.addr, a)
    n.acc = saturar_acc(a * i.coef + dato_a_acc(n.lr))
    return 0


def _rdax(n: Nucleo, i: Instruccion) -> int:
    n.acc = saturar_acc(n.acc + n.regs[i.reg] * i.coef)
    return 0


def _wrax(n: Nucleo, i: Instruccion) -> int:
    a = n.a24
    n.regs[i.reg] = a
    n.acc = saturar_acc(a * i.coef)
    return 0


def _rdfx(n: Nucleo, i: Instruccion) -> int:
    r = n.regs[i.reg]
    n.acc = saturar_acc((n.a24 - r) * i.coef + dato_a_acc(r))
    return 0


def _maxx(n: Nucleo, i: Instruccion) -> int:
    n.acc = saturar_acc(max(abs(n.acc), abs(n.regs[i.reg] * i.coef)))
    return 0


def _mulx(n: Nucleo, i: Instruccion) -> int:
    n.acc = saturar_acc((n.a24 * n.regs[i.reg]) >> DESPLAZAMIENTO_MULX)
    return 0


def _sof(n: Nucleo, i: Instruccion) -> int:
    d = addr_con_signo(i.addr) << DESPLAZAMIENTO_SOF_D
    n.acc = saturar_acc(n.a24 * i.coef + d)
    return 0


def _clip(n: Nucleo, i: Instruccion) -> int:
    n.acc = dato_a_acc(curva_suave(n.a24))
    return 0


_RUN, _ZRO, _GEZ, _NEG = int(Skp.RUN), int(Skp.ZRO), int(Skp.GEZ), int(Skp.NEG)
_NA, _MEDIA = int(Cho.NA), int(Cho.MEDIA)


def _skp(n: Nucleo, i: Instruccion) -> int:
    f = i.flags  # entero: construir un IntFlag en cada muestra era lento
    condicion = (
        (f & _RUN and not n.primera)
        or (f & _ZRO and n.acc == 0)
        or (f & _GEZ and n.acc >= 0)
        or (f & _NEG and n.acc < 0)
    )
    return i.addr if condicion else 0


def _cho(n: Nucleo, i: Instruccion) -> int:
    lfo = n.lfos[i.reg]
    if lfo is None:  # el Programa lo impide; defensa en profundidad
        raise RuntimeError(f"CHO sobre LFO {i.reg} no declarado")
    media = bool(i.flags & _MEDIA)
    depth = n.regs[LFO_BASE + 2 * i.reg + 1]
    v = n.memoria.leer_interpolado(i.addr, lfo.desplazamiento_q8(depth, media), n._tabla)
    if i.flags & _NA:
        v = (v * lfo.ventana(media)) >> DATO_FRAC
    n.lr = v
    n.acc = saturar_acc(n.acc + v * i.coef)
    return 0


def _ldax(n: Nucleo, i: Instruccion) -> int:
    n.acc = dato_a_acc(n.regs[i.reg])
    return 0


def _clr(n: Nucleo, i: Instruccion) -> int:
    n.acc = 0
    return 0


def _absa(n: Nucleo, i: Instruccion) -> int:
    n.acc = saturar_acc(abs(n.acc))
    return 0


def _rdaa(n: Nucleo, i: Instruccion) -> int:
    v = n.memoria.leer_absoluta(i.addr, n.regs[i.reg])
    n.lr = v
    n.acc = saturar_acc(n.acc + v * i.coef)
    return 0


def _wraa(n: Nucleo, i: Instruccion) -> int:
    a = n.a24
    n.memoria.escribir_absoluta(i.addr, n.regs[i.reg], a)
    n.acc = saturar_acc(a * i.coef)
    return 0


MANEJADORES: dict[Op, Manejador] = {
    Op.NOP: _nop,
    Op.RDA: _rda,
    Op.WRA: _wra,
    Op.WRAP: _wrap,
    Op.RDAX: _rdax,
    Op.WRAX: _wrax,
    Op.RDFX: _rdfx,
    Op.MAXX: _maxx,
    Op.MULX: _mulx,
    Op.SOF: _sof,
    Op.CLIP: _clip,
    Op.SKP: _skp,
    Op.CHO: _cho,
    Op.LDAX: _ldax,
    Op.CLR: _clr,
    Op.ABSA: _absa,
    Op.RDAA: _rdaa,
    Op.WRAA: _wraa,
}
