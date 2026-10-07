# SPDX-License-Identifier: MIT
"""Banco de presets (``presets/banco.toml``): el mismo programa con otros mandos y un nombre.

Una tabla por programa; cada clave es el nombre del preset y su valor, la lista
de potenciómetros (pot0, pot1…) de 0 a 1. Se leen como ``Fraction`` desde su
texto, para que ``dato()`` los cuantice igual que ``--pot``.
"""

from __future__ import annotations

import tomllib
from fractions import Fraction
from pathlib import Path

Banco = dict[str, dict[str, tuple[Fraction, ...]]]


def leer_banco(ruta: Path) -> Banco:
    with ruta.open("rb") as f:
        crudo = tomllib.load(f)
    banco: Banco = {}
    for programa, presets in crudo.items():
        if not isinstance(presets, dict):
            raise ValueError(f"{ruta}: [{programa}] debe ser una tabla de presets")
        banco[programa] = {
            nombre: tuple(Fraction(str(v)) for v in valores) for nombre, valores in presets.items()
        }
    return banco
