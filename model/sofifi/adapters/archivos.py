# SPDX-License-Identifier: MIT
"""Adaptadores de fichero para programas y microcódigo."""

from __future__ import annotations

import json
from pathlib import Path

from sofifi.domain.ensamblador import ensamblar
from sofifi.domain.isa import BITS_PALABRA, Programa

DIGITOS_HEX = (BITS_PALABRA + 3) // 4


class FuenteProgramaArchivo:
    def __init__(self, ruta: Path) -> None:
        self.ruta = ruta

    def leer(self) -> tuple[str, str]:
        return self.ruta.stem, self.ruta.read_text(encoding="utf-8")

    def incluir(self, nombre: str) -> str:
        """Los ``include`` se resuelven desde la carpeta del programa."""
        return (self.ruta.parent / nombre).read_text(encoding="utf-8")


def ensamblar_archivo(ruta: Path) -> Programa:
    """Ensambla un ``.sasm`` del disco, con sus ``include``."""
    fuente = FuenteProgramaArchivo(ruta)
    nombre, texto = fuente.leer()
    return ensamblar(texto, nombre, fuente.incluir)


class SumideroHex:
    """``<base>.hex``: una palabra de 54 bit por línea (formato ``$readmemh``).

    ``<base>.json``: memoria, LFOs, instrucciones y ciclos, para la CPU que carga el núcleo.
    """

    def __init__(self, base: Path) -> None:
        self.base = base

    def escribir(self, programa: Programa, palabras: list[int]) -> None:
        self.base.parent.mkdir(parents=True, exist_ok=True)
        hex_ = "".join(f"{p:0{DIGITOS_HEX}x}\n" for p in palabras)
        self.base.with_suffix(".hex").write_text(hex_, encoding="utf-8")
        meta = {
            "nombre": programa.nombre,
            "bits_palabra": BITS_PALABRA,
            "instrucciones": len(palabras),
            "ciclos": programa.ciclos,
            "palabras_memoria": programa.palabras_memoria,
            "lfos": [
                None if c is None else {"tipo": c.tipo.value, "excursion": c.excursion}
                for c in programa.lfos
            ],
        }
        texto = json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        self.base.with_suffix(".json").write_text(texto, encoding="utf-8")
