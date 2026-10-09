# SPDX-License-Identifier: MIT
"""Looper: el loop se repite idéntico, 2× sube una octava y el reverse invierte.

Son los criterios de aceptación de la Fase 07. Se graba con el footswitch
pulsado y la entrada calla al soltarlo: a partir de ahí, la salida es solo el
loop (pot0 = 1). Al soltar, el loop suena una muestra después.
"""

from __future__ import annotations

import random

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, frecuencias, pots, programa, tono

L = 4883  # 0,1 s de grabación


def ruido(n: int, semilla: int = 3) -> tuple[int, ...]:
    azar = random.Random(semilla)
    return tuple(azar.randrange(-(1 << 21), 1 << 21) for _ in range(n))


def tocar(
    x: tuple[int, ...], velocidad: str, sentido: str, tramos: tuple[tuple[int, int], ...]
) -> tuple[int, ...]:
    c = Controles(pots("1", velocidad, sentido, "1"), tramos_sw=tramos)
    return procesar(programa("looper"), Senal(FS, (x,)), c).canales[0]


def sigue(y: tuple[int, ...], loop: tuple[int, ...], paso: int, desde: int, n: int) -> bool:
    """True si y[desde:desde+n] recorre `loop` de `paso` en `paso` desde algún punto."""
    for j in (j for j, v in enumerate(loop) if v == y[desde]):
        if all(y[desde + t] == loop[(j + paso * t) % len(loop)] for t in range(n)):
            return True
    return False


X = ruido(L) + (0,) * (6 * L)
LOOP = tocar(X, "0.5", "0", ((0, L),))
UNA_VUELTA = LOOP[L + 1 : 2 * L + 1]


def test_el_loop_se_repite_identico() -> None:
    assert max(map(abs, UNA_VUELTA)) > 1 << 20
    vueltas = [LOOP[L + 1 + k * L : L + 1 + (k + 1) * L] for k in range(5)]
    assert all(v == UNA_VUELTA for v in vueltas)


def test_2x_y_reverse_recorren_el_mismo_loop() -> None:
    assert sigue(tocar(X, "1", "0", ((0, L),)), UNA_VUELTA, 2, 3 * L, 2 * L)
    assert sigue(tocar(X, "0.5", "1", ((0, L),)), UNA_VUELTA, -1, 3 * L, 2 * L)
    assert sigue(tocar(X, "1", "1", ((0, L),)), UNA_VUELTA, -2, 3 * L, 2 * L)


def test_2x_suena_una_octava_arriba_y_medio_una_abajo() -> None:
    x = tono(440, 0.2, 0.5) + (0,) * FS
    for velocidad, esperada in (("0.5", 440), ("1", 880), ("0", 220)):
        f = frecuencias(tocar(x, velocidad, "0", ((0, int(0.2 * FS)),)), 0.4, 1.0)
        assert all(abs(v / esperada - 1) < 0.01 for v in f), (velocidad, f)


def test_overdub_suma_o_reemplaza() -> None:
    nuevo = ruido(L, semilla=4)
    x = X[: 2 * L] + nuevo + (0,) * (4 * L)
    tramos = ((0, L), (2 * L, 3 * L))  # graba; deja sonar; overdub de una vuelta
    for realimentacion in ("1", "0"):
        c = Controles(pots("1", "0.5", "0", realimentacion), tramos_sw=tramos)
        y = procesar(programa("looper"), Senal(FS, (x,)), c).canales[0]
        despues = y[4 * L : 5 * L]
        # Sin realimentación solo queda lo nuevo; con ella, lo viejo y lo nuevo.
        assert sigue(y, despues, 1, 5 * L, L)
        energia_vieja = sum(abs(a) for a in UNA_VUELTA)
        energia = sum(abs(a) for a in despues)
        assert (energia > 1.2 * energia_vieja) == (realimentacion == "1")


def test_medio_interpola_la_vuelta_con_el_principio() -> None:
    # A ½×, la muestra entre la última y la primera es su media (F-32).
    y = tocar(X, "0", "0", ((0, L),))
    m = UNA_VUELTA
    i = next(k for k in range(3 * L, 7 * L) if y[k] == m[-1] and y[k - 2] == m[-2])
    assert abs(y[i + 1] - (m[-1] + m[0]) // 2) <= 1
    assert y[i + 2] == m[0]
