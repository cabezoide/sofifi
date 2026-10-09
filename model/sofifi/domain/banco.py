# SPDX-License-Identifier: MIT
"""Banco de programas de la microSD: bloques crudos con ranuras fijas (Fase 08, ADR 0004).

La tarjeta no lleva sistema de ficheros: un parser de FAT en el RTL es caro y es
superficie de ataque (CWE-20, CWE-787). El formato es propio y pequeño:

1. **Bloque 0, cabecera:** ``MAGIA_BANCO``, versión, número de programas y el
   CRC-32 de esos campos.
2. **Ranura k:** empieza en el bloque ``1 + 28·k``.
   - 1 bloque de metadatos: ``MAGIA_RANURA``, nombre, instrucciones, memoria,
     LFOs y el CRC-32 de los metadatos y del microcódigo.
   - 27 bloques de microcódigo: hasta 2 048 palabras de 54 bit, empaquetadas
     sin huecos y en big-endian (13 824 bytes).

El lector nunca sigue posiciones escritas en la tarjeta: la ranura sale del
índice. Antes de devolver un programa comprueba la magia, la versión, los
límites de cada campo y los dos CRC. Un banco inválido no se carga
(``ErrorBanco``). El cargador RTL hará las mismas comprobaciones.

Los enteros van en big-endian. El CRC es el CRC-32 de zlib (el mismo que usa el
HIL, ``scripts/hil_nucleo.py``).
"""

from __future__ import annotations

import struct
import zlib
from collections.abc import Sequence

from sofifi.domain.aritmetica import CICLOS_POR_MUESTRA
from sofifi.domain.coste import ciclos_rtl
from sofifi.domain.isa import (
    BITS_PALABRA,
    MAX_INSTRUCCIONES,
    Programa,
    codificar,
    decodificar,
)
from sofifi.domain.lfo import NUM_LFOS, ConfigLfo, TipoLfo
from sofifi.domain.memoria import PALABRAS_MAX

BLOQUE = 512
BLOQUES_MICROCODIGO = MAX_INSTRUCCIONES * BITS_PALABRA // (8 * BLOQUE)  # 27
BLOQUES_RANURA = 1 + BLOQUES_MICROCODIGO  # 28
MAX_PROGRAMAS = 1024  # 28 673 bloques: unos 14 MB de la tarjeta
VERSION = 1
MAGIA_BANCO = b"SOFIFI\x00\x00"
MAGIA_RANURA = b"SOFIPROG"
LARGO_NOMBRE = 32

CODIGO_LFO = {TipoLfo.SIN: 0, TipoLfo.RND: 1, TipoLfo.RAMP: 2}
TIPO_LFO = {v: k for k, v in CODIGO_LFO.items()}
SIN_LFO = 0xFF

# Cabecera: magia, versión (u8), número de programas (u16) y CRC-32 (u32).
_CABECERA = struct.Struct(">8sBHI")
# Metadatos: magia, nombre, instrucciones (u16), memoria (u16), 4 × (tipo u8,
# excursión u16) y CRC-32 (u32) de los metadatos anteriores y del microcódigo.
_METADATOS = struct.Struct(">8s32sHH" + "BH" * NUM_LFOS + "I")

assert MAX_INSTRUCCIONES * BITS_PALABRA == 8 * BLOQUE * BLOQUES_MICROCODIGO


class ErrorBanco(ValueError):
    """El banco o la ranura no son válidos: no se cargan."""


def bytes_microcodigo(instrucciones: int) -> int:
    """Bytes que ocupan ``instrucciones`` palabras de 54 bit empaquetadas."""
    return (instrucciones * BITS_PALABRA + 7) // 8


def empaquetar(palabras: Sequence[int]) -> bytes:
    """Palabras de 54 bit, una detrás de otra, en big-endian y sin huecos."""
    total = 0
    for p in palabras:
        total = (total << BITS_PALABRA) | p
    bits = len(palabras) * BITS_PALABRA
    relleno = -bits % 8
    return (total << relleno).to_bytes((bits + relleno) // 8, "big")


def desempaquetar(datos: bytes, n: int) -> list[int]:
    bits = n * BITS_PALABRA
    total = int.from_bytes(datos[: bytes_microcodigo(n)], "big") >> (-bits % 8)
    mascara = (1 << BITS_PALABRA) - 1
    return [(total >> (BITS_PALABRA * (n - 1 - k))) & mascara for k in range(n)]


def _cabecera(numero: int) -> bytes:
    sin_crc = _CABECERA.pack(MAGIA_BANCO, VERSION, numero, 0)[:-4]
    return _CABECERA.pack(MAGIA_BANCO, VERSION, numero, zlib.crc32(sin_crc)).ljust(BLOQUE, b"\0")


def _ranura(programa: Programa) -> bytes:
    nombre = programa.nombre.encode("utf-8")
    if len(nombre) > LARGO_NOMBRE:
        raise ErrorBanco(f"'{programa.nombre}': el nombre pasa de {LARGO_NOMBRE} bytes")
    if ciclos_rtl(programa) > CICLOS_POR_MUESTRA:
        raise ErrorBanco(f"'{programa.nombre}': {ciclos_rtl(programa)} ciclos del RTL > 2 048")
    lfos: list[int] = []
    for c in programa.lfos:
        lfos += [SIN_LFO, 0] if c is None else [CODIGO_LFO[c.tipo], c.excursion]
    micro = empaquetar([codificar(i) for i in programa.instrucciones])
    campos = (MAGIA_RANURA, nombre, len(programa.instrucciones), programa.palabras_memoria, *lfos)
    sin_crc = _METADATOS.pack(*campos, 0)[:-4]
    meta = _METADATOS.pack(*campos, zlib.crc32(sin_crc + micro))
    return meta.ljust(BLOQUE, b"\0") + micro.ljust(BLOQUE * BLOQUES_MICROCODIGO, b"\0")


def escribir_banco(programas: Sequence[Programa]) -> bytes:
    """Imagen de la tarjeta: cabecera y una ranura por programa, en orden."""
    if not 1 <= len(programas) <= MAX_PROGRAMAS:
        raise ErrorBanco(f"un banco lleva de 1 a {MAX_PROGRAMAS} programas")
    return _cabecera(len(programas)) + b"".join(_ranura(p) for p in programas)


def leer_cabecera(bloque0: bytes) -> int:
    """Número de programas del banco. Falla si la cabecera no es válida."""
    if len(bloque0) < _CABECERA.size:
        raise ErrorBanco("cabecera incompleta")
    magia, version, numero, crc = _CABECERA.unpack_from(bloque0)
    if magia != MAGIA_BANCO:
        raise ErrorBanco("no es un banco de SOFIFI")
    if zlib.crc32(bloque0[: _CABECERA.size - 4]) != crc:
        raise ErrorBanco("CRC de la cabecera incorrecto")
    if version != VERSION:
        raise ErrorBanco(f"versión {version}; se espera {VERSION}")
    if not 1 <= numero <= MAX_PROGRAMAS:
        raise ErrorBanco(f"{numero} programas fuera de [1, {MAX_PROGRAMAS}]")
    return int(numero)


def bloque_ranura(k: int) -> int:
    """Primer bloque de la ranura ``k``: sale del índice, nunca de la tarjeta."""
    return 1 + BLOQUES_RANURA * k


def leer_programa(imagen: bytes, k: int) -> Programa:
    """El programa de la ranura ``k``, comprobado. Falla con ``ErrorBanco`` si no vale."""
    numero = leer_cabecera(imagen[:BLOQUE])
    if not 0 <= k < numero:
        raise ErrorBanco(f"ranura {k} fuera del banco ({numero} programas)")
    inicio = BLOQUE * bloque_ranura(k)
    meta = imagen[inicio : inicio + BLOQUE]
    if len(meta) < _METADATOS.size:
        raise ErrorBanco(f"ranura {k} incompleta")
    magia, nombre, n, palabras, *resto = _METADATOS.unpack_from(meta)
    lfos_crudos, crc = resto[:-1], resto[-1]
    if magia != MAGIA_RANURA:
        raise ErrorBanco(f"ranura {k}: sin la magia de programa")
    if not 1 <= n <= MAX_INSTRUCCIONES:
        raise ErrorBanco(f"ranura {k}: {n} instrucciones fuera de [1, {MAX_INSTRUCCIONES}]")
    if not 1 <= palabras <= PALABRAS_MAX:
        raise ErrorBanco(f"ranura {k}: memoria {palabras} fuera de [1, {PALABRAS_MAX}]")
    micro = imagen[inicio + BLOQUE : inicio + BLOQUE + bytes_microcodigo(n)]
    if len(micro) < bytes_microcodigo(n):
        raise ErrorBanco(f"ranura {k}: microcódigo incompleto")
    if zlib.crc32(meta[: _METADATOS.size - 4] + micro) != crc:
        raise ErrorBanco(f"ranura {k}: CRC incorrecto")
    lfos: list[ConfigLfo | None] = []
    for tipo, excursion in zip(lfos_crudos[0::2], lfos_crudos[1::2], strict=True):
        if tipo == SIN_LFO:
            lfos.append(None)
        elif tipo in TIPO_LFO and 1 <= excursion <= 16384:
            lfos.append(ConfigLfo(TIPO_LFO[tipo], excursion))
        else:
            raise ErrorBanco(f"ranura {k}: LFO no válido (tipo {tipo}, excursión {excursion})")
    try:
        texto = nombre.rstrip(b"\0").decode("utf-8")
        instrucciones = tuple(decodificar(p) for p in desempaquetar(micro, n))
        return Programa(texto, instrucciones, palabras, tuple(lfos))
    except ValueError as exc:  # código de operación desconocido, programa inválido
        raise ErrorBanco(f"ranura {k}: {exc}") from None
