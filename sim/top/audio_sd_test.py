# SPDX-License-Identifier: MIT
"""audio_sd.v de punta a punta: microSD → núcleo → salida de 1 bit (Fase 13).

Criterio de la fase: el flujo de bits del pin es el del modelo, bit a bit
(ADR 0003). La cadena del modelo es: pista → `procesar` con el plate →
`Salida1Bit`.

El núcleo entrega la muestra de audio con un `tick` de retraso: en el `tick` k,
la salida de 1 bit toma el `dac_l` de la muestra k−1. Por eso el modelo lleva
una muestra de silencio delante.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb_tools.runner import get_runner

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
RTL = RAIZ / "rtl"
sys.path.insert(0, str(RAIZ / "sim" / "sd"))

from sofifi.adapters.archivos import ensamblar_archivo  # noqa: E402
from sofifi.domain.aritmetica import CICLOS_POR_MUESTRA, FS_WAV, UNO  # noqa: E402
from sofifi.domain.pista import MIN_MUESTRAS, escribir, muestra_a_dato  # noqa: E402
from sofifi.domain.salida_1bit import LATENCIA_CICLOS, Salida1Bit  # noqa: E402
from sofifi.domain.senal import Controles, Senal  # noqa: E402
from sofifi.services.render import procesar  # noqa: E402
from tarjeta_sd import TarjetaSD, Variante  # noqa: E402

MUESTRAS_PISTA = [round(0.4 * 32767 * (1 - 2 * ((k // 37) % 2))) for k in range(MIN_MUESTRAS)]
IMAGEN = escribir(MUESTRAS_PISTA)
N_COMPARADAS = 12  # muestras de audio; cada una son 2 048 ciclos
POT = UNO // 2  # el top fija los seis pots a 0,5


def bits_del_modelo() -> list[int]:
    programa = ensamblar_archivo(RAIZ / "programas" / "plate.sasm")
    entrada = Senal(FS_WAV, (tuple(muestra_a_dato(v) for v in MUESTRAS_PISTA),))
    salida = procesar(programa, entrada, Controles(pots=(POT,) * 6))
    # El pin lleva una muestra de retraso: el primer tick saca un dac_l de cero.
    muestras = [0, *salida.canales[0]]
    return list(Salida1Bit().flujo(muestras[: N_COMPARADAS + 1]))


@cocotb.test()
async def flujo_igual_al_modelo(dut: cocotb.handle.HierarchyObject) -> None:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    tarjeta = TarjetaSD(dut, IMAGEN, Variante())
    cocotb.start_soon(tarjeta.correr())
    dut.rst_n.value = 1
    for _ in range(400_000):
        await RisingEdge(dut.clk)
        if int(dut.u_pista.preparado.value):
            break
    assert int(dut.u_pista.preparado.value) == 1, "la pista no llegó a estar lista"
    assert int(dut.u_pista.u_lector.error.value) == 0

    # Desde el primer tick, un bit por ciclo.
    while not int(dut.u_gen.tick.value):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
    bits = []
    for _ in range(N_COMPARADAS * CICLOS_POR_MUESTRA):
        bits.append(int(dut.audio.value))
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

    esperados = bits_del_modelo()
    desfase = bits[LATENCIA_CICLOS:]
    parejas = enumerate(zip(desfase, esperados, strict=False))
    primera = next((k for k, (a, b) in parejas if a != b), None)
    assert primera is None, (
        f"primera diferencia en el bit {primera} "
        f"(muestra {(primera or 0) // CICLOS_POR_MUESTRA})"
    )
    assert int(dut.u_pista.u_lector.vacio.value) == 0, "la cola se quedó sin datos"


def _fuentes(top: str) -> list[Path]:
    """Las fuentes del top, de la lista única rtl/top/tops.txt."""
    for linea in (RTL / "top" / "tops.txt").read_text(encoding="utf-8").splitlines():
        if linea.startswith(f"{top} "):
            return [RAIZ / ruta for ruta in linea.split()[1:]]
    raise AssertionError(f"{top} no está en rtl/top/tops.txt")


def test_audio_sd(tmp_path: Path) -> None:
    fuentes = _fuentes("audio_sd")
    runner = get_runner("verilator")
    runner.build(
        sources=fuentes,
        hdl_toplevel="audio_sd",
        parameters={"DIV_LENTO": 6, "DIV_RAPIDO": 4},
        defines={"SIMULACION": 1},
        build_dir=tmp_path,
        build_args=["-Wall"],
        always=True,
    )
    runner.test(
        hdl_toplevel="audio_sd",
        test_module="audio_sd_test",
        test_dir=AQUI,
        build_dir=tmp_path,
    )
