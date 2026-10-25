# SPDX-License-Identifier: MIT
"""`sofifi pista`: escribe y comprueba la pista de audio de la microSD (Fase 13).

Une el formato (``domain/pista.py``) con un WAV del disco. La salida de 1 bit es
mono (ADR 0015), así que dos canales se promedian. Los errores salen como
``argparse.ArgumentTypeError``, como en el resto de órdenes de la CLI.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from sofifi.adapters.wav import FuenteWav
from sofifi.domain import pista
from sofifi.domain.aritmetica import FS_EXACTA, FS_WAV
from sofifi.domain.estimulo import guitarra


def _segundos(muestras: int) -> float:
    return muestras / float(FS_EXACTA)


def listar_imagen(imagen: Path) -> list[str]:
    """Comprueba la cabecera y dice cuánto dura la pista."""
    try:
        muestras = pista.leer_cabecera(imagen.read_bytes()[: pista.BLOQUE])
    except pista.ErrorPista as exc:
        raise argparse.ArgumentTypeError(f"{imagen}: {exc}") from exc
    bloques = pista.bloques_de(muestras)
    return [
        f"{imagen}: {muestras} muestras, {_segundos(muestras):.2f} s, "
        f"{1 + bloques} bloques ({(1 + bloques) * pista.BLOQUE // 1024} KiB)"
    ]


def escribir_imagen(
    imagen: Path, entrada: Path | None, segundos: float | None, sintetica: bool = False
) -> list[str]:
    """Escribe la pista desde un WAV, o desde la guitarra sintética de las demos."""
    if sintetica:
        senal = guitarra() if segundos is None else guitarra(duracion_s=segundos)
        segundos = None  # la duración ya está en la señal
        entrada = Path("guitarra sintética")
    else:
        assert entrada is not None
        senal = FuenteWav(entrada).leer()
    canales = np.array(senal.canales, dtype=np.int64)
    mono = canales[0] if len(senal.canales) == 1 else canales.mean(axis=0).round().astype(np.int64)
    if segundos is not None:
        mono = mono[: round(segundos * FS_WAV)]
    muestras = [int(v) for v in np.clip((mono + 128) >> 8, -(1 << 15), (1 << 15) - 1)]
    try:
        datos = pista.escribir(muestras)
    except pista.ErrorPista as exc:
        raise argparse.ArgumentTypeError(f"{entrada}: {exc}") from exc
    imagen.parent.mkdir(parents=True, exist_ok=True)
    imagen.write_bytes(datos)
    return [
        f"{entrada} → {imagen}: {len(muestras)} muestras, "
        f"{_segundos(len(muestras)):.2f} s, {len(datos) // 1024} KiB"
    ]
