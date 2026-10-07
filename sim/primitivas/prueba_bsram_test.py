# SPDX-License-Identifier: MIT
"""prueba_bsram en simulación: con una memoria pequeña, las tres pasadas dan 0 errores."""

from __future__ import annotations

from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb_tools.runner import get_runner
from uart_rx import recibir_linea

DIVISOR = 8
AQUI = Path(__file__).resolve().parent
RTL = AQUI.parents[1] / "rtl"


@cocotb.test()
async def tres_pasadas_sin_errores(dut: cocotb.handle.HierarchyObject) -> None:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    for vuelta in range(3):
        linea = await recibir_linea(dut.clk, dut.uart_tx, DIVISOR)
        assert linea[:2] == "B ", linea
        campos = [int(linea[2 + i : 6 + i], 16) for i in range(0, 20, 4)]
        assert campos[:4] == [0, 0, 0, 0], f"errores en la vuelta {vuelta}: {linea}"
        assert campos[4] == 2 * vuelta + 1  # un informe cada 2 vueltas


def test_prueba_bsram(tmp_path: Path) -> None:
    runner = get_runner("verilator")
    runner.build(
        sources=[
            RTL / "top" / "prueba_bsram.v",
            RTL / "primitivas" / "pll_100.v",
            RTL / "primitivas" / "bsram_dp.v",
            RTL / "comun" / "linea_hex.v",
            RTL / "comun" / "uart_tx.v",
        ],
        hdl_toplevel="prueba_bsram",
        parameters={"F_RELOJ": DIVISOR, "BAUDIOS": 1, "PALABRAS": 48, "VUELTAS": 2},
        defines={"SIMULACION": 1},
        build_dir=tmp_path,
        build_args=["-Wall"],
        always=True,
    )
    runner.test(
        hdl_toplevel="prueba_bsram",
        test_module="prueba_bsram_test",
        test_dir=AQUI,
        build_dir=tmp_path,
    )
