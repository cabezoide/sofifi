# SPDX-License-Identifier: MIT
"""Servicios en seco: dobles en memoria por los puertos, sin ficheros (SPEC_RAIZ §4.4)."""

from __future__ import annotations

from sofifi.domain.aritmetica import dato
from sofifi.domain.ensamblador import ensamblar
from sofifi.domain.isa import Programa
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import SW_PULSADO, exportar_microcodigo, procesar, renderizar

PASO = "rdax adcl, 1.0\nwrax dacl, 0\nrdax sw, 1.0\nwrax dacr, 0\n"


class ProgramaEnMemoria:
    def __init__(self, texto: str, incluidos: dict[str, str] | None = None) -> None:
        self.texto = texto
        self.incluidos = incluidos or {}

    def leer(self) -> tuple[str, str]:
        return "mem", self.texto

    def incluir(self, nombre: str) -> str:
        return self.incluidos[nombre]


class AudioEnMemoria:
    def __init__(self, senal: Senal) -> None:
        self.senal = senal
        self.escrita: Senal | None = None

    def leer(self) -> Senal:
        return self.senal

    def escribir(self, senal: Senal) -> None:
        self.escrita = senal


class MicrocodigoEnMemoria:
    def __init__(self) -> None:
        self.palabras: list[int] = []
        self.programa: Programa | None = None

    def escribir(self, programa: Programa, palabras: list[int]) -> None:
        self.programa, self.palabras = programa, palabras


def test_renderizar_mono_a_estereo_con_cola_y_footswitch() -> None:
    audio = AudioEnMemoria(Senal(48828, ((dato("0.5"), dato("0.25")),)))
    informe = renderizar(
        ProgramaEnMemoria(PASO), audio, audio, Controles(tramos_sw=((1, 3),)), cola=2
    )
    assert informe.muestras == 4
    assert audio.escrita is not None
    izq, der = audio.escrita.canales
    assert izq == (dato("0.5"), dato("0.25"), 0, 0)
    assert der == (0, SW_PULSADO, SW_PULSADO, 0)


def test_exportar_microcodigo() -> None:
    sumidero = MicrocodigoEnMemoria()
    p = exportar_microcodigo(ProgramaEnMemoria(PASO), sumidero)
    assert len(sumidero.palabras) == len(p.instrucciones) == 4
    assert all(0 <= w < 1 << 54 for w in sumidero.palabras)


def test_procesar_es_determinista() -> None:
    p = ensamblar("lfo 0 rnd 8\nmem d 40\nrdax adcl,1\nwra d,0\ncho d,1,lfo0\nwrax dacl,0\n")
    x = Senal(48828, (tuple(dato("0.3") if k % 50 == 0 else 0 for k in range(2000)),))
    assert procesar(p, x, Controles()) == procesar(p, x, Controles())
