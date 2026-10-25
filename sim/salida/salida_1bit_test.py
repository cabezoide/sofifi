# SPDX-License-Identifier: MIT
"""salida_1bit.v: el pin da el mismo flujo de bits que el modelo (ADR 0003).

El RTL va LATENCIA ciclos por detrás del modelo, porque cada ciclo hace una
sola suma. El retardo es fijo, así que la comparación desplaza el flujo. La
prueba incluye muestras a escala plena, que ejercitan el recorte de seguridad.
"""

from __future__ import annotations

from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, Timer
from comun_salida import RTL, construir
from sofifi.domain.aritmetica import CICLOS_POR_MUESTRA, UNO
from sofifi.domain.salida_1bit import LIMITE, Salida1Bit

LATENCIA = 6  # ciclos de retardo del RTL; está en la cabecera de salida_1bit.v
MUESTRAS = (0, UNO - 1, -UNO, LIMITE, -LIMITE // 2, 123456, -1, UNO // 3)


@cocotb.test()
async def igual_al_modelo(dut: cocotb.handle.HierarchyObject) -> None:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst.value, dut.tick.value, dut.muestra.value = 1, 0, 0
    await ClockCycles(dut.clk, 3)
    dut.rst.value = 0
    await RisingEdge(dut.clk)

    bits_rtl = []
    for muestra in MUESTRAS:
        dut.tick.value, dut.muestra.value = 1, muestra
        for ciclo in range(CICLOS_POR_MUESTRA):
            await Timer(1, unit="ns")
            bits_rtl.append(int(dut.bit_salida.value))
            await RisingEdge(dut.clk)
            if ciclo == 0:
                dut.tick.value = 0

    bits_modelo = list(Salida1Bit().flujo(MUESTRAS))
    assert len(bits_rtl) == len(bits_modelo)
    desfase = bits_rtl[LATENCIA:]
    for indice, (rtl, modelo) in enumerate(zip(desfase, bits_modelo, strict=False)):
        assert rtl == modelo, f"bit {indice}: RTL {rtl}, modelo {modelo}"
    # Tras el reset el pin vale 1, como el modelo; los LATENCIA primeros bits
    # son ese valor de arranque.
    assert bits_rtl[:LATENCIA] == [1] * LATENCIA


def test_salida_1bit(tmp_path: Path) -> None:
    fuentes = [
        RTL / "salida" / "salida_1bit.v",
        RTL / "salida" / "cic_interp.v",
        RTL / "salida" / "sigma_delta.v",
    ]
    construir(tmp_path, fuentes, "salida_1bit", "salida_1bit_test")
