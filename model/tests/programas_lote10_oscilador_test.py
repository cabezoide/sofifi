# SPDX-License-Identifier: MIT
"""Lote 10 del catálogo: oscilador, un eco que autooscila con un techo de nivel.

Las pruebas miden lo que lo distingue de delay.sasm: con la realimentación por
encima de 1, el lazo se sostiene en el techo, sin crecer ni morir; el tiempo
afina el tono y lo desliza, y el footswitch dispara la oscilación.
"""

from __future__ import annotations

from itertools import pairwise

from sofifi.domain.aritmetica import UNO
from sofifi.domain.nucleo import Nucleo
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, frecuencias, impulso, pots, programa, rms, tono


def test_oscilador_se_sostiene_en_el_techo_y_decae_por_debajo_de_1() -> None:
    x = impulso(1.4)

    def salida(realimentacion: str, nivel: str = "0.5", sw: bool = False) -> tuple[int, ...]:
        tramos = ((0, int(0.7 * FS)),) if sw else ()
        c = Controles(pots("0.1", realimentacion, "1", "0", "0.3", nivel), tramos_sw=tramos)
        return procesar(programa("oscilador"), x, c).canales[0]

    oscila = salida("1")
    a, b = rms(oscila, 0.7, 1.0), rms(oscila, 1.1, 1.4)
    assert 0.95 < b / a < 1.05  # medido: 1,00; ni crece ni muere
    pico = max(abs(s) for s in oscila[int(1.1 * FS) : int(1.4 * FS)]) / UNO
    assert 0.3 < pico < 0.42  # medido: 0,37; el techo con pot5 = 0,5 es 0,35
    techo_alto, techo_bajo = rms(salida("1", "1"), 1.1, 1.4), rms(salida("1", "0"), 1.1, 1.4)
    assert techo_alto > 3 * techo_bajo  # medido: ×4,9
    assert rms(salida("0.7"), 0.7, 1.0) < 0.01 * a  # medido: 0; por debajo de 1 decae
    # El footswitch dispara el lazo con pot1 = 0; al soltarlo, la oscilación muere.
    disparo = salida("0", sw=True)
    assert rms(disparo, 0.5, 0.7) > 0.8 * a  # medido: 0,26, como sin pisar
    assert rms(disparo, 1.0, 1.4) < 0.01 * a  # medido: 0


def test_oscilador_el_tiempo_afina_y_desliza_el_tono() -> None:
    """Se mueve pot0 a los 0,65 s: el tono cambia; con suavizado, se desliza."""
    x = tono(330, 0.05, 0.5) + (0,) * int(1.6 * FS)

    def salida(suavizado: str) -> tuple[int, ...]:
        n = Nucleo(programa("oscilador"))
        antes = pots("0.06", "1", "1", suavizado, "0.3", "0.5")
        despues = pots("0.09", "1", "1", suavizado, "0.3", "0.5")
        cambio = int(0.65 * FS)
        return tuple(n.procesar(s, s, antes if k < cambio else despues)[0] for k, s in enumerate(x))

    rapido = salida("0")
    f_antes = frecuencias(rapido, 0.3, 0.6)
    f_despues = frecuencias(rapido, 1.3, 1.6)
    assert max(f_antes) - min(f_antes) < 2 and max(f_despues) - min(f_despues) < 2
    assert abs(f_antes[0] - f_despues[0]) > 15  # medido: 529 Hz → 500 Hz
    # Con suavizado 1, el tono baja poco a poco, como una cinta que frena.
    lento = frecuencias(salida("1"), 0.7, 1.15)
    assert all(b < a for a, b in pairwise(lento))
    assert lento[0] - lento[-1] > 60  # medido: 519 Hz → 405 Hz


def test_oscilador_nivel_comparable_al_plate() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        c = Controles(pots("0.1", "1", "1", "0"))
        y = rms(procesar(programa("oscilador"), x, c).canales[0], 0, 1)
        assert 0.2 * plate < y < 2 * plate  # medido: 1,51× (0,1) y 0,49× (0,5)
