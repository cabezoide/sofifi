# SPDX-License-Identifier: MIT
"""UART TX: la trama 8N1 sale con el ancho de bit exacto y el handshake respeta `listo`."""

from __future__ import annotations

from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge
from cocotb_tools.runner import get_runner

DIVISOR = 8
AQUI = Path(__file__).resolve().parent
RTL = AQUI.parents[1] / "rtl"


async def recibir(dut: cocotb.handle.HierarchyObject) -> int:
    await FallingEdge(dut.tx)  # bit de start
    await ClockCycles(dut.clk, DIVISOR // 2)
    assert int(dut.tx.value) == 0, "start debe ser 0"
    byte = 0
    for i in range(8):
        await ClockCycles(dut.clk, DIVISOR)
        byte |= int(dut.tx.value) << i
    await ClockCycles(dut.clk, DIVISOR)
    assert int(dut.tx.value) == 1, "stop debe ser 1"
    return byte


@cocotb.test()
async def envia_bytes_con_handshake(dut: cocotb.handle.HierarchyObject) -> None:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst.value = 1
    dut.valido.value = 0
    dut.dato.value = 0
    await ClockCycles(dut.clk, 3)
    dut.rst.value = 0
    await RisingEdge(dut.clk)
    assert int(dut.tx.value) == 1 and int(dut.listo.value) == 1

    mensaje = b"SOFIFI\x00\xff"
    recibidos: list[int] = []

    async def receptor() -> None:
        for _ in mensaje:
            recibidos.append(await recibir(dut))

    tarea = cocotb.start_soon(receptor())
    for b in mensaje:
        dut.dato.value = b
        dut.valido.value = 1
        await RisingEdge(dut.clk)
        while int(dut.listo.value) == 0:
            await RisingEdge(dut.clk)
        # en este flanco listo==1 y valido==1: se acepta el byte
        await RisingEdge(dut.clk)
        dut.valido.value = 0
        while int(dut.listo.value) == 0:
            await RisingEdge(dut.clk)
    await tarea
    assert bytes(recibidos) == mensaje


def test_uart_tx(tmp_path: Path) -> None:
    runner = get_runner("verilator")
    runner.build(
        sources=[RTL / "comun" / "uart_tx.v"],
        hdl_toplevel="uart_tx",
        parameters={"DIVISOR": DIVISOR},
        build_dir=tmp_path,
        build_args=["-Wall"],
        always=True,
    )
    runner.test(
        hdl_toplevel="uart_tx", test_module="uart_tx_test", test_dir=AQUI, build_dir=tmp_path
    )
