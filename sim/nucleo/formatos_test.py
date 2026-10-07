# SPDX-License-Identifier: MIT
"""formatos.v: acc_a_dato, dato_a_memoria y saturar_acc coinciden con aritmetica.py."""

from __future__ import annotations

import random
from pathlib import Path

import cocotb
from cocotb.triggers import Timer
from comun import AQUI, RTL, con_signo, construir
from sofifi.domain.aritmetica import acc_a_dato, dato_a_memoria, saturar_acc


@cocotb.test()
async def conversiones_bit_exactas(dut: cocotb.handle.HierarchyObject) -> None:
    azar = random.Random(4)
    for _ in range(20_000):
        acc, dato, valor = con_signo(azar, 48), con_signo(azar, 24), con_signo(azar, 50)
        dut.acc.value, dut.dato.value, dut.valor.value = acc, dato, valor
        await Timer(1, unit="ns")
        assert dut.acc_dato.value.to_signed() == acc_a_dato(acc), f"acc_a_dato({acc})"
        assert dut.palabra.value.to_signed() << 6 == dato_a_memoria(dato), f"dato_a_memoria({dato})"
        assert dut.acc_sat.value.to_signed() == saturar_acc(valor), f"saturar_acc({valor})"


def test_formatos(tmp_path: Path) -> None:
    construir(
        tmp_path,
        [RTL / "nucleo" / f"{m}.v" for m in ("acc_a_dato", "dato_a_memoria", "saturar_acc")]
        + [AQUI / "formatos_prueba.v"],
        "formatos_prueba",
        "formatos_test",
    )
