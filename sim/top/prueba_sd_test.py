# SPDX-License-Identifier: MIT
"""prueba_sd_logica.v con el modelo de tarjeta: elige la revisión del PMOD TF y carga.

Usa las mismas funciones que scripts/prueba_sd.py (líneas de la UART y CRC del
microcódigo), con una UART rápida y reloj lento de SD corto.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import cocotb
import pytest
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb_tools.runner import get_runner
from sofifi.adapters.archivos import ensamblar_archivo
from sofifi.domain.banco import escribir_banco
from sofifi.domain.isa import codificar

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
RTL = RAIZ / "rtl"
sys.path.insert(0, str(RAIZ / "scripts"))
sys.path.insert(0, str(RAIZ / "sim" / "primitivas"))
sys.path.insert(0, str(RAIZ / "sim" / "sd"))

from prueba_sd import crc_microcodigo  # noqa: E402
from tarjeta_sd import TarjetaSD, Variante  # noqa: E402
from uart_rx import recibir_linea  # noqa: E402

DIVISOR = 16
PROGRAMAS = [ensamblar_archivo(RAIZ / "programas" / f"{n}.sasm") for n in ("tremolo", "plate")]
IMAGEN = escribir_banco(PROGRAMAS)


async def enviar(dut: cocotb.handle.HierarchyObject, datos: bytes) -> None:
    for byte in datos:
        for nivel in [0, *((byte >> i) & 1 for i in range(8)), 1]:
            dut.uart_rx.value = nivel
            await ClockCycles(dut.clk, DIVISOR)


async def respuesta(dut: cocotb.handle.HierarchyObject, n: int) -> dict[str, int]:
    vistas = {}
    for _ in range(n):
        t = await recibir_linea(dut.clk, dut.uart_tx, DIVISOR)
        vistas[t[0]] = int(t[2:], 16)
    return vistas


@cocotb.test()
async def elige_revision_y_carga(dut: cocotb.handle.HierarchyObject) -> None:
    revision = int(os.environ["REVISION"])
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    tarjeta = TarjetaSD(dut, IMAGEN, Variante(), lambda: int(dut.v1.value) == (revision == 1))
    cocotb.start_soon(tarjeta.correr())
    dut.rst.value, dut.uart_rx.value = 1, 1
    await ClockCycles(dut.clk, 5)
    dut.rst.value = 0
    await ClockCycles(dut.clk, 60_000)  # arranque (y reintento con la v1)
    await enviar(dut, b"S")
    estado = await respuesta(dut, 2)
    assert estado == {"M": revision, "E": 0}, estado
    for k, p in enumerate(PROGRAMAS):
        await enviar(dut, b"L" + k.to_bytes(2, "big"))
        r = await respuesta(dut, 3)
        palabras = [codificar(i) for i in p.instrucciones]
        assert r == {"I": len(palabras), "P": p.palabras_memoria, "X": crc_microcodigo(palabras)}, r
    await enviar(dut, b"L\x00\x05")  # ranura fuera del banco
    assert await respuesta(dut, 1) == {"F": 4}


@pytest.mark.parametrize("revision", [2, 1])
def test_prueba_sd(tmp_path: Path, revision: int) -> None:
    runner = get_runner("verilator")
    runner.build(
        sources=[RTL / "top" / "prueba_sd_logica.v"]
        + [RTL / "sd" / f for f in ("carga_sd.v", "sd_spi.v", "cargador.v")]
        + [RTL / "comun" / f for f in ("uart_rx.v", "uart_tx.v", "linea_hex.v")],
        hdl_toplevel="prueba_sd_logica",
        parameters={"F_RELOJ": DIVISOR, "BAUDIOS": 1, "DIV_LENTO": 6, "INTENTOS_ACMD41": 20},
        build_dir=tmp_path,
        build_args=["-Wall"],
        always=True,
    )
    runner.test(
        hdl_toplevel="prueba_sd_logica",
        test_module="prueba_sd_test",
        test_dir=AQUI,
        build_dir=tmp_path,
        extra_env={"REVISION": str(revision)},
    )
