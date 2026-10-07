# SPDX-License-Identifier: MIT
"""Receptor UART 8N1 para los testbenches cocotb: decodifica lo que envía `tx`."""

from __future__ import annotations

from typing import Any

from cocotb.triggers import ClockCycles, FallingEdge


async def recibir_byte(clk: Any, tx: Any, divisor: int) -> int:
    await FallingEdge(tx)  # bit de start
    await ClockCycles(clk, divisor // 2)
    assert int(tx.value) == 0, "start debe ser 0"
    byte = 0
    for i in range(8):
        await ClockCycles(clk, divisor)
        byte |= int(tx.value) << i
    await ClockCycles(clk, divisor)
    assert int(tx.value) == 1, "stop debe ser 1"
    return byte


async def recibir_linea(clk: Any, tx: Any, divisor: int) -> str:
    """Devuelve la línea sin el CR LF final."""
    texto = bytearray()
    while not texto.endswith(b"\r\n"):
        texto.append(await recibir_byte(clk, tx, divisor))
    return texto[:-2].decode("ascii")
