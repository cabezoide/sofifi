# SPDX-License-Identifier: MIT
"""Modelo de tarjeta SD en modo SPI para cocotb (Fase 08).

Responde a CMD0, CMD8, CMD55, ACMD41, CMD58 y CMD17 sobre una imagen en memoria.
Lee MOSI en el flanco de subida de SCK y cambia MISO en el de bajada (modo 0).
Cada respuesta va detrás de un byte 0xFF (Ncr = 1). Las variantes sirven para
probar los errores del controlador.
"""

from __future__ import annotations

from dataclasses import dataclass

import cocotb
from cocotb.triggers import Edge


@dataclass
class Variante:
    sdhc: bool = True  # dirección de bloque (CCS = 1); False: SDSC, de byte
    version1: bool = False  # CMD8 da «comando ilegal»
    ocupada: int = 3  # respuestas 0x01 a ACMD41 antes de 0x00; -1: nunca lista
    token_malo: bool = False  # CMD17 responde con un token de error


class TarjetaSD:
    def __init__(self, dut: cocotb.handle.HierarchyObject, imagen: bytes, v: Variante) -> None:
        self.dut, self.imagen, self.v = dut, imagen, v
        self.salida: list[int] = []  # bits pendientes de MISO
        self.comando: list[int] = []
        self.byte, self.bits = 0, 0
        self.acmd = False
        self.intentos = 0
        self.lecturas: list[int] = []  # bloques leídos, para las pruebas

    def _responder(self, *octetos: int) -> None:
        for o in (0xFF, *octetos):
            self.salida += [(o >> (7 - k)) & 1 for k in range(8)]

    def _procesar(self, trama: list[int]) -> None:
        indice = trama[0] & 0x3F
        arg = int.from_bytes(bytes(trama[1:5]), "big")
        acmd, self.acmd = self.acmd, False
        if indice == 0:
            self._responder(0x01)
        elif indice == 8:
            if self.v.version1:
                self._responder(0x05)
            else:
                self._responder(0x01, 0x00, 0x00, (arg >> 8) & 0x0F, arg & 0xFF)
        elif indice == 55:
            self.acmd = True
            self._responder(0x01 if self.intentos <= self.v.ocupada else 0x00)
        elif indice == 41 and acmd:
            lista = self.v.ocupada >= 0 and self.intentos >= self.v.ocupada
            self.intentos += 1
            self._responder(0x00 if lista else 0x01)
        elif indice == 58:
            ocr = (1 << 31) | (int(self.v.sdhc) << 30) | (1 << 20)
            self._responder(0x00, *ocr.to_bytes(4, "big"))
        elif indice == 17:
            bloque = arg if self.v.sdhc else arg // 512
            self.lecturas.append(bloque)
            if self.v.token_malo:
                self._responder(0x00, 0xFF, 0x01)
                return
            datos = self.imagen[512 * bloque : 512 * bloque + 512].ljust(512, b"\0")
            self._responder(0x00, 0xFF, 0xFF, 0xFE, *datos, 0x12, 0x34)
        else:
            self._responder(0x04)  # comando ilegal

    async def correr(self) -> None:
        self.dut.sd_miso.value = 1
        while True:
            await Edge(self.dut.sd_sck)
            if int(self.dut.sd_cs_n.value):
                self.bits, self.byte, self.comando = 0, 0, []
                continue
            if int(self.dut.sd_sck.value):  # subida: lee MOSI
                self.byte = ((self.byte << 1) | int(self.dut.sd_mosi.value)) & 0xFF
                self.bits += 1
                if self.bits == 8:
                    self.bits = 0
                    if self.comando or (self.byte & 0xC0) == 0x40:
                        self.comando.append(self.byte)
                        if len(self.comando) == 6:
                            self._procesar(self.comando)
                            self.comando = []
            else:  # bajada: siguiente bit de MISO
                self.dut.sd_miso.value = self.salida.pop(0) if self.salida else 1
