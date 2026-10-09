# SPDX-License-Identifier: MIT
"""Lote 14 del catálogo: espiral, una reverb cuya cola sube o baja de tono en cada vuelta.

Las pruebas miden lo que distingue a espiral de shimmer, escalera y arcoiris:
cada lado tiene su propio bucle y su propio intervalo, el pedal sostiene la
cola con el CLIP como techo y el nivel queda cerca del plate.
"""

from __future__ import annotations

from sofifi.domain.aritmetica import UNO
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, potencia, pots, programa, rms, tono


def test_espiral_cada_lado_sube_o_baja_con_su_intervalo() -> None:
    """Con +12 a la izquierda y −12 a la derecha, las colas se separan en octavas."""
    f = 330.0
    x = Senal(FS, (tono(f, 0.3, 0.3) + (0,) * int(0.9 * FS),))
    c = Controles(pots("1", "0", "1", "0.3", "0.7", "0"))
    izq, der = procesar(programa("espiral"), x, c).canales

    def octavas(v: tuple[int, ...], factores: tuple[float, ...]) -> float:
        return sum(potencia(v, f * k, 0.4, 1.2) for k in factores)

    arriba, abajo = (2.0, 4.0), (0.5, 0.25)
    # medido: izquierda 3 025 frente a 1,5; derecha 33 745 frente a 1,0
    assert octavas(izq, arriba) > 100 * octavas(izq, abajo)
    assert octavas(der, abajo) > 100 * octavas(der, arriba)
    # cada vuelta vuelve a subir: 4f pesa más que 2f (medido: ×2,1)
    assert potencia(izq, 4 * f, 0.4, 1.2) > 1.5 * potencia(izq, 2 * f, 0.4, 1.2)


def test_espiral_el_pedal_sostiene_la_cola_acotada() -> None:
    """Con el pedal pisado, el bucle autooscila hasta el techo del CLIP; al soltarlo, se apaga."""
    x = Senal(FS, (tono(196, 0.3, 0.3) + (0,) * int(2.7 * FS),))
    c = Controles(pots("0.75", "0.4", "1", "0.5", "0", "0"), tramos_sw=((0, 2 * FS),))
    izq, der = procesar(programa("espiral"), x, c).canales
    sostenida = rms(izq, 1.5, 2.0) + rms(der, 1.5, 2.0)
    apagada = rms(izq, 2.6, 3.0) + rms(der, 2.6, 3.0)
    assert 0.2 < sostenida < 1.2  # medido: 0,41
    assert apagada < 0.05 * sostenida  # medido: 0,0006
    assert max(abs(s) for s in izq + der) < 0.98 * UNO  # medido: 0,91


def test_espiral_nivel_cerca_del_plate() -> None:
    """Con un tono de 196 Hz a 0,1 y a 0,5, la salida no pasa de 2× el plate ni baja de 0,2×."""
    for amplitud, cola in ((0.1, 0.4), (0.5, 0.6)):
        x = Senal(FS, (tono(196, 0.3, amplitud) + (0,) * int(cola * FS),))
        b = 0.3 + cola
        y = procesar(
            programa("espiral"), x, Controles(pots("0.75", "0.4", "1", "0.5", "0.5", "0.5"))
        )
        p = procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1")))
        nivel = rms(y.canales[0], 0, b) + rms(y.canales[1], 0, b)
        ref = rms(p.canales[0], 0, b) + rms(p.canales[1], 0, b)
        assert 0.2 * ref < nivel < 2 * ref  # medido: 0,51× y 0,52×
