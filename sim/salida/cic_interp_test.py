# SPDX-License-Identifier: MIT
"""cic_interp.v: da los mismos 32 valores por muestra que InterpoladorCIC.

El RTL reparte el trabajo en ciclos distintos del modelo, así que su flujo va
retrasado. El retardo es fijo: el valor `k` de la muestra aparece en el ciclo
``DESPLAZAMIENTO + 64·k`` después del `tick`, y se mantiene 64 ciclos.
"""

from __future__ import annotations

import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, Timer
from comun_salida import RTL, construir
from sofifi.domain.aritmetica import CICLOS_POR_MUESTRA
from sofifi.domain.salida_1bit import (
    INTERPOLACION,
    LIMITE,
    MANTENIMIENTO,
    InterpoladorCIC,
)

MUESTRAS = 6
DESPLAZAMIENTO = 4  # ciclos desde el tick hasta el primer valor válido


@cocotb.test()
async def igual_al_modelo(dut: cocotb.handle.HierarchyObject) -> None:
    azar = random.Random(21)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst.value, dut.tick.value, dut.muestra.value = 1, 0, 0
    await ClockCycles(dut.clk, 3)
    dut.rst.value = 0
    await RisingEdge(dut.clk)

    modelo = InterpoladorCIC()
    for indice in range(MUESTRAS):
        muestra = azar.randrange(-LIMITE, LIMITE + 1)
        esperados = modelo.muestra(muestra)
        dut.tick.value, dut.muestra.value = 1, muestra
        await RisingEdge(dut.clk)
        dut.tick.value = 0
        leidos = []
        for ciclo in range(1, CICLOS_POR_MUESTRA):
            await Timer(1, unit="ns")
            if ciclo >= DESPLAZAMIENTO and (ciclo - DESPLAZAMIENTO) % MANTENIMIENTO == 0:
                leidos.append(dut.alto.value.to_signed())
                assert int(dut.valido.value) == 1
            await RisingEdge(dut.clk)
        assert leidos == esperados[: len(leidos)], f"muestra {indice} = {muestra}"
        assert len(leidos) == INTERPOLACION, f"faltan valores: {len(leidos)}"


def test_cic_interp(tmp_path: Path) -> None:
    construir(tmp_path, [RTL / "salida" / "cic_interp.v"], "cic_interp", "cic_interp_test")
