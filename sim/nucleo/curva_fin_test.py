# SPDX-License-Identifier: MIT
"""curva_fin.v: con 3x y p = x2·x calculados como en el núcleo, da curva_suave(x)."""

from __future__ import annotations

import random
from pathlib import Path

import cocotb
from cocotb.triggers import Timer
from comun import RTL, con_signo, construir
from sofifi.domain.aritmetica import DATO_FRAC, curva_suave


@cocotb.test()
async def igual_al_modelo(dut: cocotb.handle.HierarchyObject) -> None:
    azar = random.Random(3)
    for _ in range(20_000):
        x = con_signo(azar, 24)
        x2 = (x * x) >> DATO_FRAC
        dut.tres_x.value, dut.p.value = 3 * x, x2 * x
        await Timer(1, unit="ns")
        assert dut.y.value.to_signed() == curva_suave(x), f"x={x}"


def test_curva_fin(tmp_path: Path) -> None:
    construir(tmp_path, [RTL / "nucleo" / "curva_fin.v"], "curva_fin", "curva_fin_test")
