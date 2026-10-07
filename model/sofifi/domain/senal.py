# SPDX-License-Identifier: MIT
"""Tipos de valor que cruzan los puertos: señales y controles. Sin I/O."""

from __future__ import annotations

from dataclasses import dataclass

from sofifi.domain.aritmetica import DATO_MAX, DATO_MIN


@dataclass(frozen=True)
class Senal:
    """Audio en dato S.23 por canal (1 o 2 canales), a ``fs_hz`` muestras/s."""

    fs_hz: int
    canales: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        if len(self.canales) not in (1, 2):
            raise ValueError(f"se esperan 1 o 2 canales, hay {len(self.canales)}")
        if len({len(c) for c in self.canales}) != 1:
            raise ValueError("los canales tienen longitudes distintas")
        for c in self.canales:
            if c and (min(c) < DATO_MIN or max(c) > DATO_MAX):
                raise ValueError("muestra fuera del rango S.23")

    @property
    def muestras(self) -> int:
        return len(self.canales[0])


@dataclass(frozen=True)
class Controles:
    """Potenciómetros (dato S.23) y tramos [inicio, fin) con el footswitch pulsado."""

    pots: tuple[int, ...] = ()
    tramos_sw: tuple[tuple[int, int], ...] = ()

    def sw_en(self, muestra: int) -> bool:
        return any(a <= muestra < b for a, b in self.tramos_sw)
