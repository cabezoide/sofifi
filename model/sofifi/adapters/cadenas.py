# SPDX-License-Identifier: MIT
"""Banco de cadenas (``presets/cadenas.toml``): dos o más programas como un efecto (ADR 0013).

Cada ``[[cadena]]`` tiene ``nombre``, ``modo`` (``serie`` o ``paralelo``), la
lista ``efectos`` y, si hace falta, ``requiere = "sdram"`` y ``pots`` (las
posiciones de los potenciómetros del pedal al cargarla). En ``mandos``, un
número es un valor fijo y ``"potN"`` es el potenciómetro N del pedal.
"""

from __future__ import annotations

import tomllib
from fractions import Fraction
from pathlib import Path

from sofifi.domain.cadena import Cadena, Eslabon, Mando, Modo, PotFisico
from sofifi.domain.composicion import componer


def _mando(valor: object, donde: str) -> Mando:
    if isinstance(valor, str) and valor.startswith("pot") and valor[3:].isdigit():
        return PotFisico(int(valor[3:]))
    if isinstance(valor, int | float) and not isinstance(valor, bool):
        return Fraction(str(valor))
    raise ValueError(f"{donde}: mando '{valor}' no es un número ni «potN»")


def leer_cadenas(ruta: Path) -> list[Cadena]:
    with ruta.open("rb") as f:
        crudo = tomllib.load(f)
    cadenas = []
    for c in crudo.get("cadena", []):
        donde = f"{ruta}: «{c.get('nombre', '?')}»"
        eslabones = tuple(
            Eslabon(e["programa"], tuple(_mando(m, donde) for m in e.get("mandos", [])))
            for e in c["efectos"]
        )
        cadenas.append(
            Cadena(
                c["nombre"],
                Modo(c["modo"]),
                eslabones,
                c.get("requiere"),
                tuple(Fraction(str(v)) for v in c.get("pots", [])),
            )
        )
    nombres = [c.nombre for c in cadenas]
    repetidos = {n for n in nombres if nombres.count(n) > 1}
    if repetidos:
        raise ValueError(f"{ruta}: cadenas repetidas: {sorted(repetidos)}")
    return cadenas


def textos_de_programas(carpeta: Path) -> dict[str, str]:
    return {r.stem: r.read_text(encoding="utf-8") for r in sorted(carpeta.glob("*.sasm"))}


class FuenteCadena:
    """Una cadena como ``FuentePrograma``: el render la trata como un programa más."""

    def __init__(self, cadena: Cadena, carpeta: Path) -> None:
        self.cadena = cadena
        self.carpeta = carpeta

    def leer(self) -> tuple[str, str]:
        texto = componer(self.cadena, textos_de_programas(self.carpeta), self.incluir)
        return self.cadena.nombre, texto

    def incluir(self, nombre: str) -> str:
        return (self.carpeta / nombre).read_text(encoding="utf-8")
