# SPDX-License-Identifier: MIT
"""Verifica el núcleo en la placa contra el modelo (Fase 05, hardware-in-the-loop).

Uso::

    make prog TOP=hil_nucleo
    .venv/bin/python scripts/hil_nucleo.py

Envía 'C' a rtl/top/hil_nucleo.v, recibe las muestras capturadas a velocidad
real, comprueba el CRC-32 y compara cada muestra con el modelo bit-exact
procesando el mismo estímulo. Termina con código 0 si todas coinciden.
"""

from __future__ import annotations

import argparse
import sys
import time
import zlib
from dataclasses import dataclass
from pathlib import Path

import serial
from sofifi.domain.ensamblador import ensamblar
from sofifi.domain.nucleo import Nucleo

RAIZ = Path(__file__).resolve().parent.parent
N_CAPTURA = 4096
POT = 0x400000  # 0,5 en S.23: los seis potenciómetros del top


def con_signo24(v: int) -> int:
    return v - (1 << 24) if v & (1 << 23) else v


def estimulo(k: int) -> tuple[int, int]:
    """El mismo que hil_nucleo.v: impulso, silencio y un triángulo desde la 1 024."""
    if k == 0:
        return 0x400000, -0x200000
    if k < 1024:
        return 0, 0
    t = k % 64
    triangulo = t - 16 if t < 32 else 48 - t
    return triangulo << 17, -(triangulo << 17)


@dataclass
class Resultado:
    muestras: int
    iguales: int
    crc_ok: bool
    ciclos: int | None
    primera_diferencia: str | None

    @property
    def correcto(self) -> bool:
        return self.crc_ok and self.iguales == self.muestras > 0


def comprobar(lineas: list[str], n: int, programa: str = "plate") -> Resultado:
    """Compara las líneas recibidas (M, K, Z) con el modelo y comprueba el CRC."""
    muestras = [
        (con_signo24(int(t[2:8], 16)), con_signo24(int(t[8:14], 16)))
        for t in lineas
        if t.startswith("M ") and len(t) == 14
    ]
    ciclos = next((int(t[2:], 16) for t in lineas if t.startswith("K ")), None)
    crc_placa = next((int(t[2:], 16) for t in lineas if t.startswith("Z ")), None)
    datos = b"".join(
        (izq & 0xFFFFFF).to_bytes(3, "big") + (der & 0xFFFFFF).to_bytes(3, "big")
        for izq, der in muestras
    )
    crc_ok = crc_placa is not None and zlib.crc32(datos) == crc_placa

    fuente = (RAIZ / "programas" / f"{programa}.sasm").read_text(encoding="utf-8")
    modelo = Nucleo(ensamblar(fuente, programa))
    iguales, primera = 0, None
    for k in range(n):
        esperado = modelo.procesar(*estimulo(k), (POT,) * 6, 0)
        if k < len(muestras) and muestras[k] == esperado:
            iguales += 1
        elif primera is None:
            obtenido = muestras[k] if k < len(muestras) else None
            primera = f"muestra {k}: placa {obtenido}, modelo {esperado}"
    return Resultado(len(muestras), iguales, crc_ok, ciclos, primera)


def capturar(puerto: str, espera: float) -> list[str]:
    lineas: list[str] = []
    with serial.Serial(puerto, 115_200, timeout=0.5) as s:
        # El BL616 puede guardar bytes de un diseño anterior: se descartan antes
        # de pedir la captura (reset_input_buffer solo vacía el búfer del PC).
        s.reset_input_buffer()
        fin = time.monotonic() + 0.3
        while time.monotonic() < fin:
            s.read(4096)
        s.write(b"C")
        fin = time.monotonic() + espera
        while time.monotonic() < fin:
            crudo = s.readline()
            if crudo:
                lineas.append(crudo.decode("ascii", "replace").strip())
                if lineas[-1].startswith("Z "):
                    break
    return lineas


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--puerto", default="/dev/ttyUSB1")
    ap.add_argument("--espera", type=float, default=30.0, help="segundos máximos")
    args = ap.parse_args(argv)
    r = comprobar(capturar(args.puerto, args.espera), N_CAPTURA)
    print(f"hil: {r.muestras} muestras recibidas, {r.iguales} iguales al modelo")
    print(f"hil: CRC {'correcto' if r.crc_ok else 'INCORRECTO'}; máximo {r.ciclos} ciclos/muestra")
    if r.primera_diferencia:
        print(f"hil: primera diferencia en la {r.primera_diferencia}")
    return 0 if r.correcto and r.muestras == N_CAPTURA else 1


if __name__ == "__main__":
    sys.exit(main())
