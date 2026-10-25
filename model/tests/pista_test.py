# SPDX-License-Identifier: MIT
"""Pista de audio de la microSD (Fase 13): ida y vuelta, y rechazo de lo inválido."""

from __future__ import annotations

import struct
import zlib
from collections.abc import Callable

import pytest
from hypothesis import given
from hypothesis import strategies as st
from sofifi.domain.pista import (
    BLOQUE,
    MAGIA,
    MAX_MUESTRAS,
    MIN_MUESTRAS,
    MUESTRA_MAX,
    MUESTRA_MIN,
    MUESTRAS_POR_BLOQUE,
    VERSION,
    ErrorPista,
    bloques_de,
    escribir,
    leer,
    leer_cabecera,
    muestra_a_dato,
)

# La pista más corta que admite el lector, con los extremos del rango al final.
MUESTRAS = [k * 11 - 1000 for k in range(MIN_MUESTRAS - 4)] + [
    0,
    MUESTRA_MAX,
    MUESTRA_MIN,
    -1,
]


def test_ida_y_vuelta() -> None:
    assert leer(escribir(MUESTRAS)) == MUESTRAS


def test_la_imagen_ocupa_bloques_enteros() -> None:
    imagen = escribir(MUESTRAS)
    assert len(imagen) == (1 + bloques_de(len(MUESTRAS))) * BLOQUE
    assert leer_cabecera(imagen[:BLOQUE]) == len(MUESTRAS)


def test_bloques_de() -> None:
    assert bloques_de(1) == 1
    assert bloques_de(MUESTRAS_POR_BLOQUE) == 1
    assert bloques_de(MUESTRAS_POR_BLOQUE + 1) == 2


def test_muestra_a_dato() -> None:
    assert muestra_a_dato(1) == 1 << 8
    assert muestra_a_dato(-1) == -(1 << 8)
    assert muestra_a_dato(MUESTRA_MAX) == (1 << 23) - (1 << 8)


@pytest.mark.parametrize(
    ("motivo", "cambio"),
    [
        ("magia", lambda i: b"OTRACOSA" + i[8:]),
        ("versión", lambda i: i[:8] + bytes([VERSION + 1]) + i[9:]),
        ("crc", lambda i: i[:13] + bytes([i[13] ^ 0x80]) + i[14:]),
        ("muestras", lambda i: _con_muestras(i, 0)),
        ("tope", lambda i: _con_muestras(i, MAX_MUESTRAS + 1)),
    ],
)
def test_rechaza_una_cabecera_invalida(motivo: str, cambio: Callable[[bytes], bytes]) -> None:
    with pytest.raises(ErrorPista):
        leer(cambio(escribir(MUESTRAS)))
    assert motivo  # el motivo está en el id de la prueba


def _con_muestras(imagen: bytes, muestras: int) -> bytes:
    """Reescribe el número de muestras y su CRC: la cabecera sigue siendo coherente."""
    campos = struct.pack(">8sBI", MAGIA, VERSION, muestras)
    return campos + struct.pack(">I", zlib.crc32(campos)) + imagen[17:]


def test_rechaza_una_imagen_corta() -> None:
    imagen = escribir(MUESTRAS)
    with pytest.raises(ErrorPista):
        leer(imagen[: 2 * BLOQUE - 1])
    with pytest.raises(ErrorPista):
        leer_cabecera(b"")


def test_rechaza_muestras_imposibles() -> None:
    with pytest.raises(ErrorPista):
        escribir([])
    with pytest.raises(ErrorPista):
        escribir(MUESTRAS[:-1])  # una menos que el mínimo
    with pytest.raises(ErrorPista):
        escribir([MUESTRA_MAX + 1] * MIN_MUESTRAS)


@given(st.lists(st.integers(MUESTRA_MIN, MUESTRA_MAX), min_size=MIN_MUESTRAS, max_size=600))
def test_ida_y_vuelta_de_cualquier_pista(muestras: list[int]) -> None:
    assert leer(escribir(muestras)) == muestras


@given(st.integers(0, 4 * BLOQUE - 1))
def test_un_bit_volteado_no_cuela_en_la_cabecera(posicion: int) -> None:
    """Un bit volteado en la cabecera se rechaza; en las muestras, solo es ruido."""
    imagen = bytearray(escribir([k % 3000 for k in range(600)]))
    assert len(imagen) == 4 * BLOQUE  # 1 de cabecera y 3 de datos
    imagen[posicion] ^= 1 << (posicion % 8)
    if posicion < 17:
        with pytest.raises(ErrorPista):
            leer(bytes(imagen))
    else:
        assert len(leer(bytes(imagen))) == 600
