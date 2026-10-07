# SPDX-License-Identifier: MIT
"""Puertos de audio y de programas: lo que el núcleo necesita del exterior."""

from __future__ import annotations

from typing import Protocol

from sofifi.domain.isa import Programa
from sofifi.domain.senal import Senal


class FuenteAudio(Protocol):
    def leer(self) -> Senal: ...


class SumideroAudio(Protocol):
    def escribir(self, senal: Senal) -> None: ...


class FuentePrograma(Protocol):
    def leer(self) -> tuple[str, str]:
        """Devuelve ``(nombre, texto)`` del programa."""
        ...


class SumideroMicrocodigo(Protocol):
    def escribir(self, programa: Programa, palabras: list[int]) -> None: ...
