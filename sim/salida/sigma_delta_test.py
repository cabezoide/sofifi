# SPDX-License-Identifier: MIT
"""sigma_delta.v: el pin da el mismo bit que ModuladorSigmaDelta del modelo.

Compara paso a paso, con la entrada mantenida 64 ciclos, como en la cadena real
(ADR 0015). El RTL registra el bit, así que se lee tras el flanco.
"""

from __future__ import annotations

import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, Timer
from comun_salida import RTL, construir
from sofifi.domain.salida_1bit import (
    LIMITE,
    MANTENIMIENTO,
    ModuladorSigmaDelta,
    recortar,
)

VALORES = 400  # valores mantenidos; 400 x 64 = 25 600 ciclos


@cocotb.test()
async def igual_al_modelo(dut: cocotb.handle.HierarchyObject) -> None:
    azar = random.Random(15)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst.value, dut.habilita.value, dut.alto.value = 1, 1, 0
    await ClockCycles(dut.clk, 3)
    dut.rst.value = 0

    modelo = ModuladorSigmaDelta()
    assert int(dut.bit_salida.value) == modelo.bit, "el reset no deja el mismo bit"
    for _ in range(VALORES):
        # Los valores llegan del CIC: dentro del rango del recorte.
        alto = recortar(azar.randrange(-LIMITE, LIMITE + 1))
        dut.alto.value = alto
        for _ in range(MANTENIMIENTO):
            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")
            esperado = modelo.paso(alto)
            assert int(dut.bit_salida.value) == esperado, f"alto={alto}"
            assert dut.integra1.value.to_signed() == modelo.integra1
            assert dut.integra2.value.to_signed() == modelo.integra2


def test_sigma_delta(tmp_path: Path) -> None:
    construir(tmp_path, [RTL / "salida" / "sigma_delta.v"], "sigma_delta", "sigma_delta_test")
