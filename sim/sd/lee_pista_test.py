# SPDX-License-Identifier: MIT
"""lee_pista.v (sd_spi + lector_pista) con el modelo de tarjeta y `sofifi pista`.

Criterios de la Fase 13: las muestras salen en orden y en S.23, la pista se
repite al acabar, la cola no se queda vacía al ritmo real (una muestra cada
2 048 ciclos) y una cabecera inválida deja la salida en silencio.
"""

from __future__ import annotations

import os
import struct
import zlib
from pathlib import Path

import cocotb
import pytest
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb_tools.runner import get_runner
from sofifi.domain.pista import MAGIA, VERSION, escribir, muestra_a_dato
from tarjeta_sd import TarjetaSD, Variante

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
RTL = RAIZ / "rtl"
CICLOS_TICK = 2048  # el ritmo real: 100 MHz / 2 048 = 48 828,125 Hz

# «larga» cruza un bloque al rellenar; «corta» ocupa un bloque exacto, así que
# se repite a los 256 ticks y la vuelta se ve sin esperar minutos.
LARGA = [(-1) ** k * (k * 37 % 30000) for k in range(300)]
CORTA = [100 * k - 12800 for k in range(256)]

MOTIVOS = {"magia": 2, "version": 3, "crc": 4, "muestras": 5}


def _con_cabecera(muestras: int, magia: bytes = MAGIA, version: int = VERSION) -> bytes:
    """Imagen de CORTA con la cabecera cambiada y su CRC recalculado."""
    campos = struct.pack(">8sBI", magia, version, muestras)
    cabecera = campos + struct.pack(">I", zlib.crc32(campos))
    return cabecera.ljust(512, b"\x00") + escribir(CORTA)[512:]


IMAGENES = {
    "larga": escribir(LARGA),
    "corta": escribir(CORTA),
    "magia": _con_cabecera(len(CORTA), magia=b"OTRACOSA"),
    "version": _con_cabecera(len(CORTA), version=VERSION + 1),
    "crc": escribir(CORTA)[:13] + bytes([escribir(CORTA)[13] ^ 0x80]) + escribir(CORTA)[14:],
    "muestras": _con_cabecera(0),
}


async def arrancar(dut: cocotb.handle.HierarchyObject, caso: str) -> None:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    tarjeta = TarjetaSD(dut, IMAGENES[caso], Variante())
    cocotb.start_soon(tarjeta.correr())
    dut.rst.value, dut.tick.value = 1, 0
    await ClockCycles(dut.clk, 5)
    dut.rst.value = 0
    for _ in range(400_000):
        await RisingEdge(dut.clk)
        if int(dut.listo.value) or int(dut.error.value):
            return
    raise AssertionError("el lector no arrancó")


async def muestras_de(dut: cocotb.handle.HierarchyObject, cuantas: int) -> list[int]:
    """Da `cuantas` ticks al ritmo real y devuelve lo que sale en cada uno."""
    leidas = []
    for _ in range(cuantas):
        await ClockCycles(dut.clk, CICLOS_TICK - 1)
        dut.tick.value = 1
        await RisingEdge(dut.clk)
        dut.tick.value = 0
        await RisingEdge(dut.clk)
        leidas.append(dut.muestra.value.to_signed())
    return leidas


@cocotb.test()
async def pista_en_orden(dut: cocotb.handle.HierarchyObject) -> None:
    caso = os.environ["CASO"]
    await arrancar(dut, caso)
    if caso in MOTIVOS:
        assert int(dut.error.value) == 1, "una cabecera inválida tiene que fallar"
        assert int(dut.motivo.value) == MOTIVOS[caso]
        assert int(dut.listo.value) == 0
        leidas = await muestras_de(dut, 3)
        assert leidas == [0, 0, 0], "sin pista válida, silencio"
        return

    assert int(dut.error.value) == 0
    pista = LARGA if caso == "larga" else CORTA
    cuantas = 40 if caso == "larga" else 270  # «corta» pasa del punto de repetición
    leidas = await muestras_de(dut, cuantas)
    esperadas = [muestra_a_dato(pista[k % len(pista)]) for k in range(cuantas)]
    parejas = enumerate(zip(leidas, esperadas, strict=True))
    primero = next((k for k, (a, b) in parejas if a != b), None)
    assert leidas == esperadas, (
        f"{caso}: primera diferencia en {primero}: {leidas[max(0, (primero or 0) - 2) :][:6]} "
        f"contra {esperadas[max(0, (primero or 0) - 2) :][:6]}"
    )
    assert int(dut.vacio.value) == 0, "la cola se quedó sin datos al ritmo real"


@pytest.mark.parametrize("caso", list(IMAGENES))
def test_lee_pista(tmp_path: Path, caso: str) -> None:
    runner = get_runner("verilator")
    runner.build(
        sources=[
            RTL / "sd" / "lee_pista.v",
            RTL / "sd" / "sd_spi.v",
            RTL / "sd" / "lector_pista.v",
            RTL / "primitivas" / "bsram_pipe.v",
            RTL / "primitivas" / "bsram_bloque.v",
            RTL / "primitivas" / "registro_copia.v",
        ],
        hdl_toplevel="lee_pista",
        parameters={"DIV_LENTO": 6, "DIV_RAPIDO": 4, "INTENTOS_ACMD41": 20},
        defines={"SIMULACION": 1},
        build_dir=tmp_path,
        build_args=["-Wall"],
        always=True,
    )
    runner.test(
        hdl_toplevel="lee_pista",
        test_module="lee_pista_test",
        test_dir=AQUI,
        build_dir=tmp_path,
        extra_env={"CASO": caso},
    )
