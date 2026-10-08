# SPDX-License-Identifier: MIT
"""Reescritura de un programa ya expandido: nombres e índices de LFO (ADR 0013).

Lo usa el compositor de cadenas (``composicion.py``). Entiende la sintaxis del
ensamblador: en ``skp`` no renombra las condiciones, en ``cho`` cambia el LFO
y deja los modificadores, y en ``lfo`` cambia el índice y deja el tipo. Los
números no se tocan; todo nombre pasa por la función ``nombre``.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field

from sofifi.domain.ensamblador import ErrorEnsamblado
from sofifi.domain.isa import NOMBRES_REGISTRO

TOKEN = re.compile(
    r"(?P<num>0x[0-9a-f]+|\$[0-9a-f]+|\d+(?:\.\d*)?(?:e[+-]?\d+)?|\.\d+(?:e[+-]?\d+)?)"
    r"|(?P<nom>[a-z_][a-z0-9_]*)"
)
ETIQUETA = re.compile(r"^([a-z_][a-z0-9_]*):\s*(.*)$")
REG = re.compile(r"reg(\d+)")
POT = re.compile(r"pot(\d)")
LFO_REG = re.compile(r"lfo(\d)_(rate|depth)")
LFO_CHO = re.compile(r"(?:lfo)?(\d)")


@dataclass
class Uso:
    """Lo que usa un programa: registros generales, pots, LFOs y región absoluta."""

    regs: set[int] = field(default_factory=set)
    pots: set[int] = field(default_factory=set)
    lfos: set[int] = field(default_factory=set)
    absoluta: bool = False


def partes(linea: str) -> tuple[str | None, str, list[str]]:
    """(etiqueta, mnemónico, operandos) de una línea ya expandida."""
    m = ETIQUETA.match(linea)
    etiqueta, resto = (m.group(1), m.group(2)) if m else (None, linea)
    if not resto:
        return etiqueta, "", []
    trozos = resto.split(None, 1)
    mnem, ops = trozos[0], (trozos[1] if len(trozos) > 1 else "")
    if mnem in ("equ", "mem"):
        return etiqueta, mnem, ops.replace(",", " ").split(None, 1)
    if mnem == "lfo":
        return etiqueta, mnem, ops.replace(",", " ").split()
    return etiqueta, mnem, [a.strip() for a in ops.split(",")] if ops.strip() else []


def reescribir(
    lineas: list[str], nombre: Callable[[str], str], lfo: Callable[[int], int]
) -> list[str]:
    """Cambia cada nombre con ``nombre`` y cada índice de LFO con ``lfo``."""

    def expr(texto: str) -> str:
        return TOKEN.sub(lambda m: m.group("num") or nombre(m.group("nom")), texto)

    res = []
    for linea in lineas:
        etiqueta, mnem, args = partes(linea)
        cabeza = f"{nombre(etiqueta)}:" if etiqueta else ""
        if not mnem:
            res.append(cabeza)
            continue
        if mnem in ("equ", "mem"):
            args = [nombre(args[0]), *map(expr, args[1:])]
        elif mnem == "lfo":
            args = [str(lfo(int(args[0]))), args[1], *map(expr, args[2:])]
        elif mnem == "skp":
            args = [args[0], *map(expr, args[1:])]  # las condiciones no se renombran
        elif mnem == "cho":
            indice = LFO_CHO.fullmatch(args[2])
            if not indice:
                raise ErrorEnsamblado(0, f"LFO no válido '{args[2]}'")
            args = [expr(args[0]), expr(args[1]), f"lfo{lfo(int(indice.group(1)))}", *args[3:]]
        else:
            args = [expr(a) for a in args]
        if mnem in ("equ", "mem", "lfo"):
            res.append(f"{cabeza}{mnem}  {'  '.join(args)}")
        else:
            res.append(f"{cabeza}        {mnem}  {', '.join(args)}".rstrip())
    return res


def uso(lineas: list[str]) -> Uso:
    u = Uso()

    def ver(n: str) -> str:
        if (m := REG.fullmatch(n)) and n in NOMBRES_REGISTRO:
            u.regs.add(int(m.group(1)))
        elif (m := POT.fullmatch(n)) and n in NOMBRES_REGISTRO:
            u.pots.add(int(m.group(1)))
        elif m := LFO_REG.fullmatch(n):
            u.lfos.add(int(m.group(1)))
        return n

    def ver_lfo(k: int) -> int:
        u.lfos.add(k)
        return k

    reescribir(lineas, ver, ver_lfo)
    u.absoluta = any(partes(linea)[1] in ("rdaa", "wraa") for linea in lineas)
    return u
