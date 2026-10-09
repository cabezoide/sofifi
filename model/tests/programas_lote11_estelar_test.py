# SPDX-License-Identifier: MIT
"""Lote 11 del catálogo: estelar, un eco con un phaser dentro de la realimentación.

Las pruebas miden lo que lo distingue de un eco limpio: cada repetición pasa por
el phaser en otro punto del barrido, y el color de los ecos cambia vuelta a
vuelta. Con profundidad 0, es el eco limpio de `delay`.
"""

from __future__ import annotations

import math

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, potencia, pots, programa, rms, tono

T_ECO = 0.18926  # pot0 = 0,25: tiempo del eco medido, en segundos


def test_estelar_el_color_cambia_de_un_eco_al_siguiente() -> None:
    """Dos tonos, 700 Hz y 1,5 kHz: su diferencia en dB salta de un eco a otro."""
    dos_tonos = tuple(
        p + q for p, q in zip(tono(700, 0.05, 0.2), tono(1500, 0.05, 0.2), strict=True)
    )
    x = Senal(FS, (dos_tonos + (0,) * int(1.5 * FS),))

    def dispersion(profundidad: str) -> float:
        c = Controles(pots("0.25", "0.85", "1", profundidad, "0.5", "0"))
        y = procesar(programa("estelar"), x, c).canales[0]
        d = []
        for n in range(1, 8):
            a, b = n * T_ECO + 0.005, n * T_ECO + 0.045
            d.append(10 * math.log10(potencia(y, 700, a, b) / potencia(y, 1500, a, b)))
        pasos = [d[k + 1] - d[k] for k in range(len(d) - 1)]
        m = sum(pasos) / len(pasos)
        return math.sqrt(sum((p - m) ** 2 for p in pasos) / len(pasos))

    limpio, remolino = dispersion("0"), dispersion("1")
    assert limpio < 2  # medido: 0,78 dB (solo el paso bajo del lazo)
    assert remolino > 8 and remolino > 5 * limpio  # medido: 16,3 dB


def test_estelar_sin_profundidad_es_el_eco_limpio() -> None:
    """Con pot3 = 0, la salida es la de `delay` con el mismo tono (pot3 = 0,25)."""
    x = Senal(FS, (tono(330, 0.2, 0.3) + (0,) * int(0.8 * FS),))
    e = procesar(programa("estelar"), x, Controles(pots("0.25", "0.6", "0.5", "0", "0.5", "0")))
    d = procesar(programa("delay"), x, Controles(pots("0.25", "0.6", "0.5", "0.25")))
    resta = tuple(p - q for p, q in zip(e.canales[0], d.canales[0], strict=True))
    assert rms(resta, 0, 1.0) < 1e-3 * rms(d.canales[0], 0, 1.0)  # medido: 6·10⁻⁶


def test_estelar_nivel_acotado() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1.0
        )
        c = Controles(pots("0.25", "0.85", "1", "1", "0.5", "1"))
        estelar = rms(procesar(programa("estelar"), x, c).canales[0], 0, 1.0)
        assert 0.2 * plate < estelar < 2 * plate  # medido: 0,47 y 0,55
