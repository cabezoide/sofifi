# SPDX-License-Identifier: MIT
"""Lote 14 del catálogo: swell_ritmico, swell con forma elegible y tap tempo.

Las pruebas miden lo que lo distingue de swell y violin: la curva de la
subida cambia con pot1, y dos pisadas del pedal fijan la duración de la
subida. El nivel queda acotado frente al plate.
"""

from __future__ import annotations

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, pots, programa, rms, tono

ANTES = 0.05  # silencio antes de la nota (s)


def _nota(antes: float, segundos: float) -> Senal:
    return Senal(FS, ((0,) * int(antes * FS) + tono(196, segundos, 0.3),))


def _envolvente(y: tuple[int, ...], inicio: float, fin: float, tiempos: list[float]) -> list[float]:
    """Nivel en ventanas de 20 ms, relativo al nivel final de la nota."""
    final = rms(y, inicio + fin - 0.15, inicio + fin)
    return [rms(y, inicio + t - 0.01, inicio + t + 0.01) / final for t in tiempos]


def test_swell_ritmico_la_forma_cambia_la_curva() -> None:
    """Con pot0 = 0,3 la subida dura T = 0,26 s. Se mide el seco a T/4 y a 3T/4."""
    x = _nota(ANTES, 0.45)

    def niveles(forma: str) -> tuple[float, float]:
        c = Controles(pots("0.3", forma, "0", "0.5", "0", "0"))
        y = procesar(programa("swell_ritmico"), x, c).canales[0]
        a, b = _envolvente(y, ANTES, 0.45, [0.065, 0.195])
        return a, b

    exp_a, exp_b = niveles("0")
    lin_a, lin_b = niveles("0.5")
    log_a, log_b = niveles("1")
    # Exponencial: el primer cuarto apenas sube. Logarítmica: al revés.
    # Ideal: x² = 0,06 y 0,56; x = 0,25 y 0,75; 1 − (1 − x)² = 0,44 y 0,94.
    assert exp_a < 0.1 and exp_b > 5 * exp_a  # medido: 0,062 y 0,555
    assert log_a > 0.35 and log_b > 0.9  # medido: 0,429 y 0,928
    assert exp_a < lin_a < log_a  # medido: 0,062 · 0,245 · 0,429
    assert exp_b < lin_b < log_b  # medido: 0,555 · 0,741 · 0,928


def test_swell_ritmico_dos_pisadas_fijan_la_subida() -> None:
    """Dos pisadas separadas T fijan la subida, aunque pot0 pida 2,7 s."""
    nota = 0.5
    x = _nota(nota, 0.55)
    sin_tap = procesar(
        programa("swell_ritmico"), x, Controles(pots("1", "0.5", "0", "0.5", "0", "0"))
    ).canales[0]
    for t in (0.2, 0.4):
        a, b = int(0.02 * FS), int((0.02 + t) * FS)
        c = Controles(pots("1", "0.5", "0", "0.5", "0", "0"), ((a, a + 2000), (b, b + 2000)))
        y = procesar(programa("swell_ritmico"), x, c).canales[0]
        mitad, entero = _envolvente(y, nota, 0.55, [0.5 * t, 1.1 * t])
        assert 0.4 < mitad < 0.6  # medido: 0,496 (T = 0,2 s) y 0,493 (T = 0,4 s)
        assert entero > 0.95  # medido: 1,002 y 0,991
        # Sin pisadas, la subida de pot0 = 1 dura 2,7 s: a T solo llega a T/2,7.
        lleno = rms(y, nota + 0.4, nota + 0.55)
        assert rms(sin_tap, nota + t - 0.01, nota + t + 0.01) / lleno < 0.3  # medido: 0,07 y 0,15


def test_swell_ritmico_nivel_comparable_al_plate() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        c = Controles(pots("0", "0.5", "1", "0.7", "0.5", "0"))
        y = rms(procesar(programa("swell_ritmico"), x, c).canales[0], 0, 1)
        assert 0.2 * plate < y < 2 * plate  # medido: 1,15× y 1,23×
