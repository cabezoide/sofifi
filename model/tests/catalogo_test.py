# SPDX-License-Identifier: MIT
"""El catálogo de programas del repositorio coincide con su generador."""

from __future__ import annotations

from pathlib import Path

import pytest
from sofifi.adapters.archivos import ensamblar_archivo
from sofifi.domain.ensamblador import ensamblar
from sofifi.services.catalogo import RUTA_CATALOGO, ficha, markdown

RAIZ = Path(__file__).resolve().parents[2]


def test_docs_programas_es_el_del_generador() -> None:
    fichas = [
        ficha(r.stem, r.read_text(encoding="utf-8"), ensamblar_archivo(r))
        for r in sorted((RAIZ / "programas").glob("*.sasm"))
    ]
    en_repo = (RAIZ / RUTA_CATALOGO).read_text(encoding="utf-8")
    assert en_repo == markdown(fichas), "regenerar con: .venv/bin/sofifi catalogo"


def test_la_cabecera_es_obligatoria() -> None:
    p = ensamblar("clr\n")
    with pytest.raises(ValueError, match="falta '; familia:'"):
        ficha("x", "; resumen: algo\nclr\n", p)
    with pytest.raises(ValueError, match="desconocida"):
        ficha("x", "; familia: jazz\n; resumen: algo\n", p)
    f = ficha("x", "; familia: delay\n; resumen: Eco.\n; pot0 = tiempo (corto)\n", p)
    assert f.mandos == ("0: tiempo",) and f.familia == "delay"
