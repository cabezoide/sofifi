# SPDX-License-Identifier: MIT
"""Memoria de retardo circular, como la del FV-1 (ADR 0004, ADR 0008).

Una sola memoria por programa. El puntero de escritura **decrementa** una vez
por muestra, así que lo escrito en la dirección ``a`` se lee en la dirección
``a + N`` exactamente ``N`` muestras después. Las palabras son de 18 bit
(BSRAM en modo 1K×18) y se guardan alineadas a dato.
"""

from __future__ import annotations

from sofifi.domain.aritmetica import acc_a_dato, dato_a_memoria

# 56 bloques de BSRAM menos 14 de reserva (CPU, microcódigo, FIFOs, tablas).
BLOQUES_MEMORIA = 42
PALABRAS_POR_BLOQUE = 1024
PALABRAS_MAX = BLOQUES_MEMORIA * PALABRAS_POR_BLOQUE
# Región absoluta (RDAA, WRAA; ADR 0009): detrás de la circular, sin puntero.
PALABRAS_ABSOLUTAS = 1 << 15
MASCARA_ABSOLUTA = PALABRAS_ABSOLUTAS - 1


class MemoriaRetardo:
    def __init__(self, palabras: int, absoluta: bool = False) -> None:
        if not 1 <= palabras <= PALABRAS_MAX:
            raise ValueError(f"memoria de {palabras} palabras fuera de [1, {PALABRAS_MAX}]")
        self.palabras = palabras
        self._celdas = [0] * palabras
        self._puntero = 0
        self._absoluta = [0] * (PALABRAS_ABSOLUTAS if absoluta else 0)

    def leer_absoluta(self, origen: int, posicion: int) -> int:
        """Lectura lineal en la región absoluta (RDAA, ADR 0009).

        ``posicion`` es el registro R: 15 bit de entero y 8 de fracción en sus 23
        bit bajos. Las direcciones se enmascaran: la región es circular por sí sola.
        """
        pos = posicion & 0x7FFFFF
        i = (origen + (pos >> 8)) & MASCARA_ABSOLUTA
        f = pos & 0xFF
        m0 = self._absoluta[i]
        m1 = self._absoluta[(i + 1) & MASCARA_ABSOLUTA]
        return m0 + (((m1 - m0) * f) >> 8)

    def escribir_absoluta(self, origen: int, posicion: int, valor: int) -> None:
        """Escritura en la región absoluta (WRAA): sin interpolar, en la parte entera."""
        i = (origen + ((posicion & 0x7FFFFF) >> 8)) & MASCARA_ABSOLUTA
        self._absoluta[i] = dato_a_memoria(valor)

    def _fisica(self, direccion: int) -> int:
        return (self._puntero + direccion) % self.palabras

    def leer(self, direccion: int) -> int:
        return self._celdas[self._fisica(direccion)]

    def escribir(self, direccion: int, valor: int) -> None:
        self._celdas[self._fisica(direccion)] = dato_a_memoria(valor)

    def avanzar(self) -> None:
        """Fin de muestra: el puntero retrocede una palabra."""
        self._puntero = (self._puntero - 1) % self.palabras

    def leer_interpolado(
        self, base: int, desplazamiento_q8: int, tabla: list[tuple[int, ...]]
    ) -> int:
        """Lee en ``base + desplazamiento_q8 / 256`` con Hermite de 4 puntos.

        ``tabla[f]`` da los cuatro coeficientes S1.16 para la fracción ``f/256``
        (ver ``interpolacion.py``). Suma en ACC y redondea a dato una sola vez.
        """
        entero = base + (desplazamiento_q8 >> 8)
        fraccion = desplazamiento_q8 & 0xFF
        c = tabla[fraccion]
        suma = 0
        for k in range(4):
            suma += self.leer(entero - 1 + k) * c[k]
        return acc_a_dato(suma)
