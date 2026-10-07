# SPDX-License-Identifier: MIT
"""alu.v: para cada instrucción, el ACC siguiente es el del manejador del modelo.

El testbench pone en `p` el producto que pondrá el secuenciador (ver la cabecera
de alu.v) y ejecuta el manejador de model/sofifi/domain/nucleo.py sobre un núcleo
de prueba con el mismo estado. Los dos ACC deben coincidir bit a bit.
"""

from __future__ import annotations

import random
from pathlib import Path

import cocotb
from cocotb.triggers import Timer
from comun import RTL, con_signo, construir
from sofifi.domain.aritmetica import acc_a_dato
from sofifi.domain.isa import Instruccion, Op, addr_con_signo
from sofifi.domain.nucleo import MANEJADORES, Nucleo

OPS = [op for op in Op if op not in (Op.SKP, Op.CHO, Op.CLIP)]  # CLIP: curva_fin_test.py


class MemoriaFija:
    """Memoria de prueba: siempre devuelve el mismo valor y acepta escrituras."""

    def __init__(self, valor: int) -> None:
        self.valor = valor

    def leer(self, direccion: int) -> int:
        return self.valor

    def escribir(self, direccion: int, valor: int) -> None:
        pass


def producto(op: Op, a24: int, r: int, v: int, c: int) -> int:
    if op in (Op.RDA,):
        return v * c
    if op in (Op.RDAX, Op.MAXX):
        return r * c
    if op in (Op.WRA, Op.WRAX, Op.WRAP, Op.SOF):
        return a24 * c
    if op is Op.RDFX:
        return (a24 - r) * c
    if op is Op.MULX:
        return a24 * r
    return 0


@cocotb.test()
async def acc_igual_al_modelo(dut: cocotb.handle.HierarchyObject) -> None:
    azar = random.Random(9)
    for _ in range(40_000):
        op = azar.choice(OPS)
        acc, lr, r = con_signo(azar, 48), con_signo(azar, 24), con_signo(azar, 24)
        c, addr = con_signo(azar, 18), azar.randrange(1 << 18)
        v = con_signo(azar, 18) << 6  # la memoria guarda 18 bit alineados a dato
        n = object.__new__(Nucleo)
        n.acc, n.lr, n.regs, n.primera = acc, lr, [r] * 64, False
        n.memoria = MemoriaFija(v)  # type: ignore[assignment]
        a24 = acc_a_dato(acc)
        p = producto(op, a24, r, v, c)
        MANEJADORES[op](n, Instruccion(op, reg=0, coef=c, addr=addr))

        dut.op.value, dut.acc.value, dut.p.value = int(op), acc, p
        dut.lr.value, dut.r.value, dut.addr.value = lr, r, addr
        await Timer(1, unit="ns")
        assert dut.acc_sig.value.to_signed() == n.acc, (
            f"{op.name}: acc={acc} lr={lr} r={r} c={c} addr={addr_con_signo(addr)} p={p}"
        )


def test_alu(tmp_path: Path) -> None:
    construir(
        tmp_path,
        [RTL / "nucleo" / m for m in ("alu.v", "saturar_acc.v")],
        "alu",
        "alu_test",
    )
