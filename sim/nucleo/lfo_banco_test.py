# SPDX-License-Identifier: MIT
"""lfo_banco.v: fase, triángulo, ventana y salida RND iguales a Lfo del modelo."""

from __future__ import annotations

import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, Timer
from comun import RTL, con_signo, construir
from sofifi.domain.lfo import FASE_MOD, MEDIA_FASE, ConfigLfo, Lfo, TipoLfo, triangulo, ventana

TIPOS = (TipoLfo.SIN, TipoLfo.RND, TipoLfo.RAMP, TipoLfo.RND)
CODIGO = {TipoLfo.SIN: 0, TipoLfo.RND: 1, TipoLfo.RAMP: 2}


@cocotb.test()
async def igual_al_modelo(dut: cocotb.handle.HierarchyObject) -> None:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    modelos = [Lfo(ConfigLfo(t, 10)) for t in TIPOS]
    dut.tipos.value = sum(CODIGO[t] << (2 * n) for n, t in enumerate(TIPOS))
    dut.avanzar.value, dut.sel.value, dut.media.value, dut.rates.value = 0, 0, 0, 0
    dut.rst.value = 1
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0
    azar = random.Random(7)
    for muestra in range(3000):
        # Rates lentos, rápidos (muchas vueltas del RND) y negativos.
        rates = [con_signo(azar, azar.choice((12, 20, 24))) for _ in range(4)]
        dut.rates.value = sum((r & 0xFFFFFF) << (24 * n) for n, r in enumerate(rates))
        dut.avanzar.value = 1
        await RisingEdge(dut.clk)
        dut.avanzar.value = 0
        for lfo, r in zip(modelos, rates, strict=True):
            lfo.avanzar(r)
        while not int(dut.listo.value):
            await RisingEdge(dut.clk)
        for n, lfo in enumerate(modelos):
            for media in (0, 1):
                dut.sel.value, dut.media.value = n, media
                await Timer(1, unit="ns")
                fm = (lfo.fase + MEDIA_FASE) % FASE_MOD if media else lfo.fase
                donde = f"muestra {muestra}, LFO {n}, media {media}"
                assert int(dut.fase_sel.value) == fm, donde
                assert dut.tri_sel.value.to_signed() == triangulo(lfo.fase), donde
                assert dut.ven_sel.value.to_signed() == ventana(fm), donde
                assert dut.actual_sel.value.to_signed() == lfo._actual, donde


def test_lfo_banco(tmp_path: Path) -> None:
    construir(tmp_path, [RTL / "nucleo" / "lfo_banco.v"], "lfo_banco", "lfo_banco_test")
