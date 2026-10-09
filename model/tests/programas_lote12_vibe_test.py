# SPDX-License-Identifier: MIT
"""Lote 12 del catálogo: vibe, vibe de lámpara.

Las pruebas miden lo que distingue a vibe del phaser: en modo vibrato, el tono
sube y baja a la velocidad de pot0; con pot4, el barrido sube más rápido de lo
que baja; y el footswitch acelera el barrido con una rampa. Con profundidad 0
el programa es un filtro fijo, sin modulación.
"""

from __future__ import annotations

from itertools import pairwise

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, invariante, pots, programa, rms, tono

F0 = 500.0  # tono de prueba (Hz)


def _frecuencia(
    pot: tuple[str, ...], segundos: float, desde: float, tramos_sw: tuple[tuple[int, int], ...] = ()
) -> tuple[list[float], list[float]]:
    """Instantes (s) y frecuencia instantánea (Hz) de la salida, periodo a periodo."""
    x = Senal(FS, (tono(F0, segundos, 0.3),))
    y = procesar(programa("vibe"), x, Controles(pots(*pot), tramos_sw)).canales[0]
    v = y[int(desde * FS) :]
    c = [k - 1 + v[k - 1] / (v[k - 1] - v[k]) for k in range(1, len(v)) if v[k - 1] < 0 <= v[k]]
    t = [(a + b) / 2 / FS + desde for a, b in pairwise(c)]
    return t, [FS / (b - a) for a, b in pairwise(c)]


def _ritmo(t: list[float], f: list[float]) -> float:
    """Frecuencia (Hz) de la modulación: subidas de f por su media."""
    media = sum(f) / len(f)
    subidas = [t[i] for i in range(1, len(f)) if f[i - 1] < media <= f[i]]
    return (len(subidas) - 1) / (subidas[-1] - subidas[0])


def test_vibe_vibrato_a_la_velocidad_pedida_y_quieto_sin_profundidad() -> None:
    # pot0 = 0,3: 0,3 + 7,7·0,3 = 2,61 Hz. Solo húmedo (pot2 = 1).
    t, f = _frecuencia(("0.3", "1", "1", "0", "0", "1"), 1.6, 0.3)
    assert abs(_ritmo(t, f) - 2.61) < 0.1  # medido: 2,62 Hz
    assert max(f) - min(f) > 10  # medido: de 492,4 a 507,6 Hz
    # Con profundidad 0, la respuesta no depende del instante: filtro fijo.
    c = Controles(pots("0.6", "0", "1", "0.5", "1", "0.3"))
    assert invariante("vibe", c, 3001, 3000)
    x = Senal(FS, (tono(F0, 0.2, 0.3),))
    assert procesar(programa("vibe"), x, c).canales[0] != x.canales[0]


def test_vibe_la_lampara_sube_rapido_y_baja_lento() -> None:
    """Con pot4 = 1, el tono sube (la esquina sube) en menos tiempo del que baja."""

    def fraccion_subiendo(forma: str) -> float:
        _, f = _frecuencia(("0.3", "1", "1", "0", forma, "1"), 1.2, 0.4)
        return sum(1 for v in f if v > F0) / len(f)

    assert fraccion_subiendo("1") < 0.3  # medido: 0,22 (diseño: 0,2)
    assert 0.4 < fraccion_subiendo("0") < 0.65  # medido: 0,56


def test_vibe_footswitch_acelera_con_rampa() -> None:
    # pot0 = 0,1: 1,07 Hz; pisado, ×4 = 4,3 Hz tras la rampa de 0,45 s.
    t, f = _frecuencia(("0.1", "1", "1", "0", "0", "1"), 2.4, 1.2, ((0, int(2.4 * FS)),))
    assert 3.8 < _ritmo(t, f) < 4.6  # medido: 4,24 Hz


def test_vibe_nivel() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        c = Controles(pots("0.5", "0.7", "0.3", "0.5", "0.5", "0.5"))
        nivel = rms(procesar(programa("vibe"), x, c).canales[0], 0, 1)
        assert 0.2 * plate < nivel < 2 * plate  # medido: ×0,71 y ×0,82
