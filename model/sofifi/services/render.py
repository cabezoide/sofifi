# SPDX-License-Identifier: MIT
"""Casos de uso: ensamblar a microcódigo y procesar audio con un programa.

Reciben sus puertos ya construidos (inversión de dependencias): no conocen
ficheros ni formatos, así que la suite los ejercita en seco con dobles en memoria.
"""

from __future__ import annotations

from dataclasses import dataclass

from sofifi.domain.ensamblador import ensamblar
from sofifi.domain.isa import Programa, codificar
from sofifi.domain.nucleo import Nucleo
from sofifi.domain.senal import Controles, Senal
from sofifi.ports.audio import FuenteAudio, FuentePrograma, SumideroAudio, SumideroMicrocodigo

SW_PULSADO = (1 << 23) - 1


@dataclass(frozen=True)
class InformeRender:
    programa: str
    instrucciones: int
    ciclos: int
    palabras_memoria: int
    muestras: int


def exportar_microcodigo(fuente: FuentePrograma, sumidero: SumideroMicrocodigo) -> Programa:
    nombre, texto = fuente.leer()
    programa = ensamblar(texto, nombre, fuente.incluir)
    sumidero.escribir(programa, [codificar(i) for i in programa.instrucciones])
    return programa


def procesar(programa: Programa, entrada: Senal, controles: Controles, cola: int = 0) -> Senal:
    """Pasa ``entrada`` (mono o estéreo) por el núcleo y añade ``cola`` muestras de silencio."""
    nucleo = Nucleo(programa)
    izq_in = entrada.canales[0]
    der_in = entrada.canales[-1]
    total = entrada.muestras + cola
    izq: list[int] = []
    der: list[int] = []
    for k in range(total):
        x_l = izq_in[k] if k < entrada.muestras else 0
        x_r = der_in[k] if k < entrada.muestras else 0
        sw = SW_PULSADO if controles.sw_en(k) else 0
        y_l, y_r = nucleo.procesar(x_l, x_r, controles.pots, sw)
        izq.append(y_l)
        der.append(y_r)
    return Senal(entrada.fs_hz, (tuple(izq), tuple(der)))


def renderizar(
    fuente_programa: FuentePrograma,
    fuente_audio: FuenteAudio,
    sumidero: SumideroAudio,
    controles: Controles,
    cola: int = 0,
) -> InformeRender:
    nombre, texto = fuente_programa.leer()
    programa = ensamblar(texto, nombre, fuente_programa.incluir)
    salida = procesar(programa, fuente_audio.leer(), controles, cola)
    sumidero.escribir(salida)
    return InformeRender(
        nombre,
        len(programa.instrucciones),
        programa.ciclos,
        programa.palabras_memoria,
        salida.muestras,
    )
