# SPDX-License-Identifier: MIT
"""medidor_frecuencia: con dos relojes independientes, la cuenta es la esperada ± 1."""

from __future__ import annotations

from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb_tools.runner import get_runner

VENTANA = 1000
AQUI = Path(__file__).resolve().parent
RTL = AQUI.parents[1] / "rtl"


async def medir(dut: cocotb.handle.HierarchyObject) -> int:
    while True:
        await RisingEdge(dut.clk_ref)
        if int(dut.nueva.value):
            return int(dut.cuenta.value)


@cocotb.test()
async def cuenta_ciclos_del_reloj_medido(dut: cocotb.handle.HierarchyObject) -> None:
    # Referencia de 50 MHz y reloj medido de 99,9 MHz: 1 998 ciclos por ventana.
    cocotb.start_soon(Clock(dut.clk_ref, 20_000, unit="ps").start())
    cocotb.start_soon(Clock(dut.clk_medido, 10_010, unit="ps").start())
    dut.rst_ref.value = 1
    await ClockCycles(dut.clk_ref, 5)
    dut.rst_ref.value = 0
    await medir(dut)  # la primera ventana empieza a mitad del reset
    esperado = VENTANA * 20_000 / 10_010
    for _ in range(3):
        cuenta = await medir(dut)
        assert abs(cuenta - esperado) <= 1.5, f"{cuenta} ciclos, esperado {esperado:.1f}"


def test_medidor_frecuencia(tmp_path: Path) -> None:
    runner = get_runner("verilator")
    runner.build(
        sources=[RTL / "comun" / "medidor_frecuencia.v"],
        hdl_toplevel="medidor_frecuencia",
        parameters={"VENTANA": VENTANA},
        build_dir=tmp_path,
        build_args=["-Wall", "--timing"],
        always=True,
    )
    runner.test(
        hdl_toplevel="medidor_frecuencia",
        test_module="medidor_frecuencia_test",
        test_dir=AQUI,
        build_dir=tmp_path,
    )
