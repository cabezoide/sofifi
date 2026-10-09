# SPDX-License-Identifier: MIT
"""Lote 13 del catálogo: frenada, eco de cinta con freno completo (tape stop).

Las pruebas miden lo que distingue a frenada de cinta y de lata: con sw pisado,
el tono del eco baja hasta parar y el nivel cae al silencio; al soltar, el eco
vuelve a su tono. Sin pisar, es un eco normal en el tiempo de pot0.
"""

from __future__ import annotations

from itertools import pairwise

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, frecuencias, impulso, maximos, pots, programa, rms, tono


def test_frenada_el_freno_baja_el_tono_hasta_parar_y_vuelve() -> None:
    """Tono de 440 Hz; sw pisado de 0,5 s a 1,0 s; frenada en 0,18 s (pot3 = 0,3)."""
    x = Senal(FS, (tono(440, 1.4, 0.3),))
    pisado = ((int(0.5 * FS), int(1.0 * FS)),)
    c = Controles(pots("0.3", "0", "1", "0.3", "0", "0"), tramos_sw=pisado)
    y = procesar(programa("frenada"), x, c).canales[0]
    antes = rms(y, 0.3, 0.5)
    # La frecuencia baja de forma monótona mientras la cinta frena.
    caida = frecuencias(y, 0.5, 0.68, 0.03)
    assert len(caida) >= 4
    assert all(b < a for a, b in pairwise(caida))
    assert caida[0] > 380 and caida[-1] < 150  # medido: 408, 337, 265, 190, 123 Hz
    # El nivel cae con la velocidad.
    assert rms(y, 0.6, 0.65) < 0.6 * antes  # medido: ×0,32
    # Parada: solo queda el seco a −60 dB de la mezcla.
    assert rms(y, 0.75, 0.95) < 0.01 * antes  # medido: 0,0002 frente a 0,208
    # Al soltar, la cinta arranca en 0,05 s (pot4 = 0) y vuelve a su tono y nivel.
    despues = frecuencias(y, 1.1, 1.4, 0.05)
    assert all(abs(q - 440) < 2 for q in despues)  # medido: 439,9 a 440,1 Hz
    assert abs(rms(y, 1.1, 1.4) / antes - 1) < 0.02  # medido: 1,000


def test_frenada_sin_pisar_es_un_eco_en_el_tiempo_de_pot0() -> None:
    c = Controles(pots("0.5", "0.3", "1", "0.5"))
    y = procesar(programa("frenada"), impulso(0.4), c).canales[0]
    ecos = maximos(y, 0.05)
    assert len(ecos) == 1 and abs(ecos[0] / FS - 0.33) < 0.002  # medido: 0,3299 s


def test_frenada_nivel() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        c = Controles(pots("0.5", "0.3", "0.5", "0.5", "0", "0"))
        y = procesar(programa("frenada"), x, c).canales[0]
        assert 0.2 * plate < rms(y, 0, 1) < 2 * plate  # medido: ×0,56 y ×0,65
