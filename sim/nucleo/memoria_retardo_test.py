# SPDX-License-Identifier: MIT
"""memoria_retardo.v: lecturas y escrituras relativas iguales a MemoriaRetardo del modelo."""

from __future__ import annotations

import os
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, ReadOnly, RisingEdge
from comun import RTL, con_signo, construir
from sofifi.domain.memoria import MemoriaRetardo

PALABRAS_MAX = 2048


async def ciclo(dut: cocotb.handle.HierarchyObject) -> None:
    await RisingEdge(dut.clk)
    dut.we.value = 0
    dut.avanzar.value = 0


@cocotb.test()
async def igual_al_modelo(dut: cocotb.handle.HierarchyObject) -> None:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    azar = random.Random(42)
    for palabras in (1, 37, 1000, PALABRAS_MAX):
        modelo = MemoriaRetardo(palabras)
        dut.palabras.value = palabras
        dut.we.value, dut.avanzar.value, dut.dir_r.value, dut.dir_w.value = 0, 0, 0, 0
        dut.rst.value = 1
        await ClockCycles(dut.clk, 2)
        dut.rst.value = 0
        # La BSRAM no se borra con el reset: se escribe toda a cero, como el modelo.
        for a in range(palabras):
            dut.we.value, dut.dir_w.value, dut.dato_w.value = 1, a, 0
            await ciclo(dut)
        for _ in range(300):  # muestras
            for _ in range(azar.randrange(1, 6)):
                a, v = azar.randrange(-1, palabras), con_signo(azar, 24)
                dut.we.value, dut.dir_w.value, dut.dato_w.value = 1, a, v
                modelo.escribir(a, v)
                await ciclo(dut)
                a = azar.randrange(-1, palabras)
                dut.dir_r.value = a
                await ciclo(dut)
                await ClockCycles(dut.clk, int(os.environ.get("ESPERA_LECTURA", "3")))
                await ReadOnly()
                assert dut.dato_r.value.to_signed() == modelo.leer(a), f"P={palabras} a={a}"
                await FallingEdge(dut.clk)
            dut.avanzar.value = 1
            modelo.avanzar()
            await ciclo(dut)


FUENTES = [
    RTL / "nucleo" / "memoria_retardo.v",
    RTL / "nucleo" / "dato_a_memoria.v",
    RTL / "primitivas" / "bsram_pipe.v",
    RTL / "primitivas" / "bsram_bloque.v",
    RTL / "primitivas" / "registro_copia.v",
]


def test_memoria_retardo(tmp_path: Path) -> None:
    construir(
        tmp_path, FUENTES, "memoria_retardo", "memoria_retardo_test", {"PALABRAS_MAX": PALABRAS_MAX}
    )


def test_memoria_retardo_segmentada(tmp_path: Path) -> None:
    # 2 bloques en grupos de 1: bsram_pipe segmentada, lectura 4 ciclos más lenta (F-15).
    construir(
        tmp_path,
        FUENTES,
        "memoria_retardo",
        "memoria_retardo_test",
        {"PALABRAS_MAX": PALABRAS_MAX, "GRUPO": 1},
        {"ESPERA_LECTURA": "7"},
    )
