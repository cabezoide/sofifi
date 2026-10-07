# SPDX-License-Identifier: MIT
"""El banco de presets: programas que existen, mandos que el programa usa, valores en [0, 1]."""

from __future__ import annotations

from pathlib import Path

import pytest
from sofifi.adapters.archivos import ensamblar_archivo
from sofifi.adapters.presets import leer_banco
from sofifi.domain.isa import NUM_POTS
from sofifi.services.catalogo import ficha

RAIZ = Path(__file__).resolve().parents[2]
BANCO = leer_banco(RAIZ / "presets" / "banco.toml")
PROGRAMAS = sorted(p.stem for p in (RAIZ / "programas").glob("*.sasm"))


def mandos(nombre: str) -> set[int]:
    ruta = RAIZ / "programas" / f"{nombre}.sasm"
    f = ficha(nombre, ruta.read_text(encoding="utf-8"), ensamblar_archivo(ruta))
    return {int(m.split(":")[0]) for m in f.mandos}


def test_cada_programa_tiene_al_menos_cinco_presets() -> None:
    assert sorted(BANCO) == PROGRAMAS
    assert all(len(p) >= 5 for p in BANCO.values())
    assert sum(len(p) for p in BANCO.values()) >= 300


@pytest.mark.parametrize("programa", PROGRAMAS)
def test_los_presets_usan_los_mandos_del_programa(programa: str) -> None:
    usados = mandos(programa)
    for nombre, valores in BANCO[programa].items():
        assert len(valores) <= NUM_POTS, nombre
        assert all(0 <= v <= 1 for v in valores), nombre
        for k, v in enumerate(valores):
            assert k in usados or v == 0, f"{programa}/{nombre}: pot{k} no existe y vale {v}"
        assert max(usados) < len(valores), f"{programa}/{nombre}: faltan mandos"


def test_los_valores_de_un_preset_son_distintos_entre_presets() -> None:
    for programa, presets in BANCO.items():
        vistos = list(presets.values())
        assert len(set(vistos)) == len(vistos), f"{programa}: dos presets iguales"
