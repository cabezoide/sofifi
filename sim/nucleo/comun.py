# SPDX-License-Identifier: MIT
"""Utilidades de los testbenches del núcleo: rutas, construcción y valores aleatorios."""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Any

from cocotb_tools.runner import get_runner

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
RTL = RAIZ / "rtl"
sys.path.insert(0, str(RAIZ / "model"))


def construir(
    tmp_path: Path,
    fuentes: list[Path],
    top: str,
    modulo: str,
    parametros: dict[str, Any] | None = None,
    entorno: dict[str, str] | None = None,
) -> None:
    runner = get_runner("verilator")
    runner.build(
        sources=fuentes,
        hdl_toplevel=top,
        parameters=parametros or {},
        defines={"SIMULACION": 1},
        build_dir=tmp_path,
        build_args=["-Wall"],
        always=True,
    )
    runner.test(
        hdl_toplevel=top,
        test_module=modulo,
        test_dir=AQUI,
        build_dir=tmp_path,
        extra_env=entorno or {},
    )


def con_signo(azar: random.Random, bits: int) -> int:
    """Entero con signo de `bits` bit; 1 de cada 8 veces, un extremo del rango."""
    extremos = (-(1 << (bits - 1)), (1 << (bits - 1)) - 1, -1, 0, 1)
    if azar.random() < 0.125:
        return azar.choice(extremos)
    return azar.randrange(-(1 << (bits - 1)), 1 << (bits - 1))
