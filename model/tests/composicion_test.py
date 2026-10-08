# SPDX-License-Identifier: MIT
"""Compositor de cadenas (ADR 0013): dos programas en uno, con los mismos bits.

La propiedad central: una cadena en serie da exactamente lo mismo que procesar
la entrada con el primer programa y su salida con el segundo. Si el compositor
mezclara registros, LFOs o memoria de los dos, la salida cambiaría.
"""

from __future__ import annotations

import random
from fractions import Fraction

import pytest
from sofifi.domain.aritmetica import cuantizar, dato
from sofifi.domain.cadena import Cadena, Eslabon, Modo, PotFisico
from sofifi.domain.composicion import componer, recursos
from sofifi.domain.ensamblador import ErrorEnsamblado, ensamblar
from sofifi.domain.isa import NUM_POTS
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, PROGRAMAS, programa

TEXTOS = {p.stem: p.read_text(encoding="utf-8") for p in PROGRAMAS.glob("*.sasm")}


def incluir(nombre: str) -> str:
    return (PROGRAMAS / nombre).read_text(encoding="utf-8")


def estimulo(segundos: float) -> Senal:
    """Impulso estéreo y después ruido: llega a todas las ramas de los dos programas."""
    azar = random.Random(13)
    n = int(segundos * FS)
    izq = [dato("0.5")] + [azar.randrange(-(1 << 21), 1 << 21) for _ in range(n - 1)]
    der = [dato("-0.25")] + [azar.randrange(-(1 << 21), 1 << 21) for _ in range(n - 1)]
    return Senal(FS, (tuple(izq), tuple(der)))


def constante(v: Fraction) -> int:
    """El valor que deja en un registro `sof 0, v` y `wrax`: D es S2.15."""
    return dato(Fraction(cuantizar(v, 15, 18, "D"), 1 << 15))


FISICOS = tuple(dato(v) for v in ("0.6", "0.35", "0.45", "0.7", "0", "0"))
FIJOS = (Fraction(3, 4), Fraction(1, 3), Fraction(1, 2), Fraction(3, 10))


@pytest.mark.parametrize(
    ("primero", "segundo"),
    [("tremolo", "plate"), ("delay", "spring"), ("saturacion", "hall"), ("tremolo", "tremolo")],
)
def test_serie_da_los_mismos_bits_que_dos_pasadas(primero: str, segundo: str) -> None:
    cadena = Cadena(
        "prueba",
        Modo.SERIE,
        (
            Eslabon(primero, tuple(PotFisico(k) for k in range(4))),
            Eslabon(segundo, FIJOS),
        ),
    )
    compuesto = ensamblar(componer(cadena, TEXTOS, incluir), "cadena")
    x = estimulo(0.15)
    y = procesar(compuesto, x, Controles(FISICOS))
    medio = procesar(programa(primero), x, Controles(FISICOS))
    pots_segundo = tuple(constante(v) for v in FIJOS) + (0,) * (NUM_POTS - len(FIJOS))
    esperado = procesar(programa(segundo), medio, Controles(pots_segundo))
    assert y.canales == esperado.canales


def test_paralelo_es_la_media_de_los_dos() -> None:
    cadena = Cadena(
        "prueba",
        Modo.PARALELO,
        (
            Eslabon("tremolo", tuple(PotFisico(k) for k in range(4))),
            Eslabon("spring", tuple(PotFisico(k) for k in range(4))),
        ),
    )
    compuesto = ensamblar(componer(cadena, TEXTOS, incluir), "cadena")
    x = estimulo(0.1)
    c = Controles(FISICOS)
    y = procesar(compuesto, x, c)
    a = procesar(programa("tremolo"), x, c)
    b = procesar(programa("spring"), x, c)
    for lado in range(2):
        for k, v in enumerate(y.canales[lado]):
            assert abs(2 * v - a.canales[lado][k] - b.canales[lado][k]) <= 2


def test_los_recursos_suman_los_de_cada_programa() -> None:
    cadena = Cadena("prueba", Modo.SERIE, (Eslabon("tremolo"), Eslabon("plate")))
    r = recursos(cadena, TEXTOS, incluir)
    compuesto = ensamblar(componer(cadena, TEXTOS, incluir), "cadena")
    assert r.instrucciones == len(compuesto.instrucciones)
    assert r.memoria == compuesto.palabras_memoria == programa("plate").palabras_memoria
    assert r.lfos == 2 and r.absolutas == 0 and r.excedidos() == []


def test_sin_lfos_libres_lo_dice_y_no_compone() -> None:
    cadena = Cadena("prueba", Modo.SERIE, (Eslabon("chorus"), Eslabon("plate")))
    assert recursos(cadena, TEXTOS, incluir).excedidos() == ["lfos"]
    with pytest.raises(ErrorEnsamblado, match="LFOs"):
        componer(cadena, TEXTOS, incluir)


def test_un_delay_y_un_plate_solo_esperan_memoria() -> None:
    """Delay y luego reverb: el caso que abre la SDRAM. Hoy solo falta memoria."""
    cadena = Cadena("prueba", Modo.SERIE, (Eslabon("delay"), Eslabon("plate")), "sdram")
    assert recursos(cadena, TEXTOS, incluir).excedidos() == ["memoria"]


def test_una_cadena_necesita_dos_programas_y_mandos_validos() -> None:
    with pytest.raises(ValueError, match="dos programas"):
        Cadena("x", Modo.SERIE, (Eslabon("plate"),))
    with pytest.raises(ValueError, match="pot9"):
        Cadena("x", Modo.SERIE, (Eslabon("plate", (PotFisico(9),)), Eslabon("plate")))
    with pytest.raises(ValueError, match="fuera de"):
        Cadena("x", Modo.SERIE, (Eslabon("plate", (Fraction(2),)), Eslabon("plate")))


def test_las_cadenas_rechazan_datos_imposibles() -> None:
    dos = (Eslabon("plate"), Eslabon("plate"))
    with pytest.raises(ValueError, match="requiere"):
        Cadena("x", Modo.SERIE, dos, "dsp")
    with pytest.raises(ValueError, match="posiciones"):
        Cadena("x", Modo.SERIE, dos, None, (Fraction(3, 2),))
    with pytest.raises(ValueError, match="más de 6 mandos"):
        Cadena("x", Modo.SERIE, (Eslabon("plate", (Fraction(0),) * 7), Eslabon("plate")))


def test_sin_registros_libres_lo_dice() -> None:
    """Tres resonadores en paralelo piden 63 registros: no hay 32."""
    cadena = Cadena("x", Modo.PARALELO, (Eslabon("resonador"),) * 3)
    assert "registros" in recursos(cadena, TEXTOS, incluir).excedidos()
    with pytest.raises(ErrorEnsamblado, match="registros libres"):
        componer(cadena, TEXTOS, incluir)


def test_un_cho_con_lfo_no_valido_falla() -> None:
    textos = {"malo": "mem d 10\nlfo 0 sin 2\ncho d, 1.0, rapido\n", "plate": TEXTOS["plate"]}
    with pytest.raises(ErrorEnsamblado, match="LFO no válido"):
        componer(Cadena("x", Modo.SERIE, (Eslabon("malo"), Eslabon("plate"))), textos, incluir)
