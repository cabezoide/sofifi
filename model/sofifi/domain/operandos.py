# SPDX-License-Identifier: MIT
"""Operandos de cada instrucción: pasada 2 del ensamblador (ADR 0009).

Recibe el mnemónico y el texto de sus operandos, con los símbolos, los alias de
registro y las etiquetas que dejó la pasada 1, y devuelve la ``Instruccion``.
La sintaxis de cada instrucción está en el docstring de ``ensamblador.py``.
"""

from __future__ import annotations

import re
from fractions import Fraction

from sofifi.domain.aritmetica import COEF_BITS, coef, cuantizar
from sofifi.domain.expresion import ErrorEnsamblado, Expresion, entero
from sofifi.domain.isa import Cho, Instruccion, Op, Skp

_SIN_OPERANDOS = {"clip": Op.CLIP, "clr": Op.CLR, "absa": Op.ABSA, "nop": Op.NOP}
_MEMORIA_COEF = {"rda": Op.RDA, "wra": Op.WRA, "wrap": Op.WRAP}
_REGISTRO_COEF = {"rdax": Op.RDAX, "wrax": Op.WRAX, "rdfx": Op.RDFX, "maxx": Op.MAXX}
_SOLO_REGISTRO = {"mulx": Op.MULX, "ldax": Op.LDAX}
_OTRAS = {"sof": Op.SOF, "skp": Op.SKP, "cho": Op.CHO}
_ABSOLUTAS = {"rdaa": Op.RDAA, "wraa": Op.WRAA}

MNEMONICOS: dict[str, Op] = (
    _SIN_OPERANDOS | _MEMORIA_COEF | _REGISTRO_COEF | _SOLO_REGISTRO | _OTRAS | _ABSOLUTAS
)


def instruccion(
    n: int,
    mnem: str,
    ops: str,
    pc: int,
    simbolos: dict[str, Fraction],
    alias: dict[str, int],
    etiquetas: dict[str, int],
) -> Instruccion:
    args = [a.strip() for a in ops.split(",")] if ops.strip() else []
    op = MNEMONICOS[mnem]

    def esperar(k: int) -> None:
        if len(args) != k:
            raise ErrorEnsamblado(n, f"'{mnem}' espera {k} operandos, recibió {len(args)}")

    def valor(texto: str) -> Fraction:
        return Expresion(texto, simbolos, n).evaluar()

    def c(texto: str) -> int:
        try:
            return coef(valor(texto))
        except ValueError as exc:
            if isinstance(exc, ErrorEnsamblado):
                raise
            raise ErrorEnsamblado(n, str(exc)) from exc

    def reg(texto: str) -> int:
        if texto not in alias:
            raise ErrorEnsamblado(n, f"registro desconocido '{texto}'")
        return alias[texto]

    def direccion(texto: str) -> int:
        d = entero(valor(texto))
        if d < 0:
            raise ErrorEnsamblado(n, f"dirección negativa {d}")
        return d

    if op in _SIN_OPERANDOS.values():
        esperar(0)
        return Instruccion(op)
    if op in _MEMORIA_COEF.values():
        esperar(2)
        return Instruccion(op, coef=c(args[1]), addr=direccion(args[0]))
    if op in _ABSOLUTAS.values():  # rdaa|wraa reg, C [, origen]
        if len(args) not in (2, 3):
            raise ErrorEnsamblado(n, f"uso: {mnem} reg, C [, origen]")
        origen = direccion(args[2]) if len(args) == 3 else 0
        return Instruccion(op, reg=reg(args[0]), coef=c(args[1]), addr=origen)
    if op in _REGISTRO_COEF.values():
        esperar(2)
        return Instruccion(op, reg=reg(args[0]), coef=c(args[1]))
    if op in _SOLO_REGISTRO.values():
        esperar(1)
        return Instruccion(op, reg=reg(args[0]))
    if op is Op.SOF:
        esperar(2)
        try:
            d = cuantizar(valor(args[1]), 15, COEF_BITS, "D de sof")
        except ErrorEnsamblado:
            raise
        except ValueError as exc:
            raise ErrorEnsamblado(n, str(exc)) from exc
        return Instruccion(op, coef=c(args[0]), addr=d & ((1 << 18) - 1))
    if op is Op.SKP:
        esperar(2)
        flags = Skp(0)
        for f in args[0].split("|"):
            try:
                flags |= Skp[f.strip().upper()]
            except KeyError as exc:
                raise ErrorEnsamblado(n, f"condición de skp desconocida '{f}'") from exc
        destino = args[1]
        if destino in etiquetas:
            salto = etiquetas[destino] - pc - 1
            if salto < 0:
                raise ErrorEnsamblado(n, f"skp solo salta hacia delante ('{destino}' está detrás)")
        else:
            salto = entero(valor(destino))
        return Instruccion(op, flags=int(flags), addr=salto)
    # CHO
    if len(args) not in (3, 4):
        raise ErrorEnsamblado(n, "uso: cho dir, C, lfoN [, na|media]")
    m = re.fullmatch(r"(?:lfo)?([0-9])", args[2])
    if not m:
        raise ErrorEnsamblado(n, f"LFO no válido '{args[2]}'")
    banderas = Cho(0)
    if len(args) == 4:
        for f in args[3].split("|"):
            try:
                banderas |= Cho[f.strip().upper()]
            except KeyError as exc:
                raise ErrorEnsamblado(n, f"modificador de cho desconocido '{f}'") from exc
    return Instruccion(
        op, reg=int(m.group(1)), flags=int(banderas), coef=c(args[1]), addr=direccion(args[0])
    )
