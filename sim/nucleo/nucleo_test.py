# SPDX-License-Identifier: MIT
"""nucleo.v: los programas de programas/ dan la misma salida que el modelo, muestra a muestra.

Es el criterio de la Fase 04 (ADR 0003): igualdad exacta, tolerancia cero. El
estímulo es un impulso y después ruido del LFSR del modelo; los potenciómetros
están fijos y, en freeze, el footswitch se pulsa a mitad de la prueba.

SOFIFI_MUESTRAS fija la longitud. Por defecto son 1 000 muestras, para que la
compuerta siga siendo rápida; los criterios de aceptación de la Fase 04 se
ejecutan aparte (MED-09):

    SOFIFI_MUESTRAS=4883 pytest sim/nucleo/nucleo_test.py                 # 0,1 s, los tres
    SOFIFI_MUESTRAS=48828 SOFIFI_PROGRAMAS=plate pytest sim/nucleo/nucleo_test.py   # 1 s
    SOFIFI_MUESTRAS=12000 SOFIFI_PROGRAMAS=cinta pytest sim/nucleo/nucleo_test.py   # eco

Las 1 000 muestras de la compuerta no llegan al primer eco de la cinta (0,18 s):
en ella solo se compara la señal seca. El eco se compara en la aceptación.
"""

from __future__ import annotations

import os
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb_tools.runner import get_runner
from comun import AQUI, RAIZ, RTL
from sofifi.adapters.archivos import ensamblar_archivo
from sofifi.domain.aritmetica import CICLOS_POR_MUESTRA, dato
from sofifi.domain.coste import CICLOS_SKP_SIN_SALTO, ciclos_instruccion_rtl, ciclos_rtl
from sofifi.domain.ensamblador import ensamblar
from sofifi.domain.isa import Programa, codificar
from sofifi.domain.lfo import TipoLfo
from sofifi.domain.nucleo import Nucleo

PROGRAMAS = tuple(sorted(p.stem for p in (RAIZ / "programas").glob("*.sasm")))
# La cinta, con pot0 = 0: el primer eco llega a las ~8 800 muestras y no a las ~31 700.
POTS_PRUEBA = {
    "plate": ("0.7", "0.5", "0.3", "0.6", "0.4", "0.2"),
    "cinta": ("0", "0.5", "0.3", "0.6", "0.4", "0.2"),
}
CODIGO_LFO = {TipoLfo.SIN: 0, TipoLfo.RND: 1, TipoLfo.RAMP: 2}
FUENTES = [
    RTL / "nucleo" / f
    for f in (
        "nucleo.v",
        "alu.v",
        "curva_fin.v",
        "acc_a_dato.v",
        "dato_a_memoria.v",
        "saturar_acc.v",
        "memoria_retardo.v",
        "lfo_banco.v",
        "tabla_hermite.v",
    )
] + [
    RTL / "primitivas" / f
    for f in ("mult_27x36.v", "bsram_pipe.v", "bsram_bloque.v", "registro_copia.v")
]


def estimulo(n: int) -> list[tuple[int, int]]:
    """Impulso en la muestra 0 y, desde la mitad, ruido de media escala."""
    azar = random.Random(2026)
    muestras = [(dato("0.5"), dato("-0.25"))] + [(0, 0)] * (n // 2 - 1)
    while len(muestras) < n:
        muestras.append((azar.randrange(-(1 << 21), 1 << 21), azar.randrange(-(1 << 21), 1 << 21)))
    return muestras


@cocotb.test()
async def igual_al_modelo(dut: cocotb.handle.HierarchyObject) -> None:
    nombre = os.environ["PROGRAMA"]
    n = int(os.environ.get("SOFIFI_MUESTRAS", "1000"))
    programa = ensamblar_archivo(RAIZ / "programas" / f"{nombre}.sasm")
    modelo = Nucleo(programa)
    pots = tuple(dato(v) for v in POTS_PRUEBA.get(nombre, POTS_PRUEBA["plate"]))

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst.value, dut.tick.value, dut.prog_we.value = 1, 0, 0
    dut.cfg_instrucciones.value = len(programa.instrucciones)
    dut.cfg_palabras.value = programa.palabras_memoria
    dut.cfg_lfo_tipos.value = sum(
        CODIGO_LFO[c.tipo] << (2 * k) for k, c in enumerate(programa.lfos) if c is not None
    )
    dut.cfg_lfo_excursiones.value = sum(
        c.excursion << (15 * k) for k, c in enumerate(programa.lfos) if c is not None
    )
    dut.pots.value = sum((v & 0xFFFFFF) << (24 * k) for k, v in enumerate(pots))
    await ClockCycles(dut.clk, 3)
    for k, ins in enumerate(programa.instrucciones):
        dut.prog_we.value, dut.prog_dir.value, dut.prog_dato.value = 1, k, codificar(ins)
        await RisingEdge(dut.clk)
    dut.prog_we.value = 0
    dut.rst.value = 0
    await RisingEdge(dut.clk)
    # El núcleo borra la memoria de retardo antes de atender ticks.
    while int(dut.ocupado.value):
        await RisingEdge(dut.clk)

    maximo = 0
    for k, (izq, der) in enumerate(estimulo(n)):
        sw = 1 if nombre == "freeze" and n // 3 <= k < 2 * n // 3 else 0
        dut.adc_l.value, dut.adc_r.value, dut.sw.value = izq, der, sw
        dut.tick.value = 1
        await RisingEdge(dut.clk)
        dut.tick.value = 0
        while not int(dut.fin.value):
            await RisingEdge(dut.clk)
        esperado = modelo.procesar(izq, der, pots, sw)
        obtenido = (dut.dac_l.value.to_signed(), dut.dac_r.value.to_signed())
        assert obtenido == esperado, f"{nombre}, muestra {k}: RTL {obtenido}, modelo {esperado}"
        maximo = max(maximo, int(dut.ciclos.value))
    cota = ciclos_rtl(programa)
    dut._log.info(
        "%s: %d muestras iguales; máximo %d ciclos por muestra (cota del modelo %d)",
        nombre,
        n,
        maximo,
        cota,
    )
    assert maximo <= cota <= CICLOS_POR_MUESTRA, f"{nombre}: {maximo} ciclos, cota {cota}"


RETARDO_8 = """
mem  d  8
rdax adcl, 1.0
wra  d, 0
rda  d#, 1.0
wrax dacl, 0
"""


async def cargar(dut: cocotb.handle.HierarchyObject, programa: Programa) -> None:
    """Carga un programa con el núcleo en reset y espera a que borre la memoria."""
    dut.rst.value, dut.tick.value = 1, 0
    dut.cfg_instrucciones.value = len(programa.instrucciones)
    dut.cfg_palabras.value = programa.palabras_memoria
    dut.cfg_lfo_tipos.value, dut.cfg_lfo_excursiones.value = 0, 0
    for k, ins in enumerate(programa.instrucciones):
        dut.prog_we.value, dut.prog_dir.value, dut.prog_dato.value = 1, k, codificar(ins)
        await RisingEdge(dut.clk)
    dut.prog_we.value, dut.rst.value = 0, 0
    await RisingEdge(dut.clk)
    while int(dut.ocupado.value):
        await RisingEdge(dut.clk)


async def muestra(dut: cocotb.handle.HierarchyObject, izq: int) -> int:
    dut.adc_l.value, dut.adc_r.value, dut.sw.value = izq, 0, 0
    dut.tick.value = 1
    await RisingEdge(dut.clk)
    dut.tick.value = 0
    while not int(dut.fin.value):
        await RisingEdge(dut.clk)
    return int(dut.dac_l.value.to_signed())


@cocotb.test()
async def reset_borra_la_memoria(dut: cocotb.handle.HierarchyObject) -> None:
    """Un retardo de 8 muestras: tras un reset, no debe salir nada de antes."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.pots.value = 0
    programa = ensamblar(RETARDO_8, "retardo_8")
    await cargar(dut, programa)
    azar = random.Random(8)
    for _ in range(40):  # memoria llena de ruido
        await muestra(dut, azar.randrange(-(1 << 22), 1 << 22))
    await cargar(dut, programa)
    modelo = Nucleo(programa)
    for k in range(20):
        esperado = modelo.procesar(0, 0)[0]
        assert await muestra(dut, 0) == esperado, f"muestra {k} tras el reset"


SALTOS = """
mem  d  4
        rdax adcl, 1.0
        skp  neg, negativo
        sof  0.5, 0.25
        wrax dacl, 0
        skp  zro, fin
negativo:
        sof  -0.5, 0
        wrax dacl, 0
fin:
        rdax adcr, 1.0
        skp  gez, positivo
        clr
positivo:
        sof  1.0, -0.125
        wrax dacr, 0
"""


@cocotb.test()
async def saltos_iguales_al_modelo(dut: cocotb.handle.HierarchyObject) -> None:
    """SKP condicionales que saltan o no según el signo: la lectura adelantada se rehace."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.pots.value = 0
    programa = ensamblar(SALTOS, "saltos")
    await cargar(dut, programa)
    modelo = Nucleo(programa)
    azar = random.Random(11)
    for k in range(200):
        izq, der = azar.randrange(-(1 << 22), 1 << 22), azar.randrange(-(1 << 22), 1 << 22)
        dut.adc_l.value, dut.adc_r.value, dut.sw.value = izq, der, 0
        dut.tick.value = 1
        await RisingEdge(dut.clk)
        dut.tick.value = 0
        while not int(dut.fin.value):
            await RisingEdge(dut.clk)
        esperado = modelo.procesar(izq, der)
        obtenido = (dut.dac_l.value.to_signed(), dut.dac_r.value.to_signed())
        assert obtenido == esperado, f"muestra {k}: RTL {obtenido}, modelo {esperado}"


CABECERA_COSTE = "mem d 64\nlfo 0 sin 8\nlfo 1 rnd 8\nlfo 2 ramp 32\n"
MUESTRA_COSTE = {
    "rdax": "rdax adcl, 0.5",
    "wrax": "wrax reg0, 1.0",
    "rda": "rda d + 5, 0.5",
    "wra": "wra d + 5, 1.0",
    "wrap": "wrap d + 5, 0.5",
    "rdfx": "rdfx reg1, 0.5",
    "maxx": "maxx reg1, 0.5",
    "mulx": "mulx reg1",
    "sof": "sof 0.5, 0.1",
    "clip": "clip",
    "ldax": "ldax reg1",
    "clr": "clr",
    "absa": "absa",
    "nop": "nop",
    "cho_sin": "cho d + 10, 0.5, lfo0",
    "cho_rnd": "cho d + 10, 0.5, lfo1",
    "cho_ramp": "cho d + 10, 0.5, lfo2",
    "cho_ramp_na": "cho d + 10, 0.5, lfo2, na",
    "skp_no": "skp neg, 0",
    "skp_si": "skp gez, 1\nnop",  # salta: el nop no se ejecuta
}


async def ciclos_de(dut: cocotb.handle.HierarchyObject, texto: str) -> int:
    await cargar(dut, ensamblar(CABECERA_COSTE + texto, "coste"))
    await muestra(dut, 0)
    await muestra(dut, 0)
    return int(dut.ciclos.value)


@cocotb.test()
async def coste_de_cada_instruccion(dut: cocotb.handle.HierarchyObject) -> None:
    """Ciclos de cada instrucción en el RTL: los que cuenta el modelo (coste.py)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.pots.value = 0
    # Con 10 y 20 copias de cada instrucción: la diferencia es el coste de 10.
    for nombre, linea in MUESTRA_COSTE.items():
        diez = await ciclos_de(dut, "\n".join([linea] * 10))
        veinte = await ciclos_de(dut, "\n".join([linea] * 20))
        modelo = ciclos_instruccion_rtl(ensamblar(CABECERA_COSTE + linea, "coste").instrucciones[0])
        if nombre == "skp_no":
            modelo = CICLOS_SKP_SIN_SALTO
        assert veinte - diez == 10 * modelo, (
            f"{nombre}: RTL {(veinte - diez) / 10}, modelo {modelo}"
        )
        assert diez <= ciclos_rtl(ensamblar(CABECERA_COSTE + "\n".join([linea] * 10), "coste"))


def test_nucleo(tmp_path: Path) -> None:
    runner = get_runner("verilator")
    runner.build(
        sources=FUENTES,
        hdl_toplevel="nucleo",
        defines={"SIMULACION": 1},
        build_dir=tmp_path,
        build_args=["-Wall"],
        always=True,
    )
    for nombre in os.environ.get("SOFIFI_PROGRAMAS", ",".join(PROGRAMAS)).split(","):
        runner.test(
            hdl_toplevel="nucleo",
            test_module="nucleo_test",
            test_dir=AQUI,
            build_dir=tmp_path,
            extra_env={"PROGRAMA": nombre},
            results_xml=str(tmp_path / f"resultados_{nombre}.xml"),
        )
