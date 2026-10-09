# SPDX-License-Identifier: MIT
"""Lote 13 del catálogo: relevo, un freeze de dos capas con fundido, bend y vibrato.

Las pruebas miden lo que distingue al programa de freeze, sostenido y looper:
una pisada nueva congela el acorde nuevo y lo funde sobre el viejo sin clic,
y la capa congelada cambia de afinación con pot1. El nivel queda acotado.
"""

from __future__ import annotations

from sofifi.domain.aritmetica import UNO
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, potencia, pots, programa, rms, tono

F1, F2 = 330.0, 294.0  # «mi» y «re»


def _pisadas(*inicios: float) -> tuple[tuple[int, int], ...]:
    return tuple((int(a * FS), int((a + 0.05) * FS)) for a in inicios)


def _salto_maximo(v: tuple[int, ...], a: float, b: float) -> float:
    """Mayor diferencia entre dos muestras seguidas: un corte la dispara."""
    s = v[int(a * FS) : int(b * FS)]
    return max(abs(s[k] - s[k - 1]) for k in range(1, len(s))) / UNO


def test_relevo_sustituye_el_acorde_sin_corte() -> None:
    """Se congela F1; la segunda pisada, tocando F2, lo releva en un fundido de 0,37 s.

    La primera grabación acaba a 0,39 s y su fundido, a 0,76 s. La segunda
    graba de 0,80 a 1,14 s y funde hasta 1,51 s. pot2 = 1: solo la capa.
    """
    x = Senal(FS, (tono(F1, 0.6, 0.3) + tono(F2, 0.6, 0.3) + (0,) * int(0.8 * FS),))
    c = Controles(pots("0.5", "0.5", "1", "0", "1", "1"), tramos_sw=_pisadas(0.05, 0.8))
    y = procesar(programa("relevo"), x, c).canales[0]

    def f1_sobre_f2(a: float, b: float) -> float:
        return potencia(y, F1, a, b) / potencia(y, F2, a, b)

    assert f1_sobre_f2(0.8, 1.1) > 20  # medido: ×727; la capa es F1
    assert f1_sobre_f2(1.6, 2.0) < 0.01  # medido: 0,0018; el relevo está hecho
    # Sin corte: el fundido no salta más que la capa quieta.
    quieta = max(_salto_maximo(y, 0.8, 1.1), _salto_maximo(y, 1.6, 2.0))
    assert _salto_maximo(y, 1.1, 1.55) < 1.6 * quieta  # medido: ×1,34
    # Sin hueco ni golpe de nivel: el fundido es de igual potencia.
    nivel = rms(y, 1.6, 2.0)
    tramos = [rms(y, k / 100, k / 100 + 0.02) for k in range(110, 155)]
    assert 0.6 * nivel < min(tramos) and max(tramos) < 1.5 * nivel  # medido: ×0,70 y ×1,28


def test_relevo_el_bend_desplaza_la_capa() -> None:
    """Con pot1 en los extremos, la capa congelada suena 2 semitonos abajo o arriba."""
    x = Senal(FS, (tono(F1, 0.45, 0.3) + (0,) * int(0.8 * FS),))

    def capa(bend: str) -> tuple[int, ...]:
        c = Controles(pots("0", bend, "1", "0", "1", "1"), tramos_sw=_pisadas(0.02))
        return procesar(programa("relevo"), x, c).canales[0]

    abajo, arriba = capa("0"), capa("1")
    f_abajo, f_arriba = F1 * 2 ** (-2 / 12), F1 * 2 ** (2 / 12)
    # medido: ×493 y ×152
    assert potencia(abajo, f_abajo, 0.6, 1.2) > 100 * potencia(abajo, F1, 0.6, 1.2)
    assert potencia(arriba, f_arriba, 0.6, 1.2) > 100 * potencia(arriba, F1, 0.6, 1.2)


def test_relevo_nivel() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        c = Controles(pots("0.5", "0.5", "1", "0.3", "0.5", "0.5"), tramos_sw=_pisadas(0.02))
        nivel = rms(procesar(programa("relevo"), x, c).canales[0], 0, 1)
        assert 0.2 * plate < nivel < 2 * plate  # medido: ×0,70 y ×0,82
