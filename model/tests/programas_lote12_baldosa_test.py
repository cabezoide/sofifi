# SPDX-License-Identifier: MIT
"""Lote 12 del catálogo: baldosa, reverb sucia de dos ecos cruzados.

Las pruebas miden lo que distingue a baldosa del plate: la cola sigue a pot1
porque la realimentación cruzada es el único bucle, la retención de muestras
(pot5) añade aliasing y la salida es estéreo porque cada lado lee su línea.
"""

from __future__ import annotations

import math

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, pots, programa, rms, tono


def _agudos(v: tuple[int, ...], a: float, b: float) -> float:
    """Segunda diferencia entre señal (RMS): crece con lo que suena por encima de la nota."""
    s = v[int(a * FS) : int(b * FS)]
    d = [s[k] - 2 * s[k - 1] + s[k - 2] for k in range(2, len(s))]
    return math.sqrt(sum(x * x for x in d) / sum(x * x for x in s))


def test_baldosa_la_cola_sigue_al_decay() -> None:
    x = Senal(FS, (tono(196, 0.2, 0.3) + (0,) * int(1.1 * FS),))

    def caida(decay: str) -> float:
        c = Controles(pots("0.5", decay, "1", "0.5", "0.5", "0"))
        y = procesar(programa("baldosa"), x, c).canales[0]
        return rms(y, 1.0, 1.3) / rms(y, 0.3, 0.4)

    corta, larga = caida("0.3"), caida("1")
    assert larga > 0.25  # medido: 0,39 (−8 dB en 0,8 s)
    assert corta < 0.01  # medido: 0 (la cuantización a 12 bit corta la cola)


def test_baldosa_el_muestreo_anade_aliasing() -> None:
    """Con pot5 = 1, la retención a 4,9 kHz saca energía muy por encima de la nota."""
    x = Senal(FS, (tono(196, 0.5, 0.3),))

    def agudos(muestreo: str) -> float:
        c = Controles(pots("0.5", "0.5", "1", "0.5", "0.5", muestreo))
        return _agudos(procesar(programa("baldosa"), x, c).canales[0], 0.25, 0.5)

    limpio, sucio = agudos("0"), agudos("1")
    assert sucio > 20 * limpio  # medido: 0,113 y 0,0010 (×115)


def test_baldosa_nivel_y_estereo() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        c = Controles(pots("0.5", "0.5", "0.5", "0.5", "0.5", "0.5"))
        izq, der = procesar(programa("baldosa"), x, c).canales
        assert 0.2 * plate < rms(izq, 0, 1) < 2 * plate  # medido: ×0,43 y ×0,48
        # Cada lado lee su línea: las colas casi no se parecen.
        ti, td = izq[int(0.45 * FS) :], der[int(0.45 * FS) :]
        cor = sum(a * b for a, b in zip(ti, td, strict=True)) / math.sqrt(
            sum(a * a for a in ti) * sum(b * b for b in td)
        )
        assert abs(cor) < 0.4  # medido: 0,12 y 0,11
