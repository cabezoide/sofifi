# SPDX-License-Identifier: MIT
"""tabla_hermite.v: las 256 entradas son las de interpolacion.tabla_hermite()."""

from __future__ import annotations

from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from comun import RTL, construir
from sofifi.domain.interpolacion import tabla_hermite


def con_signo18(v: int) -> int:
    return v - (1 << 18) if v & (1 << 17) else v


@cocotb.test()
async def rom_igual_al_modelo(dut: cocotb.handle.HierarchyObject) -> None:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    for f, esperados in enumerate(tabla_hermite()):
        dut.frac.value = f
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        palabra = int(dut.coefs.value)
        leidos = tuple(con_signo18((palabra >> (18 * (3 - k))) & 0x3FFFF) for k in range(4))
        assert leidos == esperados, f"fracción {f}"


def test_tabla_hermite(tmp_path: Path) -> None:
    construir(tmp_path, [RTL / "nucleo" / "tabla_hermite.v"], "tabla_hermite", "tabla_hermite_test")
