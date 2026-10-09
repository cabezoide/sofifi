# SPDX-License-Identifier: MIT
"""Programas del núcleo: plate, shimmer y freeze (Fase 01); el resto, de la Fase 06.

Comprueban propiedades acústicas medibles (decae, se sostiene, sube una octava,
el decay sigue al potenciómetro, la modulación cambia la respuesta, el eco
llega cuando dice pot0, la señal sale al revés, hay menos muestras y menos
bits, cada nota empieza en silencio)
y una **huella bit-exact** por programa: cambiar la aritmética, la ISA o un
programa cambia la huella, y actualizarla es una decisión que se ve en el diff.
No comprueban que suene bonito: eso se escucha (ver `sofifi render`).
"""

from __future__ import annotations

import hashlib
import math
from itertools import pairwise

import pytest
from sofifi.domain.aritmetica import DATO_MAX, dato
from sofifi.domain.coste import cabe_en_el_rtl, ciclos_rtl
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import (
    FS,
    PROGRAMAS_TODOS,
    impulso,
    maximos,
    potencia,
    pots,
    programa,
    rms,
    tono,
)


@pytest.mark.parametrize("nombre", PROGRAMAS_TODOS)
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
    retraso = int(0.1 * FS)
    a, b = int(0.05 * FS), int(0.3 * FS)

    def colas(mod: str) -> tuple[tuple[int, ...], tuple[int, ...]]:
        c = Controles(pots("0.5", "0.3", "1", mod))
        y0 = procesar(programa("cloud"), impulso(0.4), c).canales[0]
        y1 = procesar(programa("cloud"), impulso(0.4, retraso), c).canales[0]
        return y0[a:b], y1[retraso + a : retraso + b]

    quieta, otra = colas("0")
    assert quieta == otra and rms(quieta, 0, 0.1) > 0
    modulada, otra = colas("1")
    diferencia = math.sqrt(sum((p - q) ** 2 for p, q in zip(modulada, otra, strict=True)))
    energia = math.sqrt(sum(p * p for p in modulada))
    assert diferencia > 0.3 * energia  # medido: 0,98


def test_cinta_el_eco_llega_cuando_dice_pot0() -> None:
    """El LFO del tiempo se desliza ~40 ms; el impulso llega a los 0,6 s, ya quieto."""
    entrada = int(0.6 * FS)
    largo = procesar(
        programa("cinta"), impulso(1.5, entrada), Controles(pots("1", "0.5", "1", "0"))
    ).canales[0]
    (eco,) = maximos(largo, 0.1)
    assert abs((eco - entrada) / FS - 0.8505) < 0.002
    corto = procesar(
        programa("cinta"), impulso(1.2, entrada), Controles(pots("0", "0.5", "1", "0"))
    ).canales[0]
    ecos = maximos(corto, 0.01)
    niveles = [corto[k] for k in ecos]
    # La realimentación repite el eco cada 0,18 s, y cada vez más bajo.
    tiempos = [(k - entrada) / FS for k in ecos]
    assert len(tiempos) == 3
    assert all(abs(t - 0.1799 * n) < 0.002 for n, t in enumerate(tiempos, start=1))
    assert niveles[0] > 2 * niveles[1] > 4 * niveles[2] > 0


def test_cinta_satura_sin_desbocarse() -> None:
    """Con realimentación 1 y entrada fuerte, CLIP sostiene el eco sin pasar del tope."""
    n = int(0.3 * FS)
    tono = tuple(dato(str(round(0.9 * math.sin(2 * math.pi * 220 * k / FS), 6))) for k in range(n))
    x = Senal(FS, (tono + (0,) * int(0.9 * FS),))
    y = procesar(programa("cinta"), x, Controles(pots("0", "1", "1", "0"))).canales[0]
    assert max(abs(v) for v in y) <= DATO_MAX
    assert 0.05 < rms(y, 0.8, 1.2) < 1.0


def test_reverse_saca_la_senal_al_reves() -> None:
    """Dos impulsos, A y después B: en la salida, B llega antes que A y a la misma distancia."""
    distancia = 1000
    x = [0] * FS
    t0 = int(0.3 * FS)
    x[t0], x[t0 + distancia] = dato("0.5"), dato("-0.25")
    y = procesar(programa("reverse"), Senal(FS, (tuple(x),)), Controles(pots("1", "0", "1")))
    a, b = maximos(y.canales[0], 0.01), maximos(y.canales[0], 0.005, -1)
    invertidos = sum(1 for p in a for q in b if abs(p - q - distancia) <= 2)
    directos = sum(1 for p in a for q in b if abs(q - p - distancia) <= 2)
    assert invertidos >= 1 and directos == 0  # medido: 2 granos, los dos invertidos


def test_lofi_reduce_muestras_y_bits() -> None:
    """La entrada va por la derecha: la salida izquierda solo lleva lo-fi, sin señal seca."""
    x = tono(220, 0.2)
    entrada = Senal(FS, ((0,) * len(x), x))

    def salida(muestreo: str, bits: str) -> tuple[int, ...]:
        c = Controles(pots(muestreo, bits, "1", "1"))
        return procesar(programa("lofi"), entrada, c).canales[0][2000:]

    def cambios(v: tuple[int, ...]) -> float:
        return sum(1 for a, b in pairwise(v) if a != b) / len(v)

    assert cambios(salida("0", "0")) > 0.99
    assert 0.015 < cambios(salida("1", "0")) < 0.025  # 1 de cada 50 muestras
    for bits, pot in ((7, "1"), (8, "0.7"), (10, "0.5"), (12, "0.3")):
        niveles = len(set(salida("0", pot)))
        assert 2 ** (bits - 2) < niveles <= 2**bits  # medido: 117, 231, 923, 3 687


def test_swell_cada_nota_empieza_en_silencio() -> None:
    """Dos notas pulsadas: a la entrada, el ataque es lo más fuerte; a la salida, lo más débil."""
    x = [0.0] * int(1.6 * FS)
    for t in (0.2, 0.9):
        k0 = int(t * FS)
        for i in range(int(0.65 * FS)):
            x[k0 + i] += 0.5 * math.exp(-i / FS / 0.4) * math.sin(2 * math.pi * 196 * i / FS)
    entrada = tuple(dato(str(round(v, 6))) for v in x)
    y = procesar(programa("swell"), Senal(FS, (entrada,)), Controles(pots("0.5", "0.3", "0", "0")))
    for t in (0.2, 0.9):
        assert rms(entrada, t, t + 0.01) > rms(entrada, t + 0.15, t + 0.25)
        assert rms(y.canales[0], t, t + 0.01) < 0.3 * rms(y.canales[0], t + 0.15, t + 0.25)


# Huellas bit-exact (sha256 de la salida estéreo de 0,1 s de impulso; más en
# los ecos, que tardan más de 0,1 s en sonar; un tono en lofi y swell, que con
# un impulso casi no suenan).
# Cambian si cambia la aritmética (ADR 0008), la ISA (ADR 0009) o el programa.
HUELLAS = {
    "granular": "5bab1e168ac461df",
    "looper": "f4b95ce672872ac4",
    "plate": "7967b952e0f3b48a",
    "shimmer": "85d032aacbdeb748",
    "freeze": "8aaff05950123adf",
    "hall": "415e559bb7dd5042",
    "cloud": "496767ac991fd49c",
    "cinta": "1b1f06252a1762ad",
    "reverse": "2f113ede645767d1",
    "lofi": "a4d6a87f66648356",
    "swell": "627e231396b504fa",
    "chorus": "751ad4420cef058d",
    "flanger": "cb4159f30e5bed32",
    "phaser": "f56d3cf9add10ab7",
    "tremolo": "1b6fc45fd6e309e6",
    "vibrato": "82980fc514ddf04c",
    "armonizador": "b09fcc26a86dbd5b",
    "doblador": "cd0ae0b848845c18",
    "escalera": "63c082164fefbd79",
    "octava": "9db69730833af9a6",
    "shimmer_quinta": "2ffc6c5bd7ddb4bf",
    "blackhole": "910ad8eed7ac34cd",
    "bloom": "0ce2ef3235e80bc3",
    "gated": "ac97c811894386d9",
    "infinite": "cab794fe727bc8ec",
    "reverb_inversa": "f6a907eefc2b7311",
    "spring": "c20eeffbf37f0c0f",
    "bbd": "1aa104b5c924569c",
    "delay": "690cbdebb0af818d",
    "ducking": "5d88112b3b9612ee",
    "lluvia": "789293f5934ee1b4",
    "pingpong": "628f30ffda3cd500",
    "autowah": "411f7e3d60c07677",
    "compresor": "2e17d632f953623c",
    "filtro": "ff8a6846cc9478cf",
    "puerta": "62aed0a4198303de",
    "saturacion": "afe17ca65691cfc1",
    "ancho": "c4b73a1ac2872ead",
    "chorale": "1345471d772e16c5",
    "resonador": "ef187741375a3185",
    "ringmod": "341b5c04807e4c42",
    "slicer": "6b8940ad32b691cd",
    "freeze_givens": "6892e89b0742c85f",
    "plate_vivo": "b01a538673d1475f",
    "shimmer_energia": "3eb9961314f955ba",
    "shimmer_grave": "da494595b375be4c",
    "marea": "a4c4a5dc5757534a",
    "ensemble": "fe6abfbc1db9e72e",
    "sostenido": "763109b6d96e55af",
    "shoegaze": "bb1e25cca088c986",
    "bruma": "2e6661ec9122cde7",
    "armonico": "23463ed15dbf6ab4",
    "arcoiris": "dee201eb880e202e",
    "tambor": "1f1e2019cced53cb",
    "mosaico": "a6d48be05b31d041",
    "erosion": "28774e5b2dc4dbbe",
    "desplazador": "98bedfe6554d4343",
    "violin": "e85cd8cdd38066ef",
    "shimmer_escondido": "70a5d7f170b3e906",
    "arco": "2c4983b7c802efae",
    "oscilador": "8e906592fdb882c9",
    "dinamica": "e9753e942a929dcc",
    "acople": "a82c064a0ae3a4ac",
}


SEGUNDOS_HUELLA = {
    "cinta": 0.6,
    "reverse": 0.4,
    "escalera": 0.6,
    "blackhole": 0.3,
    "delay": 0.5,
    "pingpong": 0.5,
    "bbd": 0.3,
    "ducking": 0.5,
    "freeze_givens": 0.5,
    "looper": 0.3,
    "granular": 0.5,
    "bruma": 0.3,
    "tambor": 0.4,
    "mosaico": 0.5,
    "erosion": 0.3,
    "desplazador": 0.4,
    "violin": 0.6,
    "oscilador": 0.3,
    "dinamica": 0.6,
}
# Con pot3 = 0,5, dinamica no actúa y da los mismos bits que freeze sin pulsar.
POTS_HUELLA = {"dinamica": ("0.5", "0.3", "0.5", "0.9")}
# Sin footswitch, el looper solo deja pasar la señal seca: graba los primeros 0,1 s.
TRAMOS_SW = {
    "acople": ((0, int(0.3 * FS)),),
    "looper": ((0, int(0.1 * FS)),),
    "erosion": ((0, int(0.1 * FS)),),
}
CON_TONO = {
    "lofi",
    "swell",
    "tremolo",
    "gated",
    "reverb_inversa",
    "compresor",
    "puerta",
    "saturacion",
    "ringmod",
    "slicer",
    "looper",
    "granular",
    "sostenido",
    "armonico",
    "arcoiris",
    "mosaico",
    "erosion",
    "violin",
    "arco",
    "acople",
    "dinamica",
}


def test_todo_programa_tiene_huella() -> None:
    assert sorted(HUELLAS) == PROGRAMAS_TODOS


def test_las_huellas_son_distintas() -> None:
    """Dos huellas iguales suelen ser solo señal seca: el estímulo no llegó al efecto."""
    assert len(set(HUELLAS.values())) == len(HUELLAS)


@pytest.mark.parametrize("nombre", sorted(HUELLAS))
def test_huella_bit_exact(nombre: str) -> None:
    if nombre in CON_TONO:
        x = Senal(FS, (tono(196, SEGUNDOS_HUELLA.get(nombre, 0.3), 0.5),))
    else:
        x = impulso(SEGUNDOS_HUELLA.get(nombre, 0.1))
    mandos = POTS_HUELLA.get(nombre, ("0.5", "0.3", "0.5", "0.5"))
    c = Controles(pots(*mandos), tramos_sw=TRAMOS_SW.get(nombre, ()))
    y = procesar(programa(nombre), x, c)
    datos = b"".join(v.to_bytes(3, "little", signed=True) for c in y.canales for v in c)
    assert hashlib.sha256(datos).hexdigest()[:16] == HUELLAS[nombre]
