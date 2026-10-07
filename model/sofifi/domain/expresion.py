# SPDX-License-Identifier: MIT
"""Errores y expresiones del ensamblador (ADR 0009).

Las expresiones se evalúan con ``Fraction`` (exactas) y un analizador de descenso
recursivo sobre ``+ - * / ( )``: nunca con ``eval``.
"""

from __future__ import annotations

import re
from fractions import Fraction


class ErrorEnsamblado(ValueError):
    def __init__(self, linea: int, mensaje: str, origen: str | None = None) -> None:
        donde = f"{origen}, línea {linea}" if origen else f"línea {linea}"
        super().__init__(f"{donde}: {mensaje}")
        self.linea = linea
        self.origen = origen
        self.mensaje = mensaje

    def en(self, origen: str | None) -> ErrorEnsamblado:
        """El mismo error, situado en el fichero ``origen`` (None: el programa)."""
        return ErrorEnsamblado(self.linea, self.mensaje, origen)


_TOKEN = re.compile(
    r"\s*(?:(?P<num>0x[0-9a-f]+|\$[0-9a-f]+|\d+(?:\.\d*)?(?:e[+-]?\d+)?|\.\d+(?:e[+-]?\d+)?)"
    r"|(?P<nom>[a-z_][a-z0-9_]*[#^]?)|(?P<op>[-+*/()]))"
)


class Expresion:
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


def entero(v: Fraction) -> int:
    """Redondeo al entero más cercano (half up), exacto."""
    return (v.numerator * 2 + v.denominator) // (2 * v.denominator)
