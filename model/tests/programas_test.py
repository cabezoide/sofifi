# SPDX-License-Identifier: MIT
"""Programas del núcleo: plate, shimmer y freeze (Fase 01); hall y cloud (Fase 06).

Comprueban propiedades acústicas medibles (decae, se sostiene, sube una octava,
el decay sigue al potenciómetro, la modulación cambia la respuesta)
y una **huella bit-exact** por programa: cambiar la aritmética, la ISA o un
programa cambia la huella, y actualizarla es una decisión que se ve en el diff.
No comprueban que suene bonito: eso se escucha (ver `sofifi render`).
"""

from __future__ import annotations

import hashlib
import math
from functools import cache
from pathlib import Path

import pytest
from sofifi.adapters.archivos import ensamblar_archivo
from sofifi.domain.aritmetica import DATO_MAX, UNO, dato
from sofifi.domain.coste import cabe_en_el_rtl, ciclos_rtl
from sofifi.domain.isa import Programa
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar

PROGRAMAS = Path(__file__).resolve().parents[2] / "programas"
FS = 48828


@cache
def programa(nombre: str) -> Programa:
    return ensamblar_archivo(PROGRAMAS / f"{nombre}.sasm")


def impulso(segundos: float, en: int = 0) -> Senal:
    x = [0] * int(segundos * FS)
    x[en] = dato("0.5")
    return Senal(FS, (tuple(x),))


def rms(v: tuple[int, ...], a: float, b: float) -> float:
    seg = v[int(a * FS) : int(b * FS)]
    return math.sqrt(sum((s / UNO) ** 2 for s in seg) / len(seg))


def potencia(v: tuple[int, ...], f: float, a: float, b: float) -> float:
    seg = v[int(a * FS) : int(b * FS)]
    w = 2 * math.pi * f / FS
    re = sum(s * math.cos(w * k) for k, s in enumerate(seg))
    im = sum(s * math.sin(w * k) for k, s in enumerate(seg))
    return (re * re + im * im) / UNO**2


def pots(*valores: str) -> tuple[int, ...]:
    return tuple(dato(v) for v in valores)


@pytest.mark.parametrize("nombre", ["plate", "shimmer", "freeze", "hall", "cloud"])
def test_cabe_en_el_nucleo(nombre: str) -> None:
    p = programa(nombre)
    assert cabe_en_el_rtl(p), f"{ciclos_rtl(p)} ciclos del RTL > 2 048"
    assert p.palabras_memoria <= 43008


def test_plate_decae_y_es_estereo() -> None:
    y = procesar(programa("plate"), impulso(1.0), Controles(pots("0.5", "0.3", "0.5")))
    izq, der = y.canales
    assert rms(izq, 0.05, 0.25) > 3 * rms(izq, 0.6, 0.8) > 0
    assert izq[1000:20000] != der[1000:20000]
    assert max(abs(v) for v in izq[100:]) < DATO_MAX // 4


def test_plate_mas_decay_es_mas_larga() -> None:
    corta = procesar(programa("plate"), impulso(1.0), Controles(pots("0.1", "0.3", "0.5")))
    larga = procesar(programa("plate"), impulso(1.0), Controles(pots("0.9", "0.3", "0.5")))
    assert rms(larga.canales[0], 0.6, 0.9) > 4 * rms(corta.canales[0], 0.6, 0.9)


def test_freeze_sostiene_la_cola() -> None:
    sw = Controles(pots("0.5", "0.3", "0.5"), tramos_sw=((int(0.05 * FS), 10 * FS),))
    y = procesar(programa("freeze"), impulso(1.5), sw).canales[0]
    temprano, tardio = rms(y, 0.5, 0.8), rms(y, 1.2, 1.5)
    assert tardio > 0.9 * temprano
    assert max(abs(v) for v in y) <= DATO_MAX


def test_freeze_sin_pulsar_decae_como_plate() -> None:
    y = procesar(programa("freeze"), impulso(1.0), Controles(pots("0.5", "0.3", "0.5"))).canales[0]
    assert rms(y, 0.05, 0.25) > 3 * rms(y, 0.6, 0.8)


def test_shimmer_anade_la_octava_superior() -> None:
    f = 330.0
    n_tono = int(0.25 * FS)
    tono = tuple(
        dato(str(round(0.3 * math.sin(2 * math.pi * f * k / FS), 6))) for k in range(n_tono)
    )
    x = Senal(FS, (tono + (0,) * int(0.9 * FS),))
    sin = procesar(programa("shimmer"), x, Controles(pots("0.6", "0.3", "1", "0"))).canales[0]
    con = procesar(programa("shimmer"), x, Controles(pots("0.6", "0.3", "1", "0.8"))).canales[0]
    ratio_sin = potencia(sin, 2 * f, 0.45, 1.1) / potencia(sin, f, 0.45, 1.1)
    ratio_con = potencia(con, 2 * f, 0.45, 1.1) / potencia(con, f, 0.45, 1.1)
    assert ratio_con > 5 * ratio_sin


def t60(v: tuple[int, ...]) -> float:
    """T60 en segundos, por la caída de nivel entre 0,2-0,4 s y 0,6-0,8 s."""
    caida_db = 20 * math.log10(rms(v, 0.2, 0.4) / rms(v, 0.6, 0.8))
    return 60 * 0.4 / caida_db


def test_hall_el_t60_sigue_a_pot0_y_es_estereo() -> None:
    corto = procesar(programa("hall"), impulso(1.0), Controles(pots("0.2", "0.3", "1")))
    largo = procesar(programa("hall"), impulso(1.0), Controles(pots("0.8", "0.3", "1")))
    izq, der = corto.canales
    assert 0.3 < t60(izq) < 1.0  # medido: 0,60 s
    assert t60(largo.canales[0]) > 2.5 * t60(izq)  # medido: 2,08 s
    assert izq[1000:20000] != der[1000:20000]


def test_cloud_la_modulacion_cambia_la_respuesta() -> None:
    """Sin modulación (pot3 = 0) el cloud es invariante: un impulso retrasado da la misma cola."""
    retraso = int(0.2 * FS)
    a, b = int(0.05 * FS), int(0.55 * FS)

    def colas(mod: str) -> tuple[tuple[int, ...], tuple[int, ...]]:
        c = Controles(pots("0.5", "0.3", "1", mod))
        y0 = procesar(programa("cloud"), impulso(0.8), c).canales[0]
        y1 = procesar(programa("cloud"), impulso(0.8, retraso), c).canales[0]
        return y0[a:b], y1[retraso + a : retraso + b]

    quieta, otra = colas("0")
    assert quieta == otra and rms(quieta, 0, 0.1) > 0
    modulada, otra = colas("1")
    diferencia = math.sqrt(sum((p - q) ** 2 for p, q in zip(modulada, otra, strict=True)))
    energia = math.sqrt(sum(p * p for p in modulada))
    assert diferencia > 0.3 * energia  # medido: 1,07


# Huellas bit-exact (sha256 de la salida estéreo de 0,1 s de impulso).
# Cambian si cambia la aritmética (ADR 0008), la ISA (ADR 0009) o el programa.
HUELLAS = {
    "plate": "7967b952e0f3b48a",
    "shimmer": "85d032aacbdeb748",
    "freeze": "8aaff05950123adf",
    "hall": "415e559bb7dd5042",
    "cloud": "496767ac991fd49c",
}


@pytest.mark.parametrize("nombre", sorted(HUELLAS))
def test_huella_bit_exact(nombre: str) -> None:
    y = procesar(programa(nombre), impulso(0.1), Controles(pots("0.5", "0.3", "0.5", "0.5")))
    datos = b"".join(v.to_bytes(3, "little", signed=True) for c in y.canales for v in c)
    assert hashlib.sha256(datos).hexdigest()[:16] == HUELLAS[nombre]
