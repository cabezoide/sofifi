# SPDX-License-Identifier: MIT
"""Adaptadores WAV (PCM entero) para los puertos de audio.

El remuestreo lineal de la entrada, si su frecuencia no es ``FS_WAV``, ocurre
**fuera** del oráculo: es comodidad para escuchar, no parte del contrato bit-exact.
"""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from sofifi.domain.aritmetica import DATO_FRAC, DATO_MAX, DATO_MIN, FS_WAV
from sofifi.domain.senal import Senal


class FuenteWav:
    def __init__(self, ruta: Path, fs_objetivo: int = FS_WAV) -> None:
        self.ruta = ruta
        self.fs_objetivo = fs_objetivo

    def leer(self) -> Senal:
        with wave.open(str(self.ruta), "rb") as w:
            ancho, canales, fs = w.getsampwidth(), w.getnchannels(), w.getframerate()
            crudo = w.readframes(w.getnframes())
        if ancho not in (2, 3, 4):
            raise ValueError(f"{self.ruta}: solo PCM de 16, 24 o 32 bit (tiene {8 * ancho})")
        bytes_ = np.frombuffer(crudo, dtype=np.uint8).reshape(-1, ancho)
        relleno = np.zeros((bytes_.shape[0], 4 - ancho), dtype=np.uint8)
        enteros = np.hstack([relleno, bytes_]).view("<i4").ravel() >> (32 - 8 * ancho)
        muestras = enteros.astype(np.int64).reshape(-1, canales)[:, :2]
        a_s23 = DATO_FRAC + 1 - 8 * ancho
        muestras = muestras << a_s23 if a_s23 >= 0 else muestras >> -a_s23
        if fs != self.fs_objetivo and len(muestras) > 1:
            t_nuevo = np.arange(int(len(muestras) * self.fs_objetivo / fs)) * fs / self.fs_objetivo
            muestras = (
                np.stack(
                    [
                        np.interp(t_nuevo, np.arange(len(muestras)), muestras[:, c])
                        for c in range(muestras.shape[1])
                    ],
                    axis=1,
                )
                .round()
                .astype(np.int64)
            )
        muestras = np.clip(muestras, DATO_MIN, DATO_MAX)
        return Senal(
            self.fs_objetivo,
            tuple(tuple(int(v) for v in muestras[:, c]) for c in range(muestras.shape[1])),
        )


def a_pcm16(senal: Senal) -> NDArray[np.int16]:
    """S.23 → PCM de 16 bit redondeado, una columna por canal."""
    datos = np.array(senal.canales, dtype=np.int64).T
    pcm: NDArray[np.int16] = np.clip((datos + 128) >> 8, -(1 << 15), (1 << 15) - 1).astype(np.int16)
    return pcm


class SumideroWav:
    """Escribe PCM de 24 bit (exacto) o de 16 bit (redondeado), con los canales de la señal."""

    def __init__(self, ruta: Path, bits: int = 24) -> None:
        if bits not in (16, 24):
            raise ValueError(f"{ruta}: solo PCM de 16 o 24 bit (pide {bits})")
        self.ruta = ruta
        self.bits = bits

    def escribir(self, senal: Senal) -> None:
        datos = a_pcm16(senal) if self.bits == 16 else np.array(senal.canales, dtype=np.int64).T
        ancho = self.bits // 8
        crudo = datos.astype("<i4").reshape(-1, 1).view(np.uint8).reshape(-1, 4)[:, :ancho]
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(self.ruta), "wb") as w:
            w.setnchannels(len(senal.canales))
            w.setsampwidth(ancho)
            w.setframerate(senal.fs_hz)
            w.writeframes(crudo.tobytes())
