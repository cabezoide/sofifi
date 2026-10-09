# SPDX-License-Identifier: MIT
"""carga_sd.v (sd_spi + cargador) con el modelo de tarjeta y bancos de sofifi banco.

Criterio de la Fase 08: un banco corrupto (un bit volteado o una longitud fuera
de rango) se rechaza también en el RTL, y entonces el núcleo no se toca. Un
banco válido llega al núcleo con las mismas palabras y la misma configuración
que da el modelo (las de `sofifi tablas`).
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
from sofifi.adapters.archivos import ensamblar_archivo
from sofifi.domain.banco import BLOQUE, bloque_ranura, bytes_microcodigo, escribir_banco
from sofifi.domain.isa import Programa, codificar
from tarjeta_sd import TarjetaSD, Variante

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
RTL = RAIZ / "rtl"
PROGRAMAS = tuple(
    ensamblar_archivo(RAIZ / "programas" / f"{n}.sasm") for n in ("tremolo", "plate", "looper")
)
IMAGEN = escribir_banco(PROGRAMAS)
META = struct.Struct(">8s32sHH" + "BH" * 4 + "I")
CODIGO_LFO = {"SIN": 0, "RND": 1, "RAMP": 2}


def voltear(imagen: bytes, byte: int, bit: int = 0) -> bytes:
    datos = bytearray(imagen)
    datos[byte] ^= 1 << bit
    return bytes(datos)


def con_meta(k: int, **cambios: int) -> bytes:
    """La ranura k con campos de metadatos cambiados y el CRC recalculado."""
    inicio = BLOQUE * bloque_ranura(k)
    campos = list(META.unpack_from(IMAGEN, inicio))
    for nombre, valor in cambios.items():
        campos[{"instrucciones": 2, "palabras": 3, "tipo_lfo0": 4}[nombre]] = valor
    micro = IMAGEN[inicio + BLOQUE : inicio + BLOQUE + bytes_microcodigo(min(campos[2], 2048))]
    meta = META.pack(*campos[:-1], zlib.crc32(META.pack(*campos[:-1], 0)[:-4] + micro))
    return IMAGEN[:inicio] + meta + IMAGEN[inicio + META.size :]


def con_microcodigo(k: int, byte: int, valor: int) -> bytes:
    """Un byte del microcódigo cambiado y el CRC recalculado (el CRC sigue cuadrando)."""
    inicio = BLOQUE * bloque_ranura(k)
    datos = bytearray(IMAGEN)
    datos[inicio + BLOQUE + byte] = valor
    campos = list(META.unpack_from(datos, inicio))
    micro = bytes(datos[inicio + BLOQUE : inicio + BLOQUE + bytes_microcodigo(campos[2])])
    struct.pack_into(
        ">I",
        datos,
        inicio + META.size - 4,
        zlib.crc32(bytes(datos[inicio : inicio + META.size - 4]) + micro),
    )
    return bytes(datos)


# caso: (imagen, ranura, motivo esperado o 0 si carga)
CASOS = {
    "plate": (IMAGEN, 1, 0),
    "looper": (IMAGEN, 2, 0),
    "cabecera": (voltear(IMAGEN, 3), 0, 2),
    "crc_cabecera": (voltear(IMAGEN, 10), 0, 3),
    "ranura": (IMAGEN, 3, 4),
    "instrucciones": (con_meta(0, instrucciones=2049), 0, 5),
    "memoria": (con_meta(0, palabras=0), 0, 5),
    "lfo": (con_meta(0, tipo_lfo0=7), 0, 6),
    "bit_metadatos": (voltear(IMAGEN, BLOQUE * bloque_ranura(1) + 41), 1, 8),
    "bit_microcodigo": (voltear(IMAGEN, BLOQUE * (bloque_ranura(1) + 1) + 300, 5), 1, 8),
    "codigo": (con_microcodigo(0, 0, 0xFC), 0, 7),  # op 63 en la primera palabra
}


def esperado(p: Programa) -> tuple[list[int], int, int, int, int, int]:
    tipos = sum(CODIGO_LFO[c.tipo.name] << (2 * k) for k, c in enumerate(p.lfos) if c is not None)
    exc = sum(c.excursion << (15 * k) for k, c in enumerate(p.lfos) if c is not None)
    palabras = [codificar(i) for i in p.instrucciones]
    return palabras, len(palabras), p.palabras_memoria, tipos, exc, int(p.usa_absoluta)


@cocotb.test()
async def carga_o_rechaza(dut: cocotb.handle.HierarchyObject) -> None:
    imagen, ranura, motivo = CASOS[os.environ["CASO"]]
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    cocotb.start_soon(TarjetaSD(dut, imagen, Variante()).correr())
    dut.rst.value, dut.cargar.value, dut.ranura.value = 1, 0, 0
    await ClockCycles(dut.clk, 5)
    dut.rst.value = 0
    while not int(dut.sd_listo.value):
        await RisingEdge(dut.clk)
    dut.ranura.value, dut.cargar.value = ranura, 1
    await RisingEdge(dut.clk)
    dut.cargar.value = 0
    escritas: dict[int, int] = {}
    paro = False
    for _ in range(3_000_000):
        await RisingEdge(dut.clk)
        paro |= bool(int(dut.nucleo_rst.value))
        if int(dut.prog_we.value):
            escritas[int(dut.prog_dir.value)] = int(dut.prog_dato.value)
        if int(dut.hecho.value) or int(dut.fallo.value):
            break
    if motivo:
        assert int(dut.fallo.value), "no falla"
        assert int(dut.motivo.value) == motivo, (
            f"motivo {int(dut.motivo.value)}, se espera {motivo}"
        )
        assert not escritas and not paro, "con un banco inválido no se toca el núcleo"
        return
    assert int(dut.hecho.value), f"falla con motivo {int(dut.motivo.value)}"
    palabras, n, mem, tipos, exc, absoluta = esperado(PROGRAMAS[ranura])
    assert [escritas.get(k) for k in range(n)] == palabras
    assert int(dut.cfg_instrucciones.value) == n and int(dut.cfg_palabras.value) == mem
    assert int(dut.cfg_lfo_tipos.value) == tipos and int(dut.cfg_lfo_excursiones.value) == exc
    assert int(dut.cfg_absoluta.value) == absoluta and not int(dut.nucleo_rst.value)


@pytest.mark.parametrize("caso", list(CASOS))
def test_carga_sd(tmp_path: Path, caso: str) -> None:
    runner = get_runner("verilator")
    runner.build(
        sources=[RTL / "sd" / f for f in ("carga_sd.v", "sd_spi.v", "cargador.v")],
        hdl_toplevel="carga_sd",
        parameters={"DIV_LENTO": 6, "DIV_RAPIDO": 4, "INTENTOS_ACMD41": 20, "ESPERA_TOKEN": 50},
        build_dir=tmp_path,
        build_args=["-Wall"],
        always=True,
    )
    runner.test(
        hdl_toplevel="carga_sd",
        test_module="carga_sd_test",
        test_dir=AQUI,
        build_dir=tmp_path,
        extra_env={"CASO": caso},
    )
