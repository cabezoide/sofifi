# SPDX-License-Identifier: MIT
"""Salida de audio de 1 bit: interpolador CIC y modulador sigma-delta (ADR 0015).

El reloj es 2 048 veces fs (ADR 0005), así que un solo pin lleva audio::

    muestra S.23 a fs ─► recorte ─► CIC S=2, R=32 ─► mantenimiento ×64 ─► Σ∆ ─► 1 bit
                                      32·fs              100 MHz        2.º orden

Este módulo es el oráculo de ``rtl/salida/`` (ADR 0003). Las tres clases
corresponden una a una con los tres módulos del RTL.

El interpolador es un filtro CIC de Hogenauer: dos peines a fs y dos
integradores a 32·fs, sin multiplicadores. Su ganancia es ``R^(S-1) = 32``, y no
``R^S``, porque el relleno de ceros divide por ``R``.

Origen del algoritmo: U. Meyer-Baese, *Digital Signal Processing with Field
Programmable Gate Arrays*, 3.ª ed., §5.3 (filtros CIC de Hogenauer). Estudiado,
no portado (ADR 0002); ver ``docs/terceros.yaml``.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from sofifi.domain.aritmetica import CICLOS_POR_MUESTRA, UNO, saturar

INTERPOLACION = 32  # R del CIC: fs -> 32·fs
ORDEN_CIC = 2  # S del CIC: dos peines y dos integradores
MANTENIMIENTO = CICLOS_POR_MUESTRA // INTERPOLACION  # 64 ciclos por valor
GANANCIA_CIC = 5  # log2(R^(S-1)); el relleno de ceros divide por R
CIC_BITS = 32  # acumuladores del CIC, en aritmética modular
CIC_MASCARA = (1 << CIC_BITS) - 1
ALTO_BITS = CIC_BITS - GANANCIA_CIC  # 27: la salida del CIC, a 32·fs

# Recorte de seguridad: con la entrada a escala plena el modulador sale de su
# zona lineal, y un programa de la microSD puede saturar a ±1 (SECURITY.md).
LIMITE = 13 * UNO // 16  # 0,8125 de escala plena

MOD_BITS = 28  # integradores del modulador, con saturación
K1 = 1  # realimentación al primer integrador
K2 = 4  # realimentación al segundo; con K2 = 2 la SNR cae más (ADR 0015)


def recortar(muestra: int) -> int:
    """Acota la muestra al rango seguro del modulador."""
    if muestra > LIMITE:
        return LIMITE
    return -LIMITE if muestra < -LIMITE else muestra


def _con_signo(valor: int) -> int:
    """Interpreta un acumulador del CIC como entero con signo."""
    if valor >> (CIC_BITS - 1):
        return valor - (1 << CIC_BITS)
    return valor


class InterpoladorCIC:
    """CIC de Hogenauer, S = 2 y R = 32. Equivale a ``rtl/salida/cic_interp.v``.

    Cada ``muestra`` devuelve 32 valores en S.23, a 32·fs. Los peines corren a
    fs y los integradores a 32·fs. Los acumuladores son modulares: los valores
    reales caben en 30 bit, así que nunca envuelven.
    """

    def __init__(self) -> None:
        self.peine1 = 0  # x[n-1]
        self.peine2 = 0  # d1[n-1]
        self.integra1 = 0
        self.integra2 = 0

    def muestra(self, x: int) -> list[int]:
        d1 = x - self.peine1
        self.peine1 = x
        d2 = d1 - self.peine2
        self.peine2 = d1
        salida = []
        for paso in range(INTERPOLACION):
            entrada = d2 if paso == 0 else 0  # relleno de ceros
            self.integra1 = (self.integra1 + entrada) & CIC_MASCARA
            self.integra2 = (self.integra2 + _con_signo(self.integra1)) & CIC_MASCARA
            salida.append(_con_signo(self.integra2) >> GANANCIA_CIC)
        return salida


class ModuladorSigmaDelta:
    """Modulador de 2.º orden con realimentación distribuida.

    Equivale a ``rtl/salida/sigma_delta.v``. Un paso por ciclo de 100 MHz. Los
    dos integradores se actualizan con el estado anterior, como los registros
    del RTL, y saturan a ``MOD_BITS``. La salida es el nivel del pin: 0 o 1.
    """

    def __init__(self) -> None:
        self.integra1 = 0
        self.integra2 = 0
        self.bit = 1  # tras el reset, el pin vale 1

    def paso(self, x: int) -> int:
        signo = UNO if self.bit else -UNO
        nuevo1 = self.integra1 + x - K1 * signo
        nuevo2 = self.integra2 + self.integra1 - K2 * signo
        self.integra1 = saturar(nuevo1, MOD_BITS)
        self.integra2 = saturar(nuevo2, MOD_BITS)
        self.bit = 1 if self.integra2 >= 0 else 0
        return self.bit


class Salida1Bit:
    """La cadena completa. Equivale a ``rtl/salida/salida_1bit.v``.

    Cada ``muestra`` devuelve 2 048 bits: un ciclo de reloj cada uno.
    """

    def __init__(self) -> None:
        self.interpolador = InterpoladorCIC()
        self.modulador = ModuladorSigmaDelta()

    def muestra(self, x: int) -> list[int]:
        bits = []
        for alto in self.interpolador.muestra(recortar(x)):
            # `alto` cabe en ALTO_BITS por construcción: el recorte acota la
            # entrada y el CIC no amplifica. No hace falta saturar.
            for _ in range(MANTENIMIENTO):
                bits.append(self.modulador.paso(alto))
        return bits

    def flujo(self, muestras: Iterable[int]) -> Iterator[int]:
        """Encadena los bits de varias muestras."""
        for x in muestras:
            yield from self.muestra(x)
