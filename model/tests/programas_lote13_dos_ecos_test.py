# SPDX-License-Identifier: MIT
"""Lote 13 del catálogo: dos_ecos, dos ecos a ritmo para el post-rock.

Las pruebas miden lo que distingue al programa de delay, cinta y pingpong:
los dos primeros ecos caen en T y en k·T según la zona de pot3; el eco de
cinta (B) es más oscuro que el limpio (A); la difusión emborrona las
repeticiones; y el nivel queda acotado con la realimentación al máximo.
"""

from __future__ import annotations

from sofifi.domain.aritmetica import UNO
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, pots, programa, rms, tono

ANTES = 0.3  # silencio inicial: los tiempos se asientan (el deslizamiento para)
T = round(32768 * (0.15 + 0.33))  # toma A con pot0 = 0,5: 15 729 muestras (0,32 s)


def _impulso(mandos: tuple[str, ...], segundos: float) -> list[float]:
    """Salida a partir del impulso, en valores absolutos."""
    x = [0] * int((ANTES + segundos) * FS)
    i0 = int(ANTES * FS)
    x[i0] = UNO // 2
    y = procesar(programa("dos_ecos"), Senal(FS, (tuple(x),)), Controles(pots(*mandos)))
    return [abs(v) / UNO for v in y.canales[0][i0:]]


def _ecos(s: list[float]) -> list[int]:
    """Posición del máximo de cada grupo de picos por encima de 0,02."""
    grupos: list[tuple[int, float]] = []
    for k in range(1, len(s) - 1):
        if s[k] > 0.02 and s[k] >= s[k - 1] and s[k] >= s[k + 1]:
            if grupos and k - grupos[-1][0] < 200:
                if s[k] > grupos[-1][1]:
                    grupos[-1] = (k, s[k])
            else:
                grupos.append((k, s[k]))
    return [k for k, _ in grupos]


def test_dos_ecos_caen_en_t_y_en_k_por_t() -> None:
    """Sin realimentación ni difusión: A en T y B en ½, ⅔, ¾ o 1,5 de T."""
    for zona, k in (("0.1", 1 / 2), ("0.4", 2 / 3), ("0.6", 3 / 4), ("0.9", 3 / 2)):
        ecos = _ecos(_impulso(("0.5", "0", "1", zona, "0.5", "0"), max(k, 1) * T / FS + 0.02))
        assert len(ecos) == 2
        b, a = sorted(ecos, key=lambda e: abs(e - T))[::-1]
        assert abs(a - T) < 10  # medido: 4 muestras antes
        assert abs(b - k * T) < 40  # medido: 7 860, 10 472, 11 779 y 23 574 (wow ±32)


def test_dos_ecos_la_cinta_es_oscura_y_la_difusion_emborrona() -> None:
    """B pierde agudos frente a A; con difusión, la cola pierde los picos de cada eco."""
    s = _impulso(("0.5", "0", "1", "0.6", "0.5", "0"), 0.4)

    def brillo(centro: int) -> float:
        seg = s[centro - 150 : centro + 150]
        return sum((seg[j] - seg[j - 1]) ** 2 for j in range(1, len(seg))) / sum(v * v for v in seg)

    assert brillo(T) > 3 * brillo(round(0.75 * T))  # medido: 1,23 y 0,26

    def cresta(difusion: str) -> float:
        cola = _impulso(("0.3", "0.8", "1", "0.6", "0.5", difusion), 1.1)[
            int(0.6 * FS) : int(1.1 * FS)
        ]
        return float(max(cola) / (sum(v * v for v in cola) / len(cola)) ** 0.5)

    assert cresta("0") > 3 * cresta("1")  # medido: 110 y 36


def test_dos_ecos_nivel_comparable_al_plate() -> None:
    """Con la realimentación al máximo y el tiempo más corto, el nivel queda cerca del plate."""
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        izq = procesar(
            programa("dos_ecos"), x, Controles(pots("0", "1", "1", "0.1", "0", "0"))
        ).canales[0]
        assert 0.2 * plate < rms(izq, 0, 1) < 2 * plate  # medido: ×1,27 (0,1) y ×1,29 (0,5)
        assert max(abs(v) for v in izq) < 0.98 * UNO
