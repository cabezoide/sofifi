# SPDX-License-Identifier: MIT
"""Lote 14 del catálogo: semilla, reverb nube con primeras reflexiones elegidas por una semilla.

Las pruebas miden lo que distingue al programa de cloud y bloom: cada zona de
pot3 da otras primeras reflexiones, y la misma zona da los mismos bits; la
cola de las líneas en paralelo sigue a pot0 y se congela con sw; y el nivel
queda acotado frente al plate.
"""

from __future__ import annotations

from sofifi.domain.aritmetica import UNO
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, impulso, pots, programa, rms, tono

TEMPRANO = int(0.1 * FS)  # las tomas tempranas caen en los primeros 108 ms


def _salida(
    mandos: tuple[str, ...], segundos: float, sw: tuple[tuple[int, int], ...] = ()
) -> tuple[tuple[int, ...], ...]:
    c = Controles(pots(*mandos), tramos_sw=sw)
    return procesar(programa("semilla"), impulso(segundos), c).canales


def _picos(semilla: str) -> tuple[int, ...]:
    """Posiciones de las cuatro muestras más fuertes de los primeros 100 ms (izquierda)."""
    y = _salida(("0.5", "0.3", "1", semilla, "0", "0"), 0.11)[0][:TEMPRANO]
    return tuple(sorted(sorted(range(len(y)), key=lambda k: -abs(y[k]))[:4]))


def test_semilla_cada_zona_da_otras_primeras_reflexiones() -> None:
    """Las 8 zonas de pot3 dan 8 patrones; dentro de una zona, los bits son iguales."""
    patrones = {_picos(f"{0.125 * n + 0.05:.3f}") for n in range(8)}
    assert len(patrones) == 8  # medido: picos en 1 220, 961, 702, 444, 294, 553, 811 y 1 070
    a = _salida(("0.5", "0.3", "1", "0.05", "0", "0"), 0.11)[0][:TEMPRANO]
    b = _salida(("0.5", "0.3", "1", "0.1", "0", "0"), 0.11)[0][:TEMPRANO]
    assert a == b  # misma zona: la misma semilla, la misma respuesta
    c = _salida(("0.5", "0.3", "1", "0.95", "0", "0"), 0.11)[0][:TEMPRANO]
    diferencia = rms(tuple(x - y for x, y in zip(a, c, strict=True)), 0, 0.1)
    assert diferencia > rms(a, 0, 0.1)  # medido: ×1,35 (sin correlación: ×1,41)


def test_semilla_la_cola_sigue_al_decay_y_se_congela() -> None:
    """La cola cae más despacio con pot0 alto; con sw, se mantiene."""

    def caida(decay: str) -> float:
        y = _salida((decay, "0.3", "1", "0.5", "0", "0"), 0.6)[0]
        return rms(y, 0.4, 0.6) / rms(y, 0.1, 0.3)

    corta, media, larga = caida("0.1"), caida("0.5"), caida("0.9")
    assert corta < 0.02 < media < 0.15 < 0.3 < larga  # medido: 0,008, 0,068 y 0,40
    sw = ((int(0.3 * FS), int(0.9 * FS)),)
    y = _salida(("0.5", "0.3", "1", "0.5", "0", "0"), 0.9, sw)[0]
    assert rms(y, 0.7, 0.9) > 0.9 * rms(y, 0.4, 0.6)  # medido: 0,00038 y 0,00039


def test_semilla_nivel_comparable_al_plate() -> None:
    """Con un tono a 0,1 y a 0,5, el RMS queda entre 0,2× y 2× el del plate, en estéreo."""
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        y = procesar(
            programa("semilla"), x, Controles(pots("0.7", "0.3", "1", "0.5", "0", "0"))
        ).canales
        for canal in y:
            # medido: ×0,56-0,67 (0,1) y ×0,66-0,79 (0,5)
            assert 0.2 * plate < rms(canal, 0, 1) < 2 * plate
            assert max(abs(v) for v in canal) < 0.98 * UNO
