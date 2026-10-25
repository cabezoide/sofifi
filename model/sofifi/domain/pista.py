# SPDX-License-Identifier: MIT
"""Pista de audio de la microSD: bloques crudos con muestras de 16 bit (Fase 13).

El pedal no tiene entrada de audio hasta la Fase 11, así que la fuente para oír
los programas en la placa es una grabación de la tarjeta (ADR 0004: la microSD
almacena, y una pista es almacenamiento). El formato es hermano del banco de
programas (``domain/banco.py``) y, como él, no lleva sistema de ficheros:

1. **Bloque 0, cabecera:** ``MAGIA``, versión, número de muestras y el CRC-32 de
   esos campos.
2. **Bloques 1 y siguientes:** muestras de 16 bit con signo, 256 por bloque, en
   big-endian. El último bloque se rellena con ceros.

El lector del RTL no sigue posiciones escritas en la tarjeta: el bloque sale de
la cuenta de muestras leídas. Comprueba la magia, la versión, el CRC-32 de la
cabecera y que el número de muestras cae en ``[1, MAX_MUESTRAS]``.

Las muestras no llevan CRC, y es a propósito: una muestra dañada es ruido, no un
riesgo. El microcódigo sí lo lleva, porque manda sobre el núcleo (SECURITY.md).

La pista se repite: al llegar al final, el lector vuelve al bloque 1. Así una
grabación de diez segundos suena sin parar. Por eso la pista tiene un mínimo de
``MIN_MUESTRAS``: con menos, cada vuelta lee un bloque entero para pocas
muestras y la cola del lector se queda sin datos.
"""

from __future__ import annotations

import struct
import zlib
from collections.abc import Sequence

BLOQUE = 512
MAGIA = b"SOFIPIST"
VERSION = 1
MUESTRA_BITS = 16
MUESTRAS_POR_BLOQUE = BLOQUE * 8 // MUESTRA_BITS  # 256
# Tope de muestras: el lector del RTL comprueba el mismo (dos bits altos a 0).
MAX_MUESTRAS = (1 << 30) - 1  # unas 6,1 horas de audio
# Mínimo: cada vuelta vuelve a leer un bloque entero, y leer un bloque tarda
# unos 33 000 ciclos, es decir 16 muestras de audio. Con un bloque completo por
# vuelta, el lector va 16 veces más rápido que el consumo.
MIN_MUESTRAS = MUESTRAS_POR_BLOQUE  # 256 muestras: 5,2 ms

# Cabecera: magia, versión (u8), muestras (u32) y CRC-32 (u32) de lo anterior.
_CABECERA = struct.Struct(">8sBI")
_CRC = struct.Struct(">I")

MUESTRA_MAX = (1 << (MUESTRA_BITS - 1)) - 1
MUESTRA_MIN = -1 - MUESTRA_MAX


class ErrorPista(ValueError):
    """La pista no es válida: no se reproduce."""


def bloques_de(muestras: int) -> int:
    """Bloques de datos que ocupan ``muestras`` muestras."""
    return (muestras + MUESTRAS_POR_BLOQUE - 1) // MUESTRAS_POR_BLOQUE


def escribir(muestras: Sequence[int]) -> bytes:
    """Imagen de la pista. ``muestras`` va en PCM de 16 bit con signo."""
    if not MIN_MUESTRAS <= len(muestras) <= MAX_MUESTRAS:
        raise ErrorPista(
            f"la pista tiene {len(muestras)} muestras, y van de {MIN_MUESTRAS} a {MAX_MUESTRAS}"
        )
    for valor in muestras:
        if not MUESTRA_MIN <= valor <= MUESTRA_MAX:
            raise ErrorPista(f"muestra fuera de 16 bit: {valor}")
    campos = _CABECERA.pack(MAGIA, VERSION, len(muestras))
    cabecera = campos + _CRC.pack(zlib.crc32(campos))
    datos = struct.pack(f">{len(muestras)}h", *muestras)
    relleno = bloques_de(len(muestras)) * BLOQUE - len(datos)
    return cabecera.ljust(BLOQUE, b"\x00") + datos + bytes(relleno)


def leer_cabecera(bloque: bytes) -> int:
    """Número de muestras de la pista. Falla si la cabecera no es válida."""
    if len(bloque) < BLOQUE:
        raise ErrorPista("la imagen no llega a un bloque")
    magia, version, muestras = _CABECERA.unpack_from(bloque)
    (crc,) = _CRC.unpack_from(bloque, _CABECERA.size)
    if magia != MAGIA:
        raise ErrorPista("magia distinta: la tarjeta no lleva una pista")
    if version != VERSION:
        raise ErrorPista(f"versión {version}, y se esperaba {VERSION}")
    if crc != zlib.crc32(bloque[: _CABECERA.size]):
        raise ErrorPista("CRC-32 de la cabecera incorrecto")
    if not 1 <= muestras <= MAX_MUESTRAS:
        raise ErrorPista(f"muestras fuera de rango: {muestras}")
    return int(muestras)


def leer(imagen: bytes) -> list[int]:
    """Muestras de la pista, en PCM de 16 bit con signo."""
    muestras = leer_cabecera(imagen[:BLOQUE])
    bloques = bloques_de(muestras)
    if len(imagen) < (1 + bloques) * BLOQUE:
        raise ErrorPista(
            f"la imagen necesita {1 + bloques} bloques y tiene {len(imagen) // BLOQUE}"
        )
    datos = imagen[BLOQUE : BLOQUE + 2 * muestras]
    return list(struct.unpack(f">{muestras}h", datos))


def muestra_a_dato(muestra: int, dato_frac: int = 23) -> int:
    """PCM de 16 bit → formato del núcleo (S.23). El RTL hace lo mismo: << 8."""
    return muestra << (dato_frac + 1 - MUESTRA_BITS)
