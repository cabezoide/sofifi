# SPDX-License-Identifier: MIT
"""Programas de la Fase 01: plate, shimmer y freeze.

Comprueban propiedades acústicas medibles (decae, se sostiene, sube una octava)
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
from sofifi.domain.aritmetica import DATO_MAX, UNO, dato
from sofifi.domain.ensamblador import ensamblar
from sofifi.domain.isa import Programa
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar

PROGRAMAS = Path(__file__).resolve().parents[2] / "programas"
FS = 48828


@cache
def programa(nombre: str) -> Programa:
    return ensamblar((PROGRAMAS / f"{nombre}.sasm").read_text(encoding="utf-8"), nombre)


def impulso(segundos: float) -> Senal:
    x = [0] * int(segundos * FS)
    x[0] = dato("0.5")
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


@pytest.mark.parametrize("nombre", ["plate", "shimmer", "freeze"])
def test_cabe_en_el_nucleo(nombre: str) -> None:
    p = programa(nombre)
    assert p.ciclos <= 2048
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


# Huellas bit-exact (sha256 de la salida estéreo de 0,1 s de impulso).
# Cambian si cambia la aritmética (ADR 0008), la ISA (ADR 0009) o el programa.
HUELLAS = {
    "plate": "7967b952e0f3b48a",
    "shimmer": "85d032aacbdeb748",
    "freeze": "8aaff05950123adf",
}


@pytest.mark.parametrize("nombre", sorted(HUELLAS))
def test_huella_bit_exact(nombre: str) -> None:
    y = procesar(programa(nombre), impulso(0.1), Controles(pots("0.5", "0.3", "0.5", "0.5")))
    datos = b"".join(v.to_bytes(3, "little", signed=True) for c in y.canales for v in c)
    assert hashlib.sha256(datos).hexdigest()[:16] == HUELLAS[nombre]
