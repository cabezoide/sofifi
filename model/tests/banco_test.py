# SPDX-License-Identifier: MIT
"""Banco de la microSD (Fase 08): lo que se escribe se lee igual, y lo corrupto se rechaza.

Criterio de aceptación de la fase: un banco corrupto (un bit volteado o una
longitud fuera de rango) no se carga. Las pruebas de longitud recalculan el
CRC, como haría quien escribe un banco a mano: el lector no se fía del CRC solo.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from sofifi.adapters.archivos import ensamblar_archivo
from sofifi.domain.banco import (
    BLOQUE,
    BLOQUES_RANURA,
    MAX_PROGRAMAS,
    ErrorBanco,
    bloque_ranura,
    bytes_microcodigo,
    desempaquetar,
    empaquetar,
    escribir_banco,
    leer_cabecera,
    leer_programa,
)
from sofifi.domain.isa import Instruccion, Op, Programa

RAIZ = Path(__file__).resolve().parents[2]
PROGRAMAS = tuple(ensamblar_archivo(r) for r in sorted((RAIZ / "programas").glob("*.sasm")))
PEQUENOS = tuple(p for p in PROGRAMAS if p.nombre in ("tremolo", "plate", "looper", "chorus"))
IMAGEN = escribir_banco(PEQUENOS)
META = struct.Struct(">8s32sHH" + "BH" * 4 + "I")  # el formato de banco.py


def test_todos_los_programas_van_y_vuelven() -> None:
    imagen = escribir_banco(PROGRAMAS)
    assert len(imagen) == BLOQUE * (1 + BLOQUES_RANURA * len(PROGRAMAS))
    assert leer_cabecera(imagen[:BLOQUE]) == len(PROGRAMAS)
    for k, p in enumerate(PROGRAMAS):
        assert leer_programa(imagen, k) == p


@given(st.lists(st.integers(0, (1 << 54) - 1), min_size=1, max_size=40))
def test_empaquetar_es_reversible(palabras: list[int]) -> None:
    datos = empaquetar(palabras)
    assert len(datos) == bytes_microcodigo(len(palabras))
    assert desempaquetar(datos, len(palabras)) == palabras


def test_dos_mil_palabras_llenan_27_bloques() -> None:
    assert bytes_microcodigo(2048) == 27 * BLOQUE


def _voltear(imagen: bytes, bit: int) -> bytes:
    datos = bytearray(imagen)
    datos[bit // 8] ^= 0x80 >> (bit % 8)
    return bytes(datos)


@settings(max_examples=300)
@given(st.integers(0, 8 * 15 - 1))
def test_un_bit_volteado_en_la_cabecera_se_rechaza(bit: int) -> None:
    with pytest.raises(ErrorBanco):
        leer_programa(_voltear(IMAGEN, bit), 0)


@settings(max_examples=500)
@given(st.data())
def test_un_bit_volteado_en_una_ranura_se_rechaza(data: st.DataObject) -> None:
    """Metadatos o microcódigo: el CRC-32 detecta cualquier error de un bit."""
    k = data.draw(st.integers(0, len(PEQUENOS) - 1))
    inicio = BLOQUE * bloque_ranura(k)
    util = [(inicio, META.size)]  # metadatos, sin el relleno del bloque
    util.append((inicio + BLOQUE, bytes_microcodigo(len(PEQUENOS[k].instrucciones))))
    desde, largo = data.draw(st.sampled_from(util))
    bit = 8 * desde + data.draw(st.integers(0, 8 * largo - 1))
    with pytest.raises(ErrorBanco):
        leer_programa(_voltear(IMAGEN, bit), k)


def _con_meta(k: int, **cambios: int) -> bytes:
    """La imagen con un campo de metadatos cambiado y el CRC recalculado."""
    inicio = BLOQUE * bloque_ranura(k)
    campos = list(META.unpack_from(IMAGEN, inicio))
    posicion = {"instrucciones": 2, "palabras": 3, "tipo_lfo0": 4, "excursion_lfo0": 5}
    for nombre, valor in cambios.items():
        campos[posicion[nombre]] = valor
    n = campos[2]
    micro = IMAGEN[inicio + BLOQUE : inicio + BLOQUE + min(bytes_microcodigo(n), 27 * BLOQUE)]
    sin_crc = META.pack(*campos[:-1], 0)[:-4]
    meta = META.pack(*campos[:-1], zlib.crc32(sin_crc + micro))
    return IMAGEN[:inicio] + meta + IMAGEN[inicio + META.size :]


@pytest.mark.parametrize(
    "cambios",
    [
        {"instrucciones": 0},
        {"instrucciones": 2049},
        {"instrucciones": 0xFFFF},
        {"palabras": 0},
        {"palabras": 43009},
        {"tipo_lfo0": 7},
        {"tipo_lfo0": 0, "excursion_lfo0": 0},
        {"tipo_lfo0": 0, "excursion_lfo0": 16385},
    ],
)
def test_un_campo_fuera_de_rango_se_rechaza_aunque_el_crc_cuadre(cambios: dict[str, int]) -> None:
    with pytest.raises(ErrorBanco):
        leer_programa(_con_meta(0, **cambios), 0)


def test_un_programa_invalido_con_crc_correcto_se_rechaza() -> None:
    """El plate con 1 palabra de memoria: sus direcciones quedan fuera (lo comprueba Programa)."""
    plate = next(k for k, p in enumerate(PEQUENOS) if p.nombre == "plate")
    with pytest.raises(ErrorBanco, match="fuera de la memoria"):
        leer_programa(_con_meta(plate, palabras=1), plate)


def test_la_ranura_sale_del_indice_y_se_comprueba() -> None:
    with pytest.raises(ErrorBanco, match="fuera del banco"):
        leer_programa(IMAGEN, len(PEQUENOS))
    with pytest.raises(ErrorBanco, match="fuera del banco"):
        leer_programa(IMAGEN, -1)
    with pytest.raises(ErrorBanco, match="incompleta"):
        leer_programa(IMAGEN[: BLOQUE * bloque_ranura(len(PEQUENOS) - 1) + 10], len(PEQUENOS) - 1)


def test_la_cabecera_rechaza_lo_que_no_es_un_banco() -> None:
    with pytest.raises(ErrorBanco, match="no es un banco"):
        leer_cabecera(bytes(BLOQUE))
    with pytest.raises(ErrorBanco, match="incompleta"):
        leer_cabecera(b"SOFIFI")


def test_escribir_comprueba_los_limites() -> None:
    with pytest.raises(ErrorBanco, match="de 1 a"):
        escribir_banco([])
    with pytest.raises(ErrorBanco, match="de 1 a"):
        escribir_banco([PEQUENOS[0]] * (MAX_PROGRAMAS + 1))
    largo = Programa("x" * 33, (Instruccion(Op.NOP),), 1)
    with pytest.raises(ErrorBanco, match="nombre"):
        escribir_banco([largo])
