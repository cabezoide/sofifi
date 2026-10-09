# SPDX-License-Identifier: MIT
"""Lote 13 del catálogo: viento, ráfagas de ruido filtrado que siguen al toque.

Las pruebas miden lo que distingue a viento de los demás programas:
- sin tocar, el fondo es ruido de banda ancha que no se repite, y su centro
  espectral se mueve con las ráfagas;
- al tocar, el viento sopla más fuerte que el fondo; con mezcla 0 sale el seco;
- el nivel queda acotado frente al plate.
"""

from __future__ import annotations

from sofifi.domain.nucleo import Nucleo
from sofifi.domain.senal import Controles, Senal
from sofifi.services.render import procesar
from tests.acustica import FS, frecuencias, pots, programa, rms, tono

REG_RUIDO = 12  # registro `r` de viento.sasm: el estado del generador


def test_viento_fondo_de_ruido_que_no_se_repite_y_se_mueve() -> None:
    """Sin entrada, con fondo: el ruido no entra en un ciclo corto y su centro se mueve."""
    nucleo = Nucleo(programa("viento"))
    p = pots("0.5", "0.5", "1", "0.5", "0.5", "1")
    estados, salida = [], []
    for _ in range(int(1.2 * FS)):
        salida.append(nucleo.procesar(0, 0, p)[0])
        estados.append(nucleo.regs[REG_RUIDO])
    # Un ciclo más corto que 1,2 s repetiría un estado: aquí no se repite ninguno.
    assert len(set(estados)) == len(estados)  # el periodo es 2^23 (172 s)
    y = tuple(salida)
    assert rms(y, 0.3, 1.2) > 0.03  # medido: 0,08
    # El centro espectral (cruces por cero en ventanas de 50 ms) se mueve con las ráfagas.
    centros = frecuencias(y, 0.3, 1.2)
    assert max(centros) > 1.8 * min(centros)  # medido: 1 433 y 3 838 Hz


def test_viento_sopla_mas_fuerte_al_tocar_y_mezcla_0_es_seco() -> None:
    nota = tono(196, 0.6, 0.3)
    x = Senal(FS, ((0,) * int(0.8 * FS) + nota,))
    viento = procesar(programa("viento"), x, Controles(pots("1", "0.3", "1", "0.8", "0.5", "0.2")))
    y = viento.canales[0]
    assert rms(y, 1.0, 1.4) > 3 * rms(y, 0.3, 0.7)  # medido: ×8,4
    seco = procesar(programa("viento"), x, Controles(pots("1", "0.3", "0", "0.8", "0.5", "0.2")))
    assert all(
        abs(a - b) <= 2 + abs(b) // 500 for a, b in zip(seco.canales[0], x.canales[0], strict=True)
    )


def test_viento_nivel() -> None:
    for amplitud in (0.1, 0.5):
        x = Senal(FS, (tono(196, 0.4, amplitud) + (0,) * int(0.6 * FS),))
        plate = rms(
            procesar(programa("plate"), x, Controles(pots("0.7", "0.3", "1"))).canales[0], 0, 1
        )
        c = Controles(pots("0.5", "0.5", "0.5", "0.5", "0.5", "0.3"))
        nivel = rms(procesar(programa("viento"), x, c).canales[0], 0, 1)
        assert 0.2 * plate < nivel < 2 * plate  # medido: ×0,55 y ×0,54
