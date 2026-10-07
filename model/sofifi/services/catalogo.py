# SPDX-License-Identifier: MIT
"""Catálogo de programas: ``docs/programas.md`` sale de las cabeceras de los ``.sasm``.

Cada programa declara en su cabecera ``; familia: …``, ``; resumen: …`` y una
línea ``; potN = nombre (…)`` por mando. El catálogo añade lo que mide el
ensamblador: instrucciones, ciclos del RTL y memoria. ``model/tests/catalogo_test.py``
exige que el fichero del repositorio sea igual a lo que produce esta función.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from sofifi.domain.aritmetica import CICLOS_POR_MUESTRA
from sofifi.domain.coste import ciclos_rtl
from sofifi.domain.isa import Programa
from sofifi.domain.memoria import PALABRAS_MAX

RUTA_CATALOGO = "docs/programas.md"
ORDEN_FAMILIAS = ("reverb", "delay", "modulación", "pitch", "dinámica", "textura", "filtro")
_POT = re.compile(r"pot(\d)\s*=\s*([^·(]+)")


@dataclass(frozen=True)
class Ficha:
    nombre: str
    familia: str
    resumen: str
    mandos: tuple[str, ...]
    instrucciones: int
    ciclos: int
    palabras: int


def ficha(nombre: str, texto: str, programa: Programa) -> Ficha:
    cabecera = [linea[1:].strip() for linea in texto.splitlines() if linea.startswith(";")]
    campos: dict[str, str] = {}
    mandos: dict[int, str] = {}
    for linea in cabecera:
        clave, _, valor = linea.partition(":")
        if clave in ("familia", "resumen") and clave not in campos:
            campos[clave] = valor.strip()
        if linea.startswith("pot"):
            for m in _POT.finditer(linea):
                mandos.setdefault(int(m.group(1)), m.group(2).strip())
    for clave in ("familia", "resumen"):
        if clave not in campos:
            raise ValueError(f"{nombre}.sasm: falta '; {clave}:' en la cabecera")
    if campos["familia"] not in ORDEN_FAMILIAS:
        raise ValueError(f"{nombre}.sasm: familia '{campos['familia']}' desconocida")
    return Ficha(
        nombre,
        campos["familia"],
        campos["resumen"],
        tuple(f"{k}: {mandos[k]}" for k in sorted(mandos)),
        len(programa.instrucciones),
        ciclos_rtl(programa),
        programa.palabras_memoria,
    )


def _miles(n: int) -> str:
    """2048 → «2 048», como en el resto de la documentación."""
    return f"{n:,}".replace(",", " ")


def markdown(fichas: list[Ficha]) -> str:
    lineas = [
        "<!-- GENERADO por `sofifi catalogo` desde programas/*.sasm. No se edita a mano:",
        "     model/tests/catalogo_test.py lo compara con su generador. -->",
        "",
        "# Programas del núcleo",
        "",
        f"{len(fichas)} programas. Cada uno es un fichero de texto en `programas/`.",
        f"Los ciclos son la cota del RTL, de {_miles(CICLOS_POR_MUESTRA)} por muestra",
        f"(`model/sofifi/domain/coste.py`). La memoria es de {_miles(PALABRAS_MAX)} palabras.",
        "",
    ]
    for familia in ORDEN_FAMILIAS:
        grupo = sorted((f for f in fichas if f.familia == familia), key=lambda f: f.nombre)
        if not grupo:
            continue
        lineas += [
            f"## {familia.capitalize()}",
            "",
            "| Programa | Qué hace | Mandos | Instrucciones | Ciclos | Memoria |",
            "|---|---|---|---|---|---|",
        ]
        for f in grupo:
            mandos = "<br>".join(f.mandos)
            lineas.append(
                f"| `{f.nombre}` | {f.resumen} | {mandos} | {f.instrucciones} "
                f"| {_miles(f.ciclos)} | {_miles(f.palabras)} |"
            )
        lineas.append("")
    return "\n".join(lineas)
