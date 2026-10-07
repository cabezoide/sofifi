# SPDX-License-Identifier: MIT
"""mult_27x36: productos 24 × 18 y 24 × 24 con signo, exactos, con latencia 3."""

from __future__ import annotations

import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from comun import RTL, con_signo, construir


@cocotb.test()
async def producto_y_latencia(dut: cocotb.handle.HierarchyObject) -> None:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    azar = random.Random(36)
    pares = [(con_signo(azar, 25), con_signo(azar, azar.choice((18, 24, 36)))) for _ in range(3000)]
    enviados: list[int] = []
    for a, b in [*pares, (0, 0), (0, 0), (0, 0)]:
        dut.a.value, dut.b.value = a, b
        await RisingEdge(dut.clk)
        enviados.append(a * b)
        if len(enviados) > 3:
            assert dut.p.value.to_signed() == enviados[-4]


def test_mult_27x36(tmp_path: Path) -> None:
    construir(tmp_path, [RTL / "primitivas" / "mult_27x36.v"], "mult_27x36", "mult_27x36_test")
