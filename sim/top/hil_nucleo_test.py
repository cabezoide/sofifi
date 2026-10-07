# SPDX-License-Identifier: MIT
"""hil_nucleo.v en simulación: tras 'C', captura y vuelca; scripts/hil_nucleo.py lo aprueba.

Usa las mismas funciones que el script del PC (estímulo, CRC-32, comparación con
el modelo), con una captura corta y una UART rápida.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb_tools.runner import get_runner

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
RTL = RAIZ / "rtl"
sys.path.insert(0, str(RAIZ / "scripts"))
sys.path.insert(0, str(RAIZ / "sim" / "primitivas"))

from hil_nucleo import comprobar  # noqa: E402
from uart_rx import recibir_linea  # noqa: E402

DIVISOR = 16
N_CAPTURA = 1024  # bsram_pipe trabaja con bloques de 1 024


async def enviar_byte(dut: cocotb.handle.HierarchyObject, byte: int) -> None:
    for nivel in [0, *((byte >> i) & 1 for i in range(8)), 1]:
        dut.uart_rx.value = nivel
        await ClockCycles(dut.clk, DIVISOR)


@cocotb.test()
async def captura_igual_al_modelo(dut: cocotb.handle.HierarchyObject) -> None:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst_n.value, dut.uart_rx.value = 1, 1
    await ClockCycles(dut.clk, 200)  # carga del programa
    await enviar_byte(dut, ord("C"))
    lineas: list[str] = []
    while not lineas or not lineas[-1].startswith("Z "):
        lineas.append(await recibir_linea(dut.clk, dut.uart_tx, DIVISOR))
    r = comprobar(lineas, N_CAPTURA)
    dut._log.info(
        "%d muestras, %d iguales, CRC %s, %s ciclos", r.muestras, r.iguales, r.crc_ok, r.ciclos
    )
    assert r.correcto and r.muestras == N_CAPTURA, r.primera_diferencia or "CRC incorrecto"


def test_hil_nucleo(tmp_path: Path) -> None:
    fuentes = []
    for linea in (RTL / "top" / "tops.txt").read_text().splitlines():
        campos = linea.split()
        if campos and campos[0] == "hil_nucleo":
            fuentes = [RAIZ / f for f in campos[1:]]
    runner = get_runner("verilator")
    runner.build(
        sources=fuentes,
        hdl_toplevel="hil_nucleo",
        parameters={"F_RELOJ": DIVISOR, "BAUDIOS": 1, "N_CAPTURA": N_CAPTURA},
        defines={"SIMULACION": 1},
        build_dir=tmp_path,
        build_args=["-Wall"],
        always=True,
    )
    runner.test(
        hdl_toplevel="hil_nucleo", test_module="hil_nucleo_test", test_dir=AQUI, build_dir=tmp_path
    )
