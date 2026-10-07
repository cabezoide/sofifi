# SPDX-License-Identifier: MIT
"""prueba_dsp en simulación: envía primero los 25 casos extremos y todos los productos son exactos."""

from __future__ import annotations

import sys
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb_tools.runner import get_runner

from uart_rx import recibir_linea

DIVISOR = 8
AQUI = Path(__file__).resolve().parent
RTL = AQUI.parents[1] / "rtl"
sys.path.insert(0, str(AQUI.parents[1] / "scripts"))

from verificar_primitivas import (  # noqa: E402
    EXTREMOS_A,
    EXTREMOS_B,
    comprobar_dsp,
    operandos_dsp,
)


@cocotb.test()
async def extremos_y_aleatorios(dut: cocotb.handle.HierarchyObject) -> None:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    extremos = [(a, b) for a in EXTREMOS_A for b in EXTREMOS_B]
    for i in range(40):
        linea = await recibir_linea(dut.clk, dut.uart_tx, DIVISOR)
        assert linea[:2] == "D ", linea
        assert comprobar_dsp(linea[2:]) is None, linea
        if i < len(extremos):
            assert operandos_dsp(linea[2:])[:2] == extremos[i], linea


def test_prueba_dsp(tmp_path: Path) -> None:
    runner = get_runner("verilator")
    runner.build(
        sources=[
            RTL / "top" / "prueba_dsp.v",
            RTL / "primitivas" / "pll_100.v",
            RTL / "primitivas" / "mult_27x18.v",
            RTL / "comun" / "linea_hex.v",
            RTL / "comun" / "uart_tx.v",
        ],
        hdl_toplevel="prueba_dsp",
        parameters={"F_RELOJ": DIVISOR, "BAUDIOS": 1, "PAUSA": 50},
        defines={"SIMULACION": 1},
        build_dir=tmp_path,
        build_args=["-Wall"],
        always=True,
    )
    runner.test(
        hdl_toplevel="prueba_dsp", test_module="prueba_dsp_test", test_dir=AQUI, build_dir=tmp_path
    )
