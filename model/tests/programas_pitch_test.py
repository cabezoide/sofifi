# SPDX-License-Identifier: MIT
"""Programas de pitch: octava, armonizador, doblador, escalera y shimmer de quinta.

Cada prueba mete un tono y mide en qué frecuencia sale la energía: el intervalo
es la propiedad que define a estos efectos.
"""

from __future__ import annotations

import pytest
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, potencia, pots, programa, tono

F = 330.0


def domina(y: tuple[int, ...], f: float, otras: tuple[float, ...], a: float, b: float) -> bool:
    """La energía en f es 20 veces la de cada una de las otras frecuencias."""
    p = potencia(y, f, a, b)
    return all(p > 20 * potencia(y, g, a, b) for g in otras)


def test_octava_baja_y_sube_una_octava() -> None:
    x = Senal(FS, (tono(F, 0.6, 0.4),))
    baja = procesar(programa("octava"), x, Controles(pots("1", "0", "0"))).canales[0]
    alta = procesar(programa("octava"), x, Controles(pots("0", "1", "0"))).canales[0]
    assert domina(baja, F / 2, (F, 2 * F), 0.2, 0.6)
    assert domina(alta, 2 * F, (F / 2, F), 0.2, 0.6)


@pytest.mark.parametrize(
    ("pot", "razon"),
    [("0.05", 0.5), ("0.25", 0.66742), ("0.4", 0.74915), ("0.6", 1.33484), ("0.75", 1.49831)],
)
def test_armonizador_da_el_intervalo_de_pot0(pot: str, razon: float) -> None:
    x = Senal(FS, (tono(F, 0.6, 0.4),))
    y = procesar(programa("armonizador"), x, Controles(pots(pot, "0", "1"))).canales[0]
    assert domina(y, F * razon, (F,), 0.2, 0.6)


def test_doblador_desafina_un_lado_arriba_y_otro_abajo() -> None:
    x = Senal(FS, (tono(1000, 1.0, 0.4),))
    izq, der = procesar(programa("doblador"), x, Controles(pots("1", "0", "1"))).canales
    arriba, abajo = 1014.55, 985.66  # ±25 cents
    assert potencia(izq, arriba, 0.3, 1.0) > 5 * potencia(izq, abajo, 0.3, 1.0)
    assert potencia(der, abajo, 0.3, 1.0) > 5 * potencia(der, arriba, 0.3, 1.0)


def test_escalera_cada_eco_sube_otra_octava() -> None:
    """Ráfaga de 330 Hz; eco cada 0,184 s con +12: 660 Hz y después 1 320 Hz."""
    x = (0,) * int(0.5 * FS) + tono(F, 0.1, 0.4) + (0,) * int(0.5 * FS)
    c = Controles(pots("0.95", "0.8", "1", "0.2"))
    y = procesar(programa("escalera"), Senal(FS, (x,)), c).canales[0]
    periodo = 0.05 + 0.2 * (0.72 - 0.05)
    for vuelta, f in ((1, 2 * F), (2, 4 * F)):
        a = 0.5 + vuelta * periodo + 0.01
        assert domina(y, f, (F, f / 2 if vuelta == 2 else 4 * F), a, a + 0.08)


def test_shimmer_quinta_anade_la_quinta() -> None:
    """Como el shimmer de +12, pero la energía nueva aparece a 1,5·f."""
    x = Senal(FS, (tono(F, 0.25, 0.3) + (0,) * int(0.9 * FS),))
    sin = procesar(programa("shimmer_quinta"), x, Controles(pots("0.6", "0.3", "1", "0")))
    con = procesar(programa("shimmer_quinta"), x, Controles(pots("0.6", "0.3", "1", "0.8")))
    q = 1.5 * F
    ratio_sin = potencia(sin.canales[0], q, 0.45, 1.1) / potencia(sin.canales[0], F, 0.45, 1.1)
    ratio_con = potencia(con.canales[0], q, 0.45, 1.1) / potencia(con.canales[0], F, 0.45, 1.1)
    assert ratio_con > 5 * ratio_sin
