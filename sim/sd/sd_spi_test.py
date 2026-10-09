# SPDX-License-Identifier: MIT
"""sd_spi.v contra el modelo de tarjeta: arranque, lectura de bloques y errores."""

from __future__ import annotations

import os
from pathlib import Path

import cocotb
import pytest
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb_tools.runner import get_runner
from tarjeta_sd import TarjetaSD, Variante

AQUI = Path(__file__).resolve().parent
RTL = AQUI.parents[1] / "rtl"
IMAGEN = bytes((7 * k + k // 512) & 0xFF for k in range(512 * 40))
VARIANTES = {
    "sdhc": Variante(),
    "sdsc": Variante(sdhc=False),
    "version1": Variante(version1=True),
    "nunca_lista": Variante(ocupada=-1),
    "token_malo": Variante(token_malo=True),
}
ERRORES = {"version1": 2, "nunca_lista": 3, "token_malo": 6}


async def arrancar(dut: cocotb.handle.HierarchyObject) -> TarjetaSD:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    tarjeta = TarjetaSD(dut, IMAGEN, VARIANTES[os.environ["VARIANTE"]])
    cocotb.start_soon(tarjeta.correr())
    dut.rst.value, dut.leer.value, dut.bloque.value = 1, 0, 0
    await ClockCycles(dut.clk, 5)
    dut.rst.value = 0
    for _ in range(400_000):
        await RisingEdge(dut.clk)
        if int(dut.listo.value) or int(dut.error.value):
            break
    return tarjeta


RECIBIDOS: list[int] = []


async def espiar(dut: cocotb.handle.HierarchyObject) -> None:
    while True:
        await RisingEdge(dut.clk)
        if int(dut.byte_hecho.value):
            await RisingEdge(dut.clk)
            RECIBIDOS.append(int(dut.rx.value))


async def leer_bloque(dut: cocotb.handle.HierarchyObject, n: int) -> bytes:
    RECIBIDOS.clear()
    cocotb.start_soon(espiar(dut))
    dut.bloque.value, dut.leer.value = n, 1
    await RisingEdge(dut.clk)
    dut.leer.value = 0
    datos = bytearray()
    for _ in range(200_000):
        await RisingEdge(dut.clk)
        if int(dut.dato_v.value):
            datos.append(int(dut.dato.value))
        if int(dut.fin.value) or int(dut.error.value):
            break
    return bytes(datos)


@cocotb.test()
async def arranca_y_lee(dut: cocotb.handle.HierarchyObject) -> None:
    variante = os.environ["VARIANTE"]
    tarjeta = await arrancar(dut)
    if variante in ERRORES and variante != "token_malo":
        assert int(dut.error.value) and int(dut.codigo.value) == ERRORES[variante]
        assert not int(dut.listo.value)
        return
    assert int(dut.listo.value), f"no arranca: código {int(dut.codigo.value)}"
    for n in (0, 29, 1, 39):
        datos = await leer_bloque(dut, n)
        if variante == "token_malo":
            assert int(dut.error.value) and int(dut.codigo.value) == 6
            return
        assert datos == IMAGEN[512 * n : 512 * n + 512], (
            f"bloque {n}: {len(datos)} bytes, error {int(dut.error.value)}, código {int(dut.codigo.value)}"
            f", recibidos {[hex(b) for b in RECIBIDOS[:20]]}, rx {int(dut.rx.value):02x}, r1 {int(dut.r1.value):02x}, lecturas {tarjeta.lecturas}"
        )
        assert int(dut.fin.value) or not int(dut.ocupado.value)
    assert tarjeta.lecturas == [0, 29, 1, 39]


@pytest.mark.parametrize("variante", list(VARIANTES))
def test_sd_spi(tmp_path: Path, variante: str) -> None:
    runner = get_runner("verilator")
    runner.build(
        sources=[RTL / "sd" / "sd_spi.v"],
        hdl_toplevel="sd_spi",
        parameters={"DIV_LENTO": 6, "DIV_RAPIDO": 4, "INTENTOS_ACMD41": 20, "ESPERA_TOKEN": 50},
        build_dir=tmp_path,
        build_args=["-Wall"],
        always=True,
    )
    runner.test(
        hdl_toplevel="sd_spi",
        test_module="sd_spi_test",
        test_dir=AQUI,
        build_dir=tmp_path,
        extra_env={"VARIANTE": variante},
    )
