# SPDX-License-Identifier: MIT
"""Lo generado coincide con su generador: la ROM Hermite del RTL sale del modelo."""

from __future__ import annotations

from pathlib import Path

from sofifi.services.tablas import RUTA_TABLA_HERMITE, verilog_tabla_hermite

RAIZ = Path(__file__).resolve().parents[2]


def test_tabla_hermite_del_rtl_es_la_del_modelo() -> None:
    en_repo = (RAIZ / RUTA_TABLA_HERMITE).read_text(encoding="utf-8")
    assert en_repo == verilog_tabla_hermite(), "regenerar con: .venv/bin/sofifi tablas"
