# SPDX-License-Identifier: MIT
"""Medidas acústicas comunes a las pruebas de programas (no es un fichero de pruebas).

Estímulos (impulso, tono), medidas (rms, potencia en una frecuencia, máximos
locales, frecuencia por ventanas) y el ensamblado de los programas del repositorio.
"""

from __future__ import annotations

import math
from functools import cache
from pathlib import Path

from sofifi.adapters.archivos import ensamblar_archivo
from sofifi.domain.aritmetica import UNO, dato
from sofifi.domain.isa import Programa
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar

PROGRAMAS = Path(__file__).resolve().parents[2] / "programas"
FS = 48828
PROGRAMAS_TODOS = sorted(p.stem for p in PROGRAMAS.glob("*.sasm"))


@cache
def programa(nombre: str) -> Programa:
    return ensamblar_archivo(PROGRAMAS / f"{nombre}.sasm")


def impulso(segundos: float, en: int = 0) -> Senal:
    x = [0] * int(segundos * FS)
    x[en] = dato("0.5")
    return Senal(FS, (tuple(x),))


def maximos(v: tuple[int, ...], umbral: float, signo: int = 1) -> list[int]:
    """Posiciones de los máximos locales de signo·v por encima del umbral."""
    u = dato(str(umbral))
    w = [signo * s for s in v]
    return [k for k in range(1, len(w) - 1) if w[k] > u and w[k] >= w[k - 1] and w[k] >= w[k + 1]]


def rms(v: tuple[int, ...], a: float, b: float) -> float:
    seg = v[int(a * FS) : int(b * FS)]
    return math.sqrt(sum((s / UNO) ** 2 for s in seg) / len(seg))


def potencia(v: tuple[int, ...], f: float, a: float, b: float) -> float:
    seg = v[int(a * FS) : int(b * FS)]
    w = 2 * math.pi * f / FS
    re = sum(s * math.cos(w * k) for k, s in enumerate(seg))
    im = sum(s * math.sin(w * k) for k, s in enumerate(seg))
    return (re * re + im * im) / UNO**2


def pots(*valores: str) -> tuple[int, ...]:
    return tuple(dato(v) for v in valores)


def tono(f: float, segundos: float, amplitud: float = 0.9) -> tuple[int, ...]:
    w = 2 * math.pi * f / FS
    return tuple(dato(str(round(amplitud * math.sin(w * k), 6))) for k in range(int(segundos * FS)))


def frecuencias(v: tuple[int, ...], a: float, b: float, ventana: float = 0.05) -> list[float]:
    """Frecuencia (Hz) por ventanas, contando cruces por cero hacia arriba."""
    res = []
    t = a
    while t + ventana <= b:
        seg = v[int(t * FS) : int((t + ventana) * FS)]
        cruces = [k for k in range(1, len(seg)) if seg[k - 1] < 0 <= seg[k]]
        if len(cruces) > 1:
            res.append((len(cruces) - 1) * FS / (cruces[-1] - cruces[0]))
        t += ventana
    return res


def invariante(nombre: str, controles: Controles, retraso: int, largo: int) -> bool:
    """True si un impulso retrasado da la misma salida, retrasada: sin modulación."""
    y0 = procesar(programa(nombre), impulso((retraso + largo) / FS), controles).canales[0]
    y1 = procesar(programa(nombre), impulso((retraso + largo) / FS, retraso), controles).canales[0]
    return y0[:largo] == y1[retraso : retraso + largo]
