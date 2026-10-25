# SPDX-License-Identifier: MIT
"""Utilidades de los testbenches de la salida de 1 bit: rutas y construcción.

El nombre no es `comun` para no chocar con `sim/nucleo/comun.py`: pytest mete
cada carpeta de pruebas en `sys.path`, y dos módulos con el mismo nombre se
pisan.
"""

from __future__ import annotations

import sys
from pathlib import Path

from cocotb_tools.runner import get_runner

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
RTL = RAIZ / "rtl"
sys.path.insert(0, str(RAIZ / "model"))


def construir(tmp_path: Path, fuentes: list[Path], top: str, modulo: str) -> None:
    runner = get_runner("verilator")
    runner.build(
        sources=fuentes,
        hdl_toplevel=top,
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
    )
