# SPDX-License-Identifier: MIT
"""UART RX: recibe los 256 bytes, ignora un start falso y descarta errores de trama."""

from __future__ import annotations

from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb_tools.runner import get_runner

DIVISOR = 16
AQUI = Path(__file__).resolve().parent
RTL = AQUI.parents[1] / "rtl"


async def enviar(dut: cocotb.handle.HierarchyObject, byte: int, stop: int = 1) -> None:
    for nivel in [0, *((byte >> i) & 1 for i in range(8)), stop]:
        dut.rx.value = nivel
        await ClockCycles(dut.clk, DIVISOR)
    dut.rx.value = 1
    await ClockCycles(dut.clk, DIVISOR)


@cocotb.test()
async def recibe_bytes(dut: cocotb.handle.HierarchyObject) -> None:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    recibidos: list[int] = []

    async def escuchar() -> None:
        while True:
            await RisingEdge(dut.clk)
            if int(dut.valido.value):
                recibidos.append(int(dut.dato.value))

    dut.rx.value, dut.rst.value = 1, 1
    await ClockCycles(dut.clk, 5)
    dut.rst.value = 0
    cocotb.start_soon(escuchar())
    for b in range(256):
        await enviar(dut, b)
    assert recibidos == list(range(256))

    # Start falso: un pulso a 0 más corto que medio bit no produce byte.
    dut.rx.value = 0
    await ClockCycles(dut.clk, DIVISOR // 4)
    dut.rx.value = 1
    await ClockCycles(dut.clk, 3 * DIVISOR)
    # Error de trama: stop a 0. Se descarta y el siguiente byte llega bien.
    await enviar(dut, 0x5A, stop=0)
    await ClockCycles(dut.clk, 2 * DIVISOR)
    await enviar(dut, 0xC3)
    assert recibidos[256:] == [0xC3]


def test_uart_rx(tmp_path: Path) -> None:
    runner = get_runner("verilator")
    runner.build(
        sources=[RTL / "comun" / "uart_rx.v"],
        hdl_toplevel="uart_rx",
        parameters={"DIVISOR": DIVISOR},
        build_dir=tmp_path,
        build_args=["-Wall"],
        always=True,
    )
    runner.test(
        hdl_toplevel="uart_rx", test_module="uart_rx_test", test_dir=AQUI, build_dir=tmp_path
    )
