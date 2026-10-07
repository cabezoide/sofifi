# SPDX-License-Identifier: MIT
"""Ensamblador de programas SOFIFI, con sintaxis tipo SpinASM (ADR 0009).

Texto → ``Programa``. Es puro: no lee ficheros; el texto llega por un puerto.
Las expresiones se evalúan con ``Fraction`` (exactas) y un analizador propio:
nunca con ``eval``.

Sintaxis::

    ; comentario
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

En las direcciones, ``linea`` es el inicio (escritura), ``linea#`` el final
(retardo completo) y ``linea^`` el punto medio, como en SpinASM. ``mem x N``
reserva N+1 palabras, para que ``x#`` esté exactamente N muestras detrás de ``x``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from fractions import Fraction

from sofifi.domain.aritmetica import COEF_BITS, coef, cuantizar
from sofifi.domain.isa import (
    NOMBRES_REGISTRO,
    Cho,
    Instruccion,
    Op,
    Programa,
    Skp,
)
from sofifi.domain.lfo import NUM_LFOS, ConfigLfo, TipoLfo


class ErrorEnsamblado(ValueError):
    def __init__(self, linea: int, mensaje: str) -> None:
        super().__init__(f"línea {linea}: {mensaje}")
        self.linea = linea


@dataclass(frozen=True)
class _Mem:
    inicio: int
    longitud: int


_TOKEN = re.compile(
    r"\s*(?:(?P<num>0x[0-9a-f]+|\$[0-9a-f]+|\d+(?:\.\d*)?(?:e[+-]?\d+)?|\.\d+(?:e[+-]?\d+)?)"
    r"|(?P<nom>[a-z_][a-z0-9_]*[#^]?)|(?P<op>[-+*/()]))"
)

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

MNEMONICOS: dict[str, Op] = (
    _SIN_OPERANDOS | _MEMORIA_COEF | _REGISTRO_COEF | _SOLO_REGISTRO | _OTRAS
)


class _Expresion:
    """Descenso recursivo sobre + - * / ( ) con Fraction."""

    def __init__(self, texto: str, simbolos: dict[str, Fraction], linea: int) -> None:
        self.linea = linea
        self.simbolos = simbolos
        self.tokens: list[tuple[str, str]] = []
        pos = 0
        texto = texto.strip()
        while pos < len(texto):
            m = _TOKEN.match(texto, pos)
            if not m or m.end() == pos:
                raise ErrorEnsamblado(linea, f"expresión no válida cerca de '{texto[pos:]}'")
            tipo = m.lastgroup or ""
            self.tokens.append((tipo, m.group(tipo)))
            pos = m.end()
        self.i = 0

    def evaluar(self) -> Fraction:
        if not self.tokens:
            raise ErrorEnsamblado(self.linea, "falta un operando")
        v = self._suma()
        if self.i != len(self.tokens):
            raise ErrorEnsamblado(self.linea, f"sobra '{self.tokens[self.i][1]}' en la expresión")
        return v

    def _ver(self) -> str | None:
        return self.tokens[self.i][1] if self.i < len(self.tokens) else None

    def _suma(self) -> Fraction:
        v = self._producto()
        while self._ver() in ("+", "-"):
            op = self.tokens[self.i][1]
            self.i += 1
            w = self._producto()
            v = v + w if op == "+" else v - w
        return v

    def _producto(self) -> Fraction:
        v = self._unario()
        while self._ver() in ("*", "/"):
            op = self.tokens[self.i][1]
            self.i += 1
            w = self._unario()
            if op == "/" and w == 0:
                raise ErrorEnsamblado(self.linea, "división por cero")
            v = v * w if op == "*" else v / w
        return v

    def _unario(self) -> Fraction:
        if self._ver() == "-":
            self.i += 1
            return -self._unario()
        if self._ver() == "+":
            self.i += 1
            return self._unario()
        return self._atomo()

    def _atomo(self) -> Fraction:
        if self.i >= len(self.tokens):
            raise ErrorEnsamblado(self.linea, "expresión incompleta")
        tipo, valor = self.tokens[self.i]
        self.i += 1
        if valor == "(":
            v = self._suma()
            if self._ver() != ")":
                raise ErrorEnsamblado(self.linea, "falta ')'")
            self.i += 1
            return v
        if tipo == "num":
            if valor.startswith(("0x", "$")):
                return Fraction(int(valor.lstrip("$").removeprefix("0x"), 16))
            return Fraction(valor)
        if tipo == "nom":
            if valor not in self.simbolos:
                raise ErrorEnsamblado(self.linea, f"símbolo desconocido '{valor}'")
            return self.simbolos[valor]
        raise ErrorEnsamblado(self.linea, f"token inesperado '{valor}'")


def _entero(v: Fraction) -> int:
    """Redondeo al entero más cercano (half up), exacto."""
    return (v.numerator * 2 + v.denominator) // (2 * v.denominator)


def _lineas(texto: str) -> list[tuple[int, str]]:
    res = []
    for n, cruda in enumerate(texto.splitlines(), start=1):
        limpia = cruda.split(";", 1)[0].strip().lower()
        if limpia:
            res.append((n, limpia))
    return res


def _separar_etiqueta(linea: str) -> tuple[str | None, str]:
    m = re.match(r"^([a-z_][a-z0-9_]*):\s*(.*)$", linea)
    return (m.group(1), m.group(2)) if m else (None, linea)


def ensamblar(texto: str, nombre: str = "programa") -> Programa:
    simbolos: dict[str, Fraction] = {}
    alias: dict[str, int] = dict(NOMBRES_REGISTRO)
    etiquetas: dict[str, int] = {}
    lfos: list[ConfigLfo | None] = [None] * NUM_LFOS
    memoria_usada = 0
    cuerpo: list[tuple[int, str, str, int]] = []  # (línea, mnemónico, operandos, pc)

    # Pasada 1: directivas, etiquetas y posiciones.
    for n, linea in _lineas(texto):
        etiqueta, resto = _separar_etiqueta(linea)
        if etiqueta:
            if etiqueta in etiquetas:
                raise ErrorEnsamblado(n, f"etiqueta repetida '{etiqueta}'")
            etiquetas[etiqueta] = len(cuerpo)
        if not resto:
            continue
        partes = resto.split(None, 1)
        mnem, ops = partes[0], (partes[1] if len(partes) > 1 else "")
        if mnem == "equ":
            campos = ops.replace(",", " ").split(None, 1)
            if len(campos) != 2:
                raise ErrorEnsamblado(n, "uso: equ nombre valor")
            nom, valor = campos
            if valor.strip() in alias:
                alias[nom] = alias[valor.strip()]
            else:
                simbolos[nom] = _Expresion(valor, simbolos, n).evaluar()
        elif mnem == "mem":
            campos = ops.replace(",", " ").split(None, 1)
            if len(campos) != 2:
                raise ErrorEnsamblado(n, "uso: mem nombre longitud")
            nom, valor = campos
            longitud = _entero(_Expresion(valor, simbolos, n).evaluar())
            if longitud < 1:
                raise ErrorEnsamblado(n, f"longitud de memoria {longitud} < 1")
            m = _Mem(memoria_usada, longitud)
            simbolos[nom] = Fraction(m.inicio)
            simbolos[nom + "#"] = Fraction(m.inicio + longitud)
            simbolos[nom + "^"] = Fraction(m.inicio + longitud // 2)
            memoria_usada += longitud + 1
        elif mnem == "lfo":
            campos = ops.replace(",", " ").split()
            if len(campos) != 3 or not campos[0].isdigit():
                raise ErrorEnsamblado(n, "uso: lfo N sin|rnd|ramp excursión")
            idx = int(campos[0])
            if not 0 <= idx < NUM_LFOS:
                raise ErrorEnsamblado(n, f"LFO {idx} fuera de 0..{NUM_LFOS - 1}")
            try:
                tipo = TipoLfo(campos[1])
                lfos[idx] = ConfigLfo(tipo, _entero(_Expresion(campos[2], simbolos, n).evaluar()))
            except ValueError as exc:
                raise ErrorEnsamblado(n, str(exc)) from exc
        elif mnem in MNEMONICOS:
            cuerpo.append((n, mnem, ops, len(cuerpo)))
        elif mnem in _FV1_NO_SOPORTADAS:
            raise ErrorEnsamblado(n, f"'{mnem}' es del FV-1 y no está en la ISA SOFIFI (ADR 0009)")
        else:
            raise ErrorEnsamblado(n, f"instrucción o directiva desconocida '{mnem}'")

    # Pasada 2: código.
    instrucciones = [
        _instruccion(n, mnem, ops, pc, simbolos, alias, etiquetas) for n, mnem, ops, pc in cuerpo
    ]
    try:
        return Programa(nombre, tuple(instrucciones), max(1, memoria_usada), tuple(lfos))
    except ValueError as exc:
        raise ErrorEnsamblado(0, str(exc)) from exc


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
        return _Expresion(texto, simbolos, n).evaluar()

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
        d = _entero(valor(texto))
        if d < 0:
            raise ErrorEnsamblado(n, f"dirección negativa {d}")
        return d

    if op in _SIN_OPERANDOS.values():
        esperar(0)
        return Instruccion(op)
    if op in _MEMORIA_COEF.values():
        esperar(2)
        return Instruccion(op, coef=c(args[1]), addr=direccion(args[0]))
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
            salto = _entero(valor(destino))
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
