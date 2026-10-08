# SPDX-License-Identifier: MIT
"""Cadenas: qué programas se unen, con qué mandos, y lo que gasta la unión (ADR 0013).

Son tipos de valor. El compositor que los convierte en un programa está en
``composicion.py``; el banco de cadenas se lee en ``adapters/cadenas.py``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction

from sofifi.domain.aritmetica import CICLOS_POR_MUESTRA
from sofifi.domain.isa import MAX_INSTRUCCIONES, NUM_POTS, NUM_REGS_GENERALES
from sofifi.domain.lfo import NUM_LFOS
from sofifi.domain.memoria import PALABRAS_ABSOLUTAS, PALABRAS_MAX


class Modo(Enum):
    SERIE = "serie"
    PARALELO = "paralelo"


@dataclass(frozen=True)
class PotFisico:
    """El mando del programa lo lleva el potenciómetro ``indice`` del pedal."""

    indice: int


Mando = Fraction | PotFisico


@dataclass(frozen=True)
class Eslabon:
    """Un programa de la cadena y sus mandos: pot0, pot1… Un mando que falta vale 0."""

    programa: str
    mandos: tuple[Mando, ...] = ()

    def mando(self, k: int) -> Mando:
        return self.mandos[k] if k < len(self.mandos) else Fraction(0)


@dataclass(frozen=True)
class Cadena:
    nombre: str
    modo: Modo
    eslabones: tuple[Eslabon, ...]
    requiere: str | None = None  # "sdram": no cabe hasta que llegue la SDRAM
    posiciones: tuple[Fraction, ...] = ()  # pots físicos al cargar la cadena, de 0 a 1

    def __post_init__(self) -> None:
        if self.requiere not in (None, "sdram"):
            raise ValueError(f"cadena '{self.nombre}': requiere '{self.requiere}' desconocido")
        if len(self.posiciones) > NUM_POTS or not all(0 <= v <= 1 for v in self.posiciones):
            raise ValueError(f"cadena '{self.nombre}': posiciones de los pots fuera de [0, 1]")
        if len(self.eslabones) < 2:
            raise ValueError(f"cadena '{self.nombre}': hacen falta dos programas o más")
        for e in self.eslabones:
            if len(e.mandos) > NUM_POTS:
                raise ValueError(f"cadena '{self.nombre}': {e.programa} tiene más de 6 mandos")
            for m in e.mandos:
                if isinstance(m, PotFisico) and not 0 <= m.indice < NUM_POTS:
                    raise ValueError(f"cadena '{self.nombre}': pot{m.indice} no existe")
                if isinstance(m, Fraction) and not 0 <= m <= 1:
                    raise ValueError(f"cadena '{self.nombre}': mando {m} fuera de [0, 1]")


@dataclass(frozen=True)
class Recursos:
    """Lo que gasta la cadena, y los límites del núcleo."""

    instrucciones: int
    ciclos: int
    memoria: int
    registros: int
    lfos: int
    absolutas: int

    def excedidos(self) -> list[str]:
        """Los recursos que no caben: "ciclos", "memoria", "registros", "lfos"…"""
        tope_memoria = PALABRAS_MAX - (PALABRAS_ABSOLUTAS if self.absolutas else 0)
        limites = {
            "instrucciones": self.instrucciones > MAX_INSTRUCCIONES,
            "ciclos": self.ciclos > CICLOS_POR_MUESTRA,
            "memoria": self.memoria > tope_memoria,
            "registros": self.registros > NUM_REGS_GENERALES,
            "lfos": self.lfos > NUM_LFOS,
            "región absoluta": self.absolutas > 1,
        }
        return [nombre for nombre, excede in limites.items() if excede]
