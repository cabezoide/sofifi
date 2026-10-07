# SPDX-License-Identifier: MIT
"""mult_27x18: producto con signo exacto y latencia de 2 ciclos (modelo de simulación)."""

from __future__ import annotations

import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb_tools.runner import get_runner

AQUI = Path(__file__).resolve().parent
RTL = AQUI.parents[1] / "rtl"
EXTREMOS_A = (0, 1, -1, (1 << 26) - 1, -(1 << 26))
EXTREMOS_B = (0, 1, -1, (1 << 17) - 1, -(1 << 17))


@cocotb.test()
async def producto_y_latencia(dut: cocotb.handle.HierarchyObject) -> None:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.ce.value = 1
    azar = random.Random(2026)
    pares = [(a, b) for a in EXTREMOS_A for b in EXTREMOS_B]
    pares += [
        (azar.randrange(-(1 << 26), 1 << 26), azar.randrange(-(1 << 17), 1 << 17))
        for _ in range(500)
    ]
    enviados: list[int] = []
    for a, b in [*pares, (0, 0), (0, 0)]:
        dut.a.value = a
        dut.b.value = b
        await RisingEdge(dut.clk)
        enviados.append(a * b)
        if len(enviados) > 2:
            # El producto de hace 2 flancos ya está en la salida.
            assert dut.p.value.to_signed() == enviados[-3]


def test_mult_27x18(tmp_path: Path) -> None:
    runner = get_runner("verilator")
    runner.build(
        sources=[RTL / "primitivas" / "mult_27x18.v"],
        hdl_toplevel="mult_27x18",
        defines={"SIMULACION": 1},
        build_dir=tmp_path,
        build_args=["-Wall"],
        always=True,
    )
    runner.test(
        hdl_toplevel="mult_27x18", test_module="mult_27x18_test", test_dir=AQUI, build_dir=tmp_path
    )
