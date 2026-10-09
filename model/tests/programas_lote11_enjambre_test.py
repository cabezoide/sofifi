# SPDX-License-Identifier: MIT
"""Lote 11 del catálogo: enjambre, una nube de ocho ecos con dispersión variable.

Las pruebas miden lo que distingue al programa: la dispersión junta los ocho
ecos en una cola continua o los separa en ecos sueltos, y el footswitch los
pone en corcheas de la dispersión.
"""

from __future__ import annotations

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, impulso, maximos, pots, programa, rms, tono

PROPORCIONES = (0.13, 0.181, 0.237, 0.322, 0.413, 0.561, 0.739, 1.0)
D_MAX = 29297  # muestras de dispersión con pot0 = 1 (600 ms)


def _picos(nombre: str, mandos: tuple[str, ...], segundos: float, sw: bool = False) -> list[int]:
    """Posiciones de los ecos de un impulso en los dos canales, de menor a mayor."""
    tramos = ((0, int(segundos * FS)),) if sw else ()
    izq, der = procesar(
        programa(nombre), impulso(segundos), Controles(pots(*mandos), tramos_sw=tramos)
    ).canales
    picos = set()
    for canal in (izq, der):
        picos |= set(maximos(canal, 0.02)) | set(maximos(canal, 0.02, -1))
    return sorted(picos)


def _cerca(medidos: list[int], esperados: list[float]) -> bool:
    return len(medidos) == len(esperados) and all(
        abs(m - e) <= 2 for m, e in zip(medidos, esperados, strict=True)
    )


def test_enjambre_la_dispersion_junta_o_separa_los_ecos() -> None:
    """Abajo: ocho ecos en 10 ms y una cola continua. Arriba: ocho ecos sueltos."""
    nitido = ("0", "0", "1", "0", "1", "0")
    juntos = _picos("enjambre", nitido, 0.05)
    assert len(juntos) == 8 and juntos[-1] < 0.011 * FS  # medido: de 63 a 488 muestras
    sueltos = _picos("enjambre", ("1", *nitido[1:]), 0.62)
    assert _cerca(sueltos, [r * D_MAX for r in PROPORCIONES])  # medido: error ≤ 1 muestra

    def ocupacion(dispersion: str) -> float:
        """Fracción de ventanas de 5 ms con energía, de 50 a 650 ms."""
        mandos = pots(dispersion, "0.9", "1", "0", "1", "0")
        y = procesar(programa("enjambre"), impulso(0.65), Controles(mandos)).canales[0]
        v = [rms(y, 0.05 + k * 0.005, 0.055 + k * 0.005) for k in range(120)]
        media = sum(v) / len(v)
        return sum(x > 0.1 * media for x in v) / len(v)

    assert ocupacion("0") > 0.95  # medido: 1,0, una reverb
    assert ocupacion("1") < 0.2  # medido: 0,03, ecos sueltos


def test_enjambre_con_footswitch_los_ecos_caen_en_corcheas() -> None:
    picos = _picos("enjambre", ("1", "0", "1", "0", "1", "0"), 0.62, sw=True)
    assert _cerca(picos, [k * D_MAX / 8 for k in range(1, 9)])  # medido: error ≤ 1 muestra


def test_enjambre_nivel_comparable_al_plate() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1")))
        mandos = pots("0.5", "0.3", "1", "0.5", "0.5", "0")
        y = procesar(programa("enjambre"), x, Controles(mandos))
        for canal in (0, 1):
            r = rms(y.canales[canal], 0, 1.0) / rms(plate.canales[canal], 0, 1.0)
            assert 0.2 < r < 2.0  # medido: 1,02 con 0,1 y 1,18-1,26 con 0,5
