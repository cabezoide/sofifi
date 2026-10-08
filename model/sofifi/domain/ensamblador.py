# SPDX-License-Identifier: MIT
"""Ensamblador de programas SOFIFI, con sintaxis tipo SpinASM (ADR 0009).

Texto → ``Programa``. Es puro: no lee ficheros. El texto llega por un puerto, y
los ficheros de ``include`` los lee la función ``incluir`` que pasa quien llama.
Las expresiones se evalúan en ``expresion.py``: exactas y nunca con ``eval``.

Sintaxis::

    ; comentario
    include  comun/bloque.sasm         ; inserta el texto de otro fichero
    equ   nombre  expr | registro      ; constante o alias de registro
    mem   nombre  expr                 ; línea de retardo de expr muestras
    lfo   N  sin|rnd|ramp  expr        ; LFO N (0..3) con excursión o ventana
    etiqueta:
    rda   dir, C        wra  dir, C        wrap dir, C
    rdax  reg, C        wrax reg, C        rdfx reg, C       maxx reg, C
    mulx  reg           ldax reg           sof  C, D
    clip | clr | absa | nop
    skp   run|zro|gez|neg, etiqueta|N
    cho   dir, C, lfoN [, na|media]
    rdaa  reg, C [, origen]          wraa reg, C [, origen]    ; región absoluta (ADR 0009)

En las direcciones, ``linea`` es el inicio (escritura), ``linea#`` el final
(retardo completo) y ``linea^`` el punto medio, como en SpinASM. ``mem x N``
reserva N+1 palabras, para que ``x#`` esté exactamente N muestras detrás de ``x``.

``include`` inserta el fichero en su sitio, como si estuviera escrito allí. Un
fichero incluido puede incluir otros; un ciclo de includes es un error. Los
errores de un fichero incluido dan su nombre y su línea.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from fractions import Fraction

from sofifi.domain.aritmetica import COEF_BITS, coef, cuantizar
from sofifi.domain.expresion import ErrorEnsamblado as ErrorEnsamblado
from sofifi.domain.expresion import Expresion, entero
from sofifi.domain.isa import (
    NOMBRES_REGISTRO,
    Cho,
    Instruccion,
    Op,
    Programa,
    Skp,
)
from sofifi.domain.lfo import NUM_LFOS, ConfigLfo, TipoLfo

Incluir = Callable[[str], str]
PROFUNDIDAD_INCLUDE = 8


@dataclass(frozen=True)
class _Mem:
    inicio: int
    longitud: int


_FV1_NO_SOPORTADAS = {
    "wlds",
    "wldr",
    "jam",
    "log",
    "exp",
    "and",
    "or",
    "xor",
    "not",
    "wrlx",
    "wrhx",
}

_SIN_OPERANDOS = {"clip": Op.CLIP, "clr": Op.CLR, "absa": Op.ABSA, "nop": Op.NOP}
_MEMORIA_COEF = {"rda": Op.RDA, "wra": Op.WRA, "wrap": Op.WRAP}
_REGISTRO_COEF = {"rdax": Op.RDAX, "wrax": Op.WRAX, "rdfx": Op.RDFX, "maxx": Op.MAXX}
_SOLO_REGISTRO = {"mulx": Op.MULX, "ldax": Op.LDAX}
_OTRAS = {"sof": Op.SOF, "skp": Op.SKP, "cho": Op.CHO}
_ABSOLUTAS = {"rdaa": Op.RDAA, "wraa": Op.WRAA}

MNEMONICOS: dict[str, Op] = (
    _SIN_OPERANDOS | _MEMORIA_COEF | _REGISTRO_COEF | _SOLO_REGISTRO | _OTRAS | _ABSOLUTAS
)


def _lineas(
    texto: str, incluir: Incluir | None, origen: str | None = None, pila: tuple[str, ...] = ()
) -> list[tuple[str | None, int, str]]:
    """Líneas útiles ``(origen, número, texto)``, con los ``include`` ya expandidos."""
    res: list[tuple[str | None, int, str]] = []
    for n, cruda in enumerate(texto.splitlines(), start=1):
        sin_comentario = cruda.split(";", 1)[0].strip()
        limpia = sin_comentario.lower()
        if not limpia:
            continue
        if limpia.split(None, 1)[0] != "include":
            res.append((origen, n, limpia))
            continue
        partes = sin_comentario.split(None, 1)
        nombre = partes[1].strip().strip('"') if len(partes) > 1 else ""
        if not nombre:
            raise ErrorEnsamblado(n, "uso: include fichero", origen)
        if incluir is None:
            raise ErrorEnsamblado(n, f"include '{nombre}' sin función para leer ficheros", origen)
        if nombre in pila or nombre == origen:
            raise ErrorEnsamblado(n, f"include en ciclo: '{nombre}'", origen)
        if len(pila) >= PROFUNDIDAD_INCLUDE:
            raise ErrorEnsamblado(n, f"más de {PROFUNDIDAD_INCLUDE} includes anidados", origen)
        try:
            incluido = incluir(nombre)
        except OSError as exc:
            raise ErrorEnsamblado(n, f"no se puede leer '{nombre}': {exc}", origen) from exc
        res.extend(_lineas(incluido, incluir, nombre, (*pila, *([origen] if origen else []))))
    return res


def _separar_etiqueta(linea: str) -> tuple[str | None, str]:
    m = re.match(r"^([a-z_][a-z0-9_]*):\s*(.*)$", linea)
    return (m.group(1), m.group(2)) if m else (None, linea)


@dataclass
class _Estado:
    """Lo que la pasada 1 acumula: símbolos, registros, etiquetas, LFOs y memoria."""

    simbolos: dict[str, Fraction] = field(default_factory=dict)
    alias: dict[str, int] = field(default_factory=lambda: dict(NOMBRES_REGISTRO))
    etiquetas: dict[str, int] = field(default_factory=dict)
    lfos: list[ConfigLfo | None] = field(default_factory=lambda: [None] * NUM_LFOS)
    memoria_usada: int = 0
    # (origen, línea, mnemónico, operandos, pc)
    cuerpo: list[tuple[str | None, int, str, str, int]] = field(default_factory=list)


def ensamblar(texto: str, nombre: str = "programa", incluir: Incluir | None = None) -> Programa:
    e = _Estado()
    # Pasada 1: directivas, etiquetas y posiciones.
    for origen, n, linea in _lineas(texto, incluir):
        try:
            _pasada_1(e, n, linea, origen)
        except ErrorEnsamblado as exc:
            raise exc.en(origen) from None
    # Pasada 2: código.
    instrucciones = []
    for origen, n, mnem, ops, pc in e.cuerpo:
        try:
            instrucciones.append(_instruccion(n, mnem, ops, pc, e.simbolos, e.alias, e.etiquetas))
        except ErrorEnsamblado as exc:
            raise exc.en(origen) from None
    try:
        return Programa(nombre, tuple(instrucciones), max(1, e.memoria_usada), tuple(e.lfos))
    except ValueError as exc:
        raise ErrorEnsamblado(0, str(exc)) from exc


def _pasada_1(e: _Estado, n: int, linea: str, origen: str | None) -> None:
    etiqueta, resto = _separar_etiqueta(linea)
    if etiqueta:
        if etiqueta in e.etiquetas:
            raise ErrorEnsamblado(n, f"etiqueta repetida '{etiqueta}'")
        e.etiquetas[etiqueta] = len(e.cuerpo)
    if not resto:
        return
    partes = resto.split(None, 1)
    mnem, ops = partes[0], (partes[1] if len(partes) > 1 else "")
    if mnem == "equ":
        campos = ops.replace(",", " ").split(None, 1)
        if len(campos) != 2:
            raise ErrorEnsamblado(n, "uso: equ nombre valor")
        nom, valor = campos
        if valor.strip() in e.alias:
            e.alias[nom] = e.alias[valor.strip()]
        else:
            e.simbolos[nom] = Expresion(valor, e.simbolos, n).evaluar()
    elif mnem == "mem":
        campos = ops.replace(",", " ").split(None, 1)
        if len(campos) != 2:
            raise ErrorEnsamblado(n, "uso: mem nombre longitud")
        nom, valor = campos
        longitud = entero(Expresion(valor, e.simbolos, n).evaluar())
        if longitud < 1:
            raise ErrorEnsamblado(n, f"longitud de memoria {longitud} < 1")
        m = _Mem(e.memoria_usada, longitud)
        e.simbolos[nom] = Fraction(m.inicio)
        e.simbolos[nom + "#"] = Fraction(m.inicio + longitud)
        e.simbolos[nom + "^"] = Fraction(m.inicio + longitud // 2)
        e.memoria_usada += longitud + 1
    elif mnem == "lfo":
        campos = ops.replace(",", " ").split()
        if len(campos) != 3 or not campos[0].isdigit():
            raise ErrorEnsamblado(n, "uso: lfo N sin|rnd|ramp excursión")
        idx = int(campos[0])
        if not 0 <= idx < NUM_LFOS:
            raise ErrorEnsamblado(n, f"LFO {idx} fuera de 0..{NUM_LFOS - 1}")
        try:
            tipo = TipoLfo(campos[1])
            excursion = entero(Expresion(campos[2], e.simbolos, n).evaluar())
            e.lfos[idx] = ConfigLfo(tipo, excursion)
        except ValueError as exc:
            if isinstance(exc, ErrorEnsamblado):
                raise
            raise ErrorEnsamblado(n, str(exc)) from exc
    elif mnem in MNEMONICOS:
        e.cuerpo.append((origen, n, mnem, ops, len(e.cuerpo)))
    elif mnem in _FV1_NO_SOPORTADAS:
        raise ErrorEnsamblado(n, f"'{mnem}' es del FV-1 y no está en la ISA SOFIFI (ADR 0009)")
    else:
        raise ErrorEnsamblado(n, f"instrucción o directiva desconocida '{mnem}'")


def _instruccion(
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
