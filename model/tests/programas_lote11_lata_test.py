# SPDX-License-Identifier: MIT
"""Lote 11 del catálogo: lata, eco de lata de aceite.

Las pruebas miden lo que distingue a lata de cinta y de bbd: el vibrato está
atado al tiempo de eco (un eco más largo da un vaivén más lento) y cada eco
pierde agudos. También comprueban que el primer eco llega en el tiempo de pot0.
"""

from __future__ import annotations

from itertools import pairwise

from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, impulso, potencia, pots, programa, rms, tono

ESPERA = int(0.25 * FS)  # el tiempo se desliza desde la mitad: se espera a que llegue


def _cruces(v: tuple[int, ...]) -> list[float]:
    """Cruces por cero hacia arriba, con interpolación lineal (en muestras)."""
    return [k - 1 + v[k - 1] / (v[k - 1] - v[k]) for k in range(1, len(v)) if v[k - 1] < 0 <= v[k]]


def _vibrato(pot0: str, segundos: float) -> tuple[float, float]:
    """Frecuencia (Hz) y variación relativa de tono del vibrato en el eco de un tono de 1 kHz."""
    x = Senal(FS, (tono(1000, segundos, 0.3),))
    y = procesar(programa("lata"), x, Controles(pots(pot0, "0", "1", "1"))).canales[0]
    c = _cruces(y[int(0.45 * FS) :])
    periodos = [b - a for a, b in pairwise(c)]
    m = 8  # media móvil de 8 periodos
    suave = [sum(periodos[i : i + m]) / m for i in range(len(periodos) - m)]
    t = [(c[i + m // 2] + c[i + m // 2 + 1]) / 2 for i in range(len(suave))]
    media = sum(suave) / len(suave)
    subidas = [t[i] for i in range(1, len(suave)) if suave[i - 1] < media <= suave[i]]
    f = (len(subidas) - 1) * FS / (subidas[-1] - subidas[0])
    return f, (max(suave) - min(suave)) / media / 2


def test_lata_primer_eco_en_el_tiempo_y_pierde_agudos() -> None:
    for pot0, ms in (("0", 60), ("1", 350)):
        x = impulso((ESPERA + 0.4 * FS) / FS, ESPERA)
        y = procesar(programa("lata"), x, Controles(pots(pot0, "0", "1", "0"))).canales[0]
        pico = max(range(len(y)), key=lambda k: abs(y[k])) - ESPERA
        assert abs(pico / FS * 1000 - ms) < 2  # medido: 60,1 y 349,9 ms
    # Con realimentación, cada eco tiene menos agudos (3 kHz) frente a graves (300 Hz).
    y = procesar(programa("lata"), impulso(0.6), Controles(pots("0.3", "0.7", "1", "0"))).canales[0]
    d = int((0.06 + 0.29 * 0.3) * FS)

    def brillo(n: int) -> float:
        a, b = (n * d - 200) / FS, (n * d + 600) / FS
        return potencia(y, 3000, a, b) / potencia(y, 300, a, b)

    b1, b2, b3 = brillo(1), brillo(2), brillo(3)
    assert b1 > 1.4 * b2 > 1.4 * 1.4 * b3  # medido: 0,59 · 0,34 · 0,20


def test_lata_vibrato_mas_lento_con_eco_mas_largo() -> None:
    corto, dev_corto = _vibrato("0.1", 1.05)  # eco de 89 ms
    largo, dev_largo = _vibrato("0.7", 2.2)  # eco de 263 ms
    assert 3.0 < corto < 4.1  # medido: 3,54 Hz (diseño: 0,9 Hz / 0,254)
    assert 1.0 < largo < 1.4  # medido: 1,20 Hz (diseño: 0,9 Hz / 0,751)
    # La profundidad crece con el tiempo: la variación de tono queda igual.
    assert 0.01 < dev_corto < 0.02 and 0.01 < dev_largo < 0.02  # medido: 1,4 % y 1,4 %


def test_lata_nivel() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        c = Controles(pots("0.3", "0.5", "0.5", "0.5", "0.5", "0.5"))
        nivel = rms(procesar(programa("lata"), x, c).canales[0], 0, 1)
        assert 0.2 * plate < nivel < 2 * plate  # medido: ×0,54 y ×0,63
