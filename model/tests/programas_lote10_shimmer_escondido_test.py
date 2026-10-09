# SPDX-License-Identifier: MIT
"""Lote 10 del catálogo: shimmer_escondido.

Las pruebas miden lo que distingue al programa del shimmer: con pot3 bajo, la
octava desaparece del todo; con ducking, la octava se calla mientras se toca y
aparece en la cola; y el nivel queda acotado frente al plate.
"""

from __future__ import annotations

from functools import cache

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, potencia, pots, programa, rms, tono

F = 196.0


@cache
def _salida(nombre: str, amplitud: float, *valores: str) -> tuple[int, ...]:
    """Tono de 196 Hz durante 0,4 s y 0,6 s de cola."""
    x = Senal(FS, (tono(F, 0.4, amplitud) + (0,) * int(0.6 * FS),))
    return procesar(programa(nombre), x, Controles(pots(*valores))).canales[0]


def test_con_pot3_bajo_no_hay_octava() -> None:
    """Por debajo del umbral, el envío vale 0 exacto: la salida es la del plate."""
    plate = _salida("plate", 0.5, "0.7", "0.3", "1")
    cero = _salida("shimmer_escondido", 0.5, "0.7", "0.3", "1", "0", "0.5", "0.5")
    casi = _salida("shimmer_escondido", 0.5, "0.7", "0.3", "1", "0.03", "0.5", "0.5")
    assert casi == cero  # el SKP del umbral: 0,03 da lo mismo que 0, bit a bit
    dif = tuple(a - b for a, b in zip(cero, plate, strict=True))
    # Solo difiere el CLIP del tanque. Medido: 0,010 y 1,03.
    assert rms(dif, 0, 1.0) < 0.05 * rms(plate, 0, 1.0)
    assert potencia(cero, 2 * F, 0.5, 1.0) < 1.5 * potencia(plate, 2 * F, 0.5, 1.0)


def test_la_octava_se_esconde_mientras_se_toca() -> None:
    """Con ducking, la octava (2f) es mucho mayor en la cola que mientras se toca."""
    x = Senal(FS, (tono(F, 0.8, 0.3) + (0,) * int(0.7 * FS),))

    def octava(ducking: str) -> tuple[float, float]:
        c = Controles(pots("0.7", "0.3", "1", "1", ducking, "0.5"))
        y = procesar(programa("shimmer_escondido"), x, c).canales[0]
        return potencia(y, 2 * F, 0.4, 0.8), potencia(y, 2 * F, 1.0, 1.5)

    tocando, cola = octava("1")
    tocando_sin, cola_sin = octava("0")
    assert cola > 25 * tocando  # medido: ×50
    assert tocando < 0.2 * tocando_sin  # medido: 0,12
    assert cola > 0.5 * cola_sin  # medido: 0,74; la octava no se pierde, se aplaza


def test_nivel_acotado_frente_al_plate() -> None:
    for amplitud in (0.1, 0.5):
        plate = _salida("plate", amplitud, "0.7", "0.3", "1")
        y = _salida("shimmer_escondido", amplitud, "0.7", "0.3", "1", "1", "0", "1")
        # Medido: 1,19 (amplitud 0,1) y 1,12 (amplitud 0,5) veces el plate.
        assert 0.2 * rms(plate, 0, 1.0) < rms(y, 0, 1.0) < 2 * rms(plate, 0, 1.0)
