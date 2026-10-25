# SPDX-License-Identifier: MIT
"""Salida de 1 bit (ADR 0015): relación señal/ruido, estabilidad y determinismo.

Las medidas se hacen en régimen permanente. Si la ventana incluye el arranque,
el escalón de la primera muestra ensucia todo el espectro y la SNR medida baja
a unos 47 dB: eso es un artefacto de la medida, no del modulador.
"""

from __future__ import annotations

import numpy as np
import pytest
from sofifi.domain.aritmetica import FS_EXACTA, UNO
from sofifi.domain.salida_1bit import (
    INTERPOLACION,
    K2,
    LIMITE,
    MOD_BITS,
    InterpoladorCIC,
    ModuladorSigmaDelta,
    Salida1Bit,
    recortar,
)

PERIODO = 256  # muestras de audio por ventana
CICLOS = 5  # periodos del tono en la ventana: 953,7 Hz
BANDA_HZ = 20_000.0
RELOJ_HZ = float(FS_EXACTA) * 2048


def _tono(amplitud: float, muestras: int) -> list[int]:
    n = np.arange(muestras)
    return [round(float(v)) for v in amplitud * UNO * np.sin(2 * np.pi * CICLOS * n / PERIODO)]


def _snr_en_banda(bits: list[int]) -> float:
    """SNR del flujo de 1 bit en 0-20 kHz, con una ventana coherente."""
    ventana = np.array(bits[-PERIODO * 2048 :], dtype=np.float64) * 2 - 1
    potencia = 2 * np.abs(np.fft.rfft(ventana) / len(ventana)) ** 2
    frecuencia = np.fft.rfftfreq(len(ventana), d=1.0 / RELOJ_HZ)
    senal = potencia[CICLOS]
    en_banda = (frecuencia > 0) & (frecuencia <= BANDA_HZ)
    return float(10 * np.log10(senal / (potencia[en_banda].sum() - senal)))


@pytest.mark.parametrize(
    ("amplitud", "snr_minima"),
    [(0.8, 115.0), (0.5, 110.0), (0.25, 105.0)],
)
def test_snr_en_banda(amplitud: float, snr_minima: float) -> None:
    """Entre −12 y −2 dBFS, la SNR en banda pasa de 100 dB (ADR 0015)."""
    bits = list(Salida1Bit().flujo(_tono(amplitud, 2 * PERIODO)))
    assert _snr_en_banda(bits) > snr_minima


def test_el_cic_interpola_linealmente() -> None:
    """El CIC de S = 2 es una interpolación lineal, con un retardo de 2 muestras.

    Es la propiedad que justifica la estructura: dos medias móviles de longitud
    R dan un núcleo triangular.
    """
    muestras = _tono(0.8, 40)
    interpolador = InterpoladorCIC()
    salida = [v for x in muestras for v in interpolador.muestra(x)]
    for indice in range(1, len(muestras)):
        anterior, siguiente = muestras[indice - 1], muestras[indice]
        for paso in range(INTERPOLACION):
            exacto = anterior + (siguiente - anterior) * (paso + 1) / INTERPOLACION
            # El truncado del integrador (>> GANANCIA_CIC) deja menos de 1 LSB.
            assert abs(salida[indice * INTERPOLACION + paso] - exacto) < 1.0


def test_recorte_simetrico() -> None:
    assert recortar(UNO) == LIMITE
    assert recortar(-UNO) == -LIMITE
    assert recortar(0) == 0
    assert recortar(LIMITE - 1) == LIMITE - 1


@pytest.mark.parametrize("caso", ["seno", "cuadrada", "ruido", "dc", "silencio"])
def test_los_integradores_no_saturan(caso: str) -> None:
    """Con el recorte, ningún caso a escala plena saca al modulador de rango."""
    azar = np.random.default_rng(7)
    n = 2 * PERIODO
    entradas = {
        "seno": _tono(1.0, n),
        "cuadrada": [UNO - 1 if (k // 16) % 2 == 0 else -UNO for k in range(n)],
        "ruido": [int(v) for v in azar.integers(-UNO, UNO, size=n)],
        "dc": [UNO - 1] * n,
        "silencio": [0] * n,
    }[caso]
    salida = Salida1Bit()
    tope = (1 << (MOD_BITS - 1)) - 1
    peor = 0
    for x in entradas:
        salida.muestra(x)
        peor = max(peor, abs(salida.modulador.integra1), abs(salida.modulador.integra2))
    assert peor < tope, f"{caso}: {peor / UNO:.2f} veces la escala plena"
    assert peor / UNO < 9.0  # medido: 7,32 como mucho (ADR 0015)


def test_dc_a_escala_plena_sigue_al_recorte() -> None:
    """Con DC a escala plena, la media del flujo es la del recorte: 13/16."""
    bits = list(Salida1Bit().flujo([UNO - 1] * PERIODO))
    media = sum(2 * b - 1 for b in bits) / len(bits)
    assert media == pytest.approx(LIMITE / UNO, abs=0.01)


def test_silencio_no_tiene_tono_de_reposo() -> None:
    """Con la entrada a cero, la salida alterna y no deja nada en banda."""
    bits = list(Salida1Bit().flujo([0] * 2 * PERIODO))
    ventana = np.array(bits[-PERIODO * 2048 :], dtype=np.float64) * 2 - 1
    potencia = 2 * np.abs(np.fft.rfft(ventana) / len(ventana)) ** 2
    frecuencia = np.fft.rfftfreq(len(ventana), d=1.0 / RELOJ_HZ)
    en_banda = (frecuencia > 0) & (frecuencia <= BANDA_HZ)
    assert 10 * np.log10(potencia[en_banda].sum() + 1e-300) < -150.0


def test_determinista() -> None:
    muestras = _tono(0.5, 8)
    assert list(Salida1Bit().flujo(muestras)) == list(Salida1Bit().flujo(muestras))


def test_el_modulador_arranca_en_uno() -> None:
    """El contrato con el RTL incluye el estado tras el reset (ADR 0003)."""
    modulador = ModuladorSigmaDelta()
    assert modulador.bit == 1
    assert modulador.integra1 == 0
    assert modulador.integra2 == 0
    assert modulador.paso(0) == 0  # con la entrada a cero, alterna
    assert K2 == 4
