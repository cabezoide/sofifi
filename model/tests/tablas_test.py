# SPDX-License-Identifier: MIT
"""Lo generado coincide con su generador: la ROM Hermite del RTL sale del modelo."""

from __future__ import annotations

from pathlib import Path

from sofifi.domain.ensamblador import ensamblar
from sofifi.services.tablas import (
    PROGRAMAS_EN_ROM,
    RUTA_TABLA_HERMITE,
    ruta_programa,
    verilog_programa,
    verilog_tabla_hermite,
)

RAIZ = Path(__file__).resolve().parents[2]


def test_tabla_hermite_del_rtl_es_la_del_modelo() -> None:
    en_repo = (RAIZ / RUTA_TABLA_HERMITE).read_text(encoding="utf-8")
    assert en_repo == verilog_tabla_hermite(), "regenerar con: .venv/bin/sofifi tablas"


def test_programas_en_rom_son_los_del_ensamblador() -> None:
    for nombre in PROGRAMAS_EN_ROM:
        fuente = (RAIZ / "programas" / f"{nombre}.sasm").read_text(encoding="utf-8")
        en_repo = (RAIZ / ruta_programa(nombre)).read_text(encoding="utf-8")
        assert en_repo == verilog_programa(ensamblar(fuente, nombre)), "regenerar: sofifi tablas"
