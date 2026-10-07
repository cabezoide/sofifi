# SPDX-License-Identifier: MIT
"""LFSR y osciladores de baja frecuencia del núcleo (ADR 0008).

Todo es entero y determinista: el ruido sale de un LFSR con semilla fija,
nunca de ``random``. Cada muestra, *antes* de ejecutar el programa, cada LFO
avanza con los registros ``lfoN_rate`` y ``lfoN_depth`` de la muestra anterior.

- **Fase:** 24 bit sin signo; ``rate`` (dato S.23 leído como entero) es el
  incremento por muestra, así que ``f = rate · fs / 2²⁴`` (≈ 0,0029 Hz por LSB).
- **SIN:** triángulo suavizado con ``curva_suave``. Bipolar, escalado por
  ``depth`` y por la excursión declarada ``E`` (muestras).
- **RND:** cada vuelta de fase, el LFSR fija un objetivo nuevo; la salida lo
  persigue con un filtro de un polo (``>> 6``). Bipolar, como SIN.
- **RAMP:** diente de sierra para el pitch shifter. El desplazamiento va de 0
  a la ventana ``W``; ``rate`` negativo sube el tono y positivo lo baja.
  Desde la muestra ``fase`` se calcula también la ventana triangular de fundido.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from sofifi.domain.aritmetica import DATO_FRAC, DATO_MAX, curva_suave, saturar

FASE_BITS = 24
FASE_MOD = 1 << FASE_BITS
MEDIA_FASE = FASE_MOD >> 1
LFSR_MASCARA = 0xD0000001  # Galois, 32 bit, longitud máxima
LFSR_SEMILLA = 0xACE1ACE1
SUAVIZADO_RND = 6
NUM_LFOS = 4


def lfsr_paso(estado: int) -> int:
    lsb = estado & 1
    estado >>= 1
    if lsb:
        estado ^= LFSR_MASCARA
    return estado


class TipoLfo(Enum):
    SIN = "sin"
    RND = "rnd"
    RAMP = "ramp"


@dataclass(frozen=True)
class ConfigLfo:
    tipo: TipoLfo
    excursion: int  # E (SIN, RND) o ventana W (RAMP), en muestras

    def __post_init__(self) -> None:
        if not 1 <= self.excursion <= 16384:
            raise ValueError(f"excursión de LFO {self.excursion} fuera de [1, 16384]")


def triangulo(fase: int) -> int:
    """Fase de 24 bit → triángulo S.23 en [-1, 1], 0 en fase 0, +1 en un cuarto."""
    cuarto = FASE_MOD >> 2
    if fase < cuarto:
        t = fase << 1
    elif fase < 3 * cuarto:
        t = (MEDIA_FASE - fase) << 1
    else:
        t = (fase - FASE_MOD) << 1
    return saturar(t, DATO_FRAC + 1)


def ventana(fase: int) -> int:
    """Ventana triangular S.23: 0 en fase 0 (salto del puntero), 1 a media fase."""
    distancia = abs(2 * fase - FASE_MOD)  # en [0, 2^24]
    return min(DATO_MAX, (1 << DATO_FRAC) - (distancia >> 1))


class Lfo:
    def __init__(self, config: ConfigLfo) -> None:
        self.config = config
        self.fase = 0
        self._lfsr = LFSR_SEMILLA
        self._objetivo = 0
        self._actual = 0

    def avanzar(self, rate: int) -> None:
        nueva = self.fase + rate
        vuelta = nueva >= FASE_MOD or nueva < 0
        self.fase = nueva % FASE_MOD
        if self.config.tipo is TipoLfo.RND:
            if vuelta:
                for _ in range(DATO_FRAC + 1):
                    self._lfsr = lfsr_paso(self._lfsr)
                self._objetivo = (self._lfsr & 0xFFFFFF) - (1 << DATO_FRAC)
            self._actual += (self._objetivo - self._actual) >> SUAVIZADO_RND

    def forma(self) -> int:
        """Valor bipolar S.23 (SIN, RND)."""
        if self.config.tipo is TipoLfo.SIN:
            return curva_suave(triangulo(self.fase))
        return self._actual

    def desplazamiento_q8(self, depth: int, media: bool = False) -> int:
        """Desplazamiento de lectura en muestras con 8 bits de fracción (≥ 0)."""
        e = self.config.excursion
        if self.config.tipo is TipoLfo.RAMP:
            fase = (self.fase + MEDIA_FASE) % FASE_MOD if media else self.fase
            return (fase * e) >> (FASE_BITS - 8)
        amplitud = (self.forma() * depth) >> DATO_FRAC
        return (e << 8) + ((amplitud * e) >> (DATO_FRAC - 8))

    def ventana(self, media: bool = False) -> int:
        fase = (self.fase + MEDIA_FASE) % FASE_MOD if media else self.fase
        return ventana(fase)
