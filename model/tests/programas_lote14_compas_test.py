# SPDX-License-Identifier: MIT
"""Lote 14 del catálogo: compas, eco con tap tempo y subdivisiones.

Las pruebas miden lo que distingue al programa de delay y pingpong: sin tap,
el eco cae en la negra de pot0 por la figura de pot3. Dos pisadas separadas
T cambian la negra a T, y la toma de la derecha cae en el puntillo. El nivel
queda acotado.
"""

from __future__ import annotations

from sofifi.domain.aritmetica import UNO
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, impulso, pots, programa, rms, tono


def _eco(c: tuple[int, ...], desde: int) -> int:
    """Muestras desde `desde` hasta el pico más alto que llega después."""
    k = max(range(desde + 20, len(c)), key=lambda k: abs(c[k]))
    return k - desde


def test_compas_sin_tap_el_eco_cae_en_la_figura_de_pot0() -> None:
    """pot0 = 0,5 da una negra de 0,4 · 65 536 muestras; pot3 elige negra o corchea con puntillo."""
    negra = 0.4 * 65536
    en = int(0.05 * FS)
    for figura, sub in (("0.1", 1.0), ("0.3", 0.75)):
        x = impulso(0.65, en)
        c = Controles(pots("0.5", "0", "1", figura, "0", "1"))
        y = procesar(programa("compas"), x, c).canales[0]
        assert abs(_eco(y, en) - negra * sub) < 3  # medido: 26 213 y 19 660 muestras


def test_compas_dos_pisadas_marcan_la_negra() -> None:
    """Con pisadas separadas T = 0,3 s: izquierda en T·sub, derecha en ¾ de la toma 1."""
    t = int(0.3 * FS)
    p1 = int(0.05 * FS)
    tramos = ((p1, p1 + 2000), (p1 + t, p1 + t + 2000))
    en = p1 + t + int(0.4 * FS)  # el retardo se desliza ~0,35 s hasta la negra nueva
    x = impulso((en + t) / FS + 0.05, en)

    def ecos(figura: str) -> tuple[int, int]:
        c = Controles(pots("0.5", "0", "1", figura, "1", "1"), tramos_sw=tramos)
        izq, der = procesar(programa("compas"), x, c).canales
        return _eco(izq, en), _eco(der, en)

    negra_izq, puntillo_der = ecos("0.1")
    assert abs(negra_izq - t) < 8  # medido: T + 4 (el deslizamiento se para a ~4 muestras)
    assert abs(puntillo_der - 0.75 * t) < 8  # medido: ¾·T + 3
    puntillo_izq, _ = ecos("0.3")
    assert abs(puntillo_izq - 0.75 * t) < 8  # medido: ¾·T + 4


def test_compas_nivel_comparable_al_plate() -> None:
    """Con realimentación casi al máximo y las dos tomas, el nivel queda cerca del plate."""
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        c = Controles(pots("0.4", "0.95", "1", "0.3", "1", "1"))
        for canal in procesar(programa("compas"), x, c).canales:
            assert 0.2 * plate < rms(canal, 0, 1) < 2 * plate  # medido: ×1,18-1,54
            assert max(abs(v) for v in canal) < 0.98 * UNO  # medido: 0,90
