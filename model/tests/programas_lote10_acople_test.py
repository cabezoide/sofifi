# SPDX-License-Identifier: MIT
"""Lote 10 del catálogo: acople, el acople simulado de un amplificador.

Una nota sostenida hace crecer encima un armónico saturado pasado un tiempo.
Las pruebas miden la espera y el crecimiento, el apagado con un ataque nuevo,
el footswitch y el nivel de la salida.
"""

from __future__ import annotations

from functools import cache

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, potencia, pots, programa, rms, tono


def _banda(v: tuple[int, ...], f: float, a: float, b: float) -> float:
    """Energía del armónico f entre a y b segundos.

    El pitch shifter de doble tap deja el armónico un 1-3 % por debajo de f:
    en cada salto de la ventana, la fase de la voz retrocede un poco.
    """
    return sum(potencia(v, f * (1 - k / 100), a, b) for k in range(5))


def test_acople_crece_pasada_la_espera_en_el_intervalo_elegido() -> None:
    """Un tono de 196 Hz sostenido: el armónico es casi nulo al principio y luego crece."""
    x = Senal(FS, (tono(196, 1.2, 0.3),))
    # pot0 = 0 → espera de 0,3 s; pot3 = 0 → subida de unos 0,15 s.
    for intervalo, razon in (("0", 2.0), ("0.5", 1.49831), ("1", 4.0)):
        c = Controles(pots("0", intervalo, "1", "0", "0.5", "1"))
        y = procesar(programa("acople"), x, c).canales[0]
        h = 196 * razon
        antes, despues = _banda(y, h, 0.05, 0.25), _banda(y, h, 0.85, 1.2)
        assert despues > 1000 * antes  # medido: ×4e4 o más en los tres intervalos
        # El armónico elegido domina a los otros dos.
        otros = [196 * r for r in (2.0, 1.49831, 4.0) if r != razon]
        assert all(despues > 100 * _banda(y, o, 0.85, 1.2) for o in otros)  # medido: ×1 500 o más
        # Nivel acotado: CLIP y pot5 limitan el acople.
        assert rms(y, 0.85, 1.2) < 2 * rms(x.canales[0], 0.85, 1.2)  # medido: ×1,8


def test_acople_una_nota_nueva_lo_apaga_y_el_footswitch_lo_adelanta() -> None:
    """Un ataque nuevo apaga el acople y la espera empieza otra vez; sw lo hace sonar ya."""
    # La segunda nota llega tras 60 ms de silencio: el detector ve el ataque.
    x = Senal(FS, (tono(196, 1.0, 0.3) + (0,) * int(0.06 * FS) + tono(262, 1.0, 0.3),))
    y = procesar(programa("acople"), x, Controles(pots("0", "0", "1", "0", "0.5", "1"))).canales[0]
    t = 1.06  # inicio de la segunda nota
    vieja = _banda(y, 392, 0.8, 1.0)
    assert _banda(y, 392, t + 0.05, t + 0.3) < 0.002 * vieja  # medido: ×0,00005
    nueva_antes, nueva_despues = _banda(y, 524, t, t + 0.3), _banda(y, 524, t + 0.7, t + 1.0)
    assert nueva_despues > 100 * nueva_antes  # medido: ×530
    # Con la espera más larga (4 s), el footswitch pisado desde 0,5 s hace sonar la octava.
    x = Senal(FS, (tono(196, 1.1, 0.3),))
    c = Controles(pots("1", "0", "1", "1", "0.5", "1"), tramos_sw=((int(0.5 * FS), int(1.1 * FS)),))
    y = procesar(programa("acople"), x, c).canales[0]
    assert _banda(y, 392, 0.8, 1.1) > 1000 * _banda(y, 392, 0.2, 0.5)  # medido: ×8e4


@cache
def _plate(amplitud: float) -> float:
    x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
    return rms(procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1)


def test_acople_nivel_razonable_frente_al_plate() -> None:
    """Con el footswitch pisado, el acople suena entero desde el principio."""
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        c = Controles(pots("0", "0", "1", "0", "0.5", "1"), tramos_sw=((0, FS),))
        nivel = rms(procesar(programa("acople"), x, c).canales[0], 0, 1)
        assert 0.2 * _plate(amplitud) < nivel < 2 * _plate(amplitud)  # medido: ×1,32 y ×1,33
