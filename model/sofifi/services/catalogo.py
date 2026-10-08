# SPDX-License-Identifier: MIT
"""Catálogo de programas: ``docs/programas.md`` sale de las cabeceras de los ``.sasm``.

Cada programa declara en su cabecera ``; familia: …``, ``; resumen: …`` y una
línea ``; potN = nombre (…)`` por mando. El catálogo añade lo que mide el
ensamblador: instrucciones, ciclos del RTL y memoria. ``model/tests/catalogo_test.py``
exige que el fichero del repositorio sea igual a lo que produce esta función.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from sofifi.domain.aritmetica import CICLOS_POR_MUESTRA
from sofifi.domain.coste import ciclos_rtl
from sofifi.domain.isa import Programa
from sofifi.domain.memoria import PALABRAS_ABSOLUTAS, PALABRAS_MAX
from sofifi.services.catalogo_textos import FAMILIAS, IDIOMAS, MANDOS, TEXTOS

RUTA_CATALOGO = "docs/programas.md"
ORDEN_FAMILIAS = tuple(FAMILIAS)
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
    resumenes: tuple[tuple[str, str], ...] = ()  # (idioma, resumen) traducidos

    def resumen_en(self, idioma: str) -> str:
        return dict(self.resumenes).get(idioma, self.resumen) if idioma != "es" else self.resumen


def ficha(nombre: str, texto: str, programa: Programa) -> Ficha:
    cabecera = [linea[1:].strip() for linea in texto.splitlines() if linea.startswith(";")]
    campos: dict[str, str] = {}
    mandos: dict[int, str] = {}
    for linea in cabecera:
        clave, _, valor = linea.partition(":")
        if clave.startswith(("familia", "resumen")) and clave not in campos:
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
        # La región absoluta (RDAA, WRAA) también es memoria del programa.
        programa.palabras_memoria + (PALABRAS_ABSOLUTAS if programa.usa_absoluta else 0),
        tuple((i, campos[f"resumen.{i}"]) for i in IDIOMAS[1:] if f"resumen.{i}" in campos),
    )


def _miles(n: int, idioma: str = "es") -> str:
    """2048 → «2 048» en español; «2,048» en los demás idiomas."""
    return f"{n:,}".replace(",", " " if idioma == "es" else ",")


def mando_traducido(m: str, idioma: str) -> str:
    """«0: mezcla» → «0: mix» en inglés; sin traducción conocida, se deja igual."""
    k, _, etiqueta = m.partition(": ")
    if idioma == "es" or etiqueta not in MANDOS:
        return m
    return f"{k}: {MANDOS[etiqueta][IDIOMAS.index(idioma) - 1]}"


def markdown(fichas: list[Ficha], presets: dict[str, int] | None = None, idioma: str = "es") -> str:
    """Catálogo en Markdown en ``idioma``; ``presets`` da cuántos presets tiene cada programa."""
    presets = presets or {}
    t = TEXTOS[idioma]
    lineas = [
        "<!-- GENERADO por `sofifi catalogo` desde programas/*.sasm. No se edita a mano:",
        "     model/tests/catalogo_test.py lo compara con su generador. -->",
        "",
        t["titulo"],
        "",
        t["total"].format(n=len(fichas), p=sum(presets.values())),
        t["coste"].format(c=_miles(CICLOS_POR_MUESTRA, idioma), m=_miles(PALABRAS_MAX, idioma)),
        "",
    ]
    for familia in ORDEN_FAMILIAS:
        grupo = sorted((f for f in fichas if f.familia == familia), key=lambda f: f.nombre)
        if not grupo:
            continue
        lineas += [
            f"## {FAMILIAS[familia][IDIOMAS.index(idioma)]}",
            "",
            t["cabecera"],
            "|---|---|---|---|---|---|---|",
        ]
        for f in grupo:
            mandos = "<br>".join(mando_traducido(m, idioma) for m in f.mandos)
            lineas.append(
                f"| `{f.nombre}` | {f.resumen_en(idioma)} | {mandos} | {presets.get(f.nombre, 0)} "
                f"| {f.instrucciones} | {_miles(f.ciclos, idioma)} | {_miles(f.palabras, idioma)} |"
            )
        lineas.append("")
    return "\n".join(lineas)


def ruta_catalogo(idioma: str) -> str:
    return RUTA_CATALOGO if idioma == "es" else RUTA_CATALOGO.replace(".md", f".{idioma}.md")


def catalogos(fichas: list[Ficha], presets: dict[str, int]) -> dict[str, str]:
    """Los cuatro catálogos, ruta → texto. Las traducciones llevan el sello i18n (ADR 0007)
    con la huella del catálogo español que se genera a la vez."""
    es = markdown(fichas, presets, "es")
    sha = hashlib.sha256(es.encode("utf-8")).hexdigest()[:12]
    res = {RUTA_CATALOGO: es}
    for idioma in IDIOMAS[1:]:
        sello = f"<!-- i18n: fuente={RUTA_CATALOGO} sha={sha} estado=al_dia -->\n"
        res[ruta_catalogo(idioma)] = sello + markdown(fichas, presets, idioma)
    return res
