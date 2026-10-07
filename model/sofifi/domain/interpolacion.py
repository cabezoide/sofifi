# SPDX-License-Identifier: MIT
"""Tabla de interpolación Hermite (Catmull-Rom) de 4 puntos, 256 fracciones.

Se calcula con ``Fraction`` (exacta, sin coma flotante), así que es idéntica
en cualquier máquina y el RTL la carga como ROM (1 bloque de BSRAM: 256 x 4
coeficientes de 18 bit). Para la fracción ``f`` entre ``x0`` y ``x1``::

    y = c0·x[-1] + c1·x0 + c2·x1 + c3·x2
"""

from __future__ import annotations

from fractions import Fraction
from functools import cache

from sofifi.domain.aritmetica import coef

FRACCIONES = 256


def coeficientes(f: Fraction) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    f2 = f * f
    f3 = f2 * f
    return (
        (-f3 + 2 * f2 - f) / 2,
        (3 * f3 - 5 * f2 + 2) / 2,
        (-3 * f3 + 4 * f2 + f) / 2,
        (f3 - f2) / 2,
    )


@cache
def tabla_hermite() -> list[tuple[int, ...]]:
    return [
        tuple(coef(c) for c in coeficientes(Fraction(i, FRACCIONES))) for i in range(FRACCIONES)
    ]
