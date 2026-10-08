# SPDX-License-Identifier: MIT
"""Banco de cadenas (``presets/cadenas.toml``, ADR 0013).

Cada cadena usa programas que existen y mandos válidos. Las que no llevan
``requiere`` caben hoy en el núcleo. Las que llevan ``requiere = "sdram"`` no
caben, y solo por la memoria: cuando llegue la SDRAM, son las que se abren.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from sofifi.adapters.cadenas import FuenteCadena, leer_cadenas, textos_de_programas
from sofifi.domain.aritmetica import dato
from sofifi.domain.cadena import Cadena
from sofifi.domain.composicion import ensamblar_cadena, nombre_programa, recursos
from sofifi.domain.isa import NUM_POTS
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, PROGRAMAS, impulso, pots, programa, rms, tono

RAIZ = Path(__file__).resolve().parents[2]
CADENAS = leer_cadenas(RAIZ / "presets" / "cadenas.toml")
TEXTOS = textos_de_programas(PROGRAMAS)


def incluir(nombre: str) -> str:
    return (PROGRAMAS / nombre).read_text(encoding="utf-8")


def test_el_banco_tiene_cadenas_que_caben_y_cadenas_para_la_sdram() -> None:
    assert sum(c.requiere is None for c in CADENAS) >= 10
    assert sum(c.requiere == "sdram" for c in CADENAS) >= 3
    assert len({nombre_programa(c) for c in CADENAS}) == len(CADENAS)


@pytest.mark.parametrize("cadena", CADENAS, ids=lambda c: nombre_programa(c))
def test_cada_cadena_cabe_o_solo_espera_memoria(cadena: Cadena) -> None:
    assert all(e.programa in TEXTOS for e in cadena.eslabones)
    assert len(cadena.posiciones) == NUM_POTS
    falta = recursos(cadena, TEXTOS, incluir).excedidos()
    assert falta == ([] if cadena.requiere is None else ["memoria"])


@pytest.mark.parametrize(
    "cadena", [c for c in CADENAS if c.requiere is None], ids=lambda c: nombre_programa(c)
)
def test_cada_cadena_que_cabe_suena(cadena: Cadena) -> None:
    """Ensambla, pasa un impulso y no sale de rango: es un programa más del núcleo."""
    p = ensamblar_cadena(cadena, TEXTOS, incluir)
    y = procesar(p, impulso(0.05), Controles(tuple(dato(v) for v in cadena.posiciones)))
    assert any(y.canales[0]) or any(y.canales[1])


def test_la_fuente_de_cadena_da_el_mismo_programa() -> None:
    c = CADENAS[0]
    nombre, texto = FuenteCadena(c, PROGRAMAS).leer()
    assert nombre == c.nombre and texto.startswith("; GENERADO por el compositor")


@pytest.mark.parametrize(
    "cadena", [c for c in CADENAS if c.requiere is None], ids=lambda c: nombre_programa(c)
)
def test_ninguna_cadena_salta_de_volumen(cadena: Cadena) -> None:
    """Con una nota suave y una fuerte, la cadena no suena más del doble que el plate.

    Un salto de volumen al cambiar de preset es un riesgo (SECURITY.md, fails.md F-22 y F-23).
    """
    p = ensamblar_cadena(cadena, TEXTOS, incluir)
    pots_cadena = Controles(tuple(dato(v) for v in cadena.posiciones))
    for amplitud in (0.1, 0.4):
        x = Senal(FS, (tono(196, 0.2, amplitud) + (0,) * int(0.4 * FS),))
        plate = procesar(programa("plate"), x, Controles(pots("0.5", "0.35", "0.35")))
        y = procesar(p, x, pots_cadena)
        assert rms(y.canales[0], 0, 0.6) < 2 * rms(plate.canales[0], 0, 0.6), f"amplitud {amplitud}"
