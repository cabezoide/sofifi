# SPDX-License-Identifier: MIT
"""Configuración de las simulaciones RTL: cocotb sobre verilator (Fase 02)."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
RTL = RAIZ / "rtl"


@pytest.fixture(scope="session", autouse=True)
def _verilator_en_path() -> None:
    """El verilator de pip se instala como `verilator-cli`; cocotb busca `verilator`.

    Se pone en PATH el binario real del paquete, nunca un enlace a
    `verilator-cli`: ese envoltorio busca `verilator` en PATH y se lanzaría a sí
    mismo en bucle (bomba de procesos que tumbó la máquina el 2026-10-07).
    """
    import verilator

    raiz_verilator = Path(verilator.__file__).resolve().parent
    os.environ["VERILATOR_ROOT"] = str(raiz_verilator)
    # `.venv/bin` aporta el `python` que verilated.mk invoca sin ruta.
    rutas = [raiz_verilator / "bin", RAIZ / ".venv" / "bin"]
    os.environ["PATH"] = os.pathsep.join([*map(str, rutas), os.environ.get("PATH", "")])
    encontrado = shutil.which("verilator")
    if encontrado is None or Path(encontrado).resolve().name == "verilator-cli":
        pytest.fail("falta el `verilator` real (make install instala el paquete)")
