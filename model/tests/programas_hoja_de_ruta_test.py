# SPDX-License-Identifier: MIT
"""Ampliaciones de la hoja de ruta de la Fase 03: plate vivo, shimmer energético y freeze de Givens.

Cada una se compara con el programa del que sale: debe hacer lo mismo cuando
su mando está a 0, y añadir solo lo que promete cuando no.
"""

from __future__ import annotations

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, impulso, potencia, pots, programa, rms, tono


def test_plate_vivo_es_el_plate_con_vida_cero_y_cambia_con_vida() -> None:
    plate = procesar(programa("plate"), impulso(0.5), Controles(pots("0.5", "0.3", "0.5", "0")))
    quieto = procesar(
        programa("plate_vivo"), impulso(0.5), Controles(pots("0.5", "0.3", "0.5", "0"))
    )
    vivo = procesar(programa("plate_vivo"), impulso(0.5), Controles(pots("0.5", "0.3", "0.5", "1")))
    assert quieto.canales == plate.canales  # bit a bit
    assert vivo.canales != plate.canales


def test_shimmer_energia_frena_la_octava_en_notas_largas() -> None:
    f = 330.0

    def octavas(nombre: str, x: Senal, c: Controles, a: float, b: float) -> float:
        y = procesar(programa(nombre), x, c).canales[0]
        return sum(potencia(y, f * m, a, b) for m in (2, 4))

    larga = Senal(FS, (tono(f, 2.0, 0.3) + (0,) * FS,))
    c_larga = Controles(pots("0.8", "0.2", "1", "1"))
    assert octavas("shimmer_energia", larga, c_larga, 2.1, 2.9) < 0.4 * octavas(
        "shimmer", larga, c_larga, 2.1, 2.9
    )  # medido: 0,24 frente a 0,97
    corta = Senal(FS, (tono(f, 0.25, 0.3) + (0,) * int(0.9 * FS),))
    c_corta = Controles(pots("0.6", "0.3", "1", "0.8"))
    assert octavas("shimmer_energia", corta, c_corta, 0.45, 1.1) > 0.4 * octavas(
        "shimmer", corta, c_corta, 0.45, 1.1
    )  # medido: 0,033 frente a 0,054


def test_freeze_givens_gira_sin_perder_energia() -> None:
    """La rotación cuantizada a 24 bit conserva la energía y mueve el espectro."""

    def congelado(nombre: str, giro: str) -> tuple[int, ...]:
        c = Controles(pots("0.5", "0.3", "0.5", giro), tramos_sw=((int(0.05 * FS), 10 * FS),))
        return procesar(programa(nombre), impulso(4.5), c).canales[0]

    def cambio(y: tuple[int, ...]) -> float:
        fr = (300, 700, 1100, 1500, 1900)
        a = [potencia(y, f, 1.0, 1.5) for f in fr]
        b = [potencia(y, f, 4.0, 4.5) for f in fr]
        return sum(abs(p - q) for p, q in zip(a, b, strict=True)) / sum(a)

    girando, freeze = congelado("freeze_givens", "1"), congelado("freeze", "0")
    assert abs(rms(girando, 4.0, 4.5) / rms(girando, 0.5, 1.0) - 1) < 0.05
    assert cambio(girando) > 1.5 * cambio(freeze)  # medido: 1,44 frente a 0,67
