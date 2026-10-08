# SPDX-License-Identifier: MIT
"""El catálogo de programas del repositorio coincide con su generador."""

from __future__ import annotations

from pathlib import Path

import pytest
from sofifi.adapters.archivos import ensamblar_archivo
from sofifi.adapters.cadenas import leer_cadenas, textos_de_programas
from sofifi.adapters.presets import leer_banco
from sofifi.domain.composicion import recursos
from sofifi.domain.ensamblador import ensamblar
from sofifi.services.catalogo import catalogos, ficha, ficha_cadena
from sofifi.services.catalogo_textos import MANDOS

RAIZ = Path(__file__).resolve().parents[2]


def test_docs_programas_es_el_del_generador() -> None:
    fichas = [
        ficha(r.stem, r.read_text(encoding="utf-8"), ensamblar_archivo(r))
        for r in sorted((RAIZ / "programas").glob("*.sasm"))
    ]
    presets = {p: len(v) for p, v in leer_banco(RAIZ / "presets" / "banco.toml").items()}
    carpeta = RAIZ / "programas"
    textos = textos_de_programas(carpeta)

    def incluir(nombre: str) -> str:
        return (carpeta / nombre).read_text(encoding="utf-8")

    cadenas = [
        ficha_cadena(c, recursos(c, textos, incluir))
        for c in leer_cadenas(RAIZ / "presets" / "cadenas.toml")
    ]
    for ruta, texto in catalogos(fichas, presets, cadenas).items():
        en_repo = (RAIZ / ruta).read_text(encoding="utf-8")
        assert en_repo == texto, f"{ruta}: regenerar con: .venv/bin/sofifi catalogo"


def test_todo_programa_tiene_resumen_en_cuatro_idiomas() -> None:
    for r in sorted((RAIZ / "programas").glob("*.sasm")):
        f = ficha(r.stem, r.read_text(encoding="utf-8"), ensamblar_archivo(r))
        assert {i for i, _ in f.resumenes} == {"en", "zh-CN", "ja"}, r.name


def test_los_mandos_tienen_traduccion() -> None:
    for r in sorted((RAIZ / "programas").glob("*.sasm")):
        f = ficha(r.stem, r.read_text(encoding="utf-8"), ensamblar_archivo(r))
        for m in f.mandos:
            assert m.split(": ", 1)[1] in MANDOS, f"{r.name}: falta «{m}» en catalogo_textos.MANDOS"


def test_la_cabecera_es_obligatoria() -> None:
    p = ensamblar("clr\n")
    with pytest.raises(ValueError, match="falta '; familia:'"):
        ficha("x", "; resumen: algo\nclr\n", p)
    with pytest.raises(ValueError, match="desconocida"):
        ficha("x", "; familia: jazz\n; resumen: algo\n", p)
    f = ficha("x", "; familia: delay\n; resumen: Eco.\n; pot0 = tiempo (corto)\n", p)
    assert f.mandos == ("0: tiempo",) and f.familia == "delay"
