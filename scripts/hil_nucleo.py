# SPDX-License-Identifier: MIT
"""Verifica el núcleo en la placa contra el modelo (Fase 05, hardware-in-the-loop).

Uso::

    make prog TOP=hil_nucleo
    .venv/bin/python scripts/hil_nucleo.py

Envía 'C' a rtl/top/hil_nucleo.v, recibe las muestras capturadas a velocidad
real, comprueba el CRC-32 y compara cada muestra con el modelo bit-exact
procesando el mismo estímulo. Termina con código 0 si todas coinciden.

Con ``--traza K0`` pide la traza del núcleo desde la muestra K0 (cada cambio del
ACC, con su pc) y dice cuál es la primera instrucción que no coincide con el
modelo. Sirve para localizar un fallo de timing en el silicio (fails.md, F-15).
"""

from __future__ import annotations

import argparse
import sys
import time
import zlib
from dataclasses import dataclass
from pathlib import Path

import serial
from sofifi.adapters.archivos import ensamblar_archivo
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
    primera_muestra: int | None = None

    @property
    def correcto(self) -> bool:
        return self.crc_ok and self.iguales == self.muestras > 0


def comprobar(lineas: list[str], n: int, programa: str = "plate") -> Resultado:
    """Compara las líneas recibidas (M, K, Z) con el modelo y comprueba el CRC."""
    muestras = [
        (con_signo24(int(t[4:10], 16)), con_signo24(int(t[10:16], 16)))
        for t in lineas
        if t.startswith("M ") and len(t) == 16
    ]
    ciclos = next((int(t[2:], 16) & 0xFFFF for t in lineas if t.startswith("K ")), None)
    crc_placa = next((int(t[2:], 16) for t in lineas if t.startswith("Z ")), None)
    datos = b"".join(
        (izq & 0xFFFFFF).to_bytes(3, "big") + (der & 0xFFFFFF).to_bytes(3, "big")
        for izq, der in muestras
    )
    crc_ok = crc_placa is not None and zlib.crc32(datos) == crc_placa

    modelo = Nucleo(ensamblar_archivo(RAIZ / "programas" / f"{programa}.sasm"))
    iguales, primera, primera_k = 0, None, None
    for k in range(n):
        esperado = modelo.procesar(*estimulo(k), (POT,) * 6, 0)
        if k < len(muestras) and muestras[k] == esperado:
            iguales += 1
        elif primera is None:
            obtenido = muestras[k] if k < len(muestras) else None
            primera = f"muestra {k}: placa {obtenido}, modelo {esperado}"
            primera_k = k
    return Resultado(len(muestras), iguales, crc_ok, ciclos, primera, primera_k)


def traza_esperada(k0: int, n: int, programa: str = "plate") -> list[tuple[int, int]]:
    """La traza que graba hil_nucleo.v con 'T': (pc, ACC) en cada cambio del ACC.

    El núcleo pone ACC = 0 y pc = 0 al empezar cada muestra; cada instrucción deja
    el pc de la siguiente junto al ACC nuevo.
    """
    modelo = Nucleo(ensamblar_archivo(RAIZ / "programas" / f"{programa}.sasm"))
    for k in range(k0):
        modelo.procesar(*estimulo(k), (POT,) * 6, 0)
    salida: list[tuple[int, int]] = []
    previo, k = modelo.acc, k0
    while len(salida) < n:
        if previo != 0:
            salida.append((0, 0))
            previo = 0
        pasos: list[tuple[int, int]] = []
        modelo.procesar(*estimulo(k), (POT,) * 6, 0, pasos)
        for pc, acc in pasos:
            if acc != previo:
                salida.append((pc, acc))
                previo = acc
        k += 1
    return salida[:n]


def comprobar_traza(lineas: list[str], k0: int, programa: str = "plate") -> str | None:
    """Compara la traza de la placa con la del modelo; None si coinciden."""
    k_linea = next((int(t[2:], 16) for t in lineas if t.startswith("K ")), None)
    if k_linea is None:
        return "no llegó la línea K"
    entradas = k_linea >> 16
    placa = [int(t[2:], 16) for t in lineas if t.startswith("M ") and len(t) == 16][:entradas]
    esperada = traza_esperada(k0, entradas, programa)
    if len(placa) < entradas:
        return f"llegaron {len(placa)} entradas de {entradas}"
    for i, (v, (pc, acc)) in enumerate(zip(placa, esperada, strict=True)):
        pc_placa, acc_placa = v >> 47, v & ((1 << 47) - 1)
        acc_placa -= (1 << 47) if acc_placa >> 46 else 0
        if (pc_placa, acc_placa) != (pc & 0x7F, acc >> 1):
            return (
                f"entrada {i}: placa pc={pc_placa} ACC/2={acc_placa}; "
                f"modelo pc={pc & 0x7F} ACC/2={acc >> 1} (instrucción {pc - 1})"
            )
    return None


def capturar(puerto: str, espera: float, orden: bytes = b"C", baudios: int = 115_200) -> list[str]:
    lineas: list[str] = []
    with serial.Serial(puerto, baudios, timeout=0.5) as s:
        # El BL616 puede guardar bytes de un diseño anterior: se descartan antes
        # de pedir la captura (reset_input_buffer solo vacía el búfer del PC).
        s.reset_input_buffer()
        fin = time.monotonic() + 0.3
        while time.monotonic() < fin:
            s.read(4096)
        s.write(orden)
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
    ap.add_argument("--traza", type=int, metavar="K0", help="pide la traza desde la muestra K0")
    args = ap.parse_args(argv)
    if args.traza is not None:
        orden = b"T" + args.traza.to_bytes(2, "big")
        diferencia = comprobar_traza(capturar(args.puerto, args.espera, orden), args.traza)
        if diferencia is None:
            print("hil: traza igual al modelo")
        else:
            print(f"hil: traza distinta: {diferencia}")
        return 0 if diferencia is None else 1
    r = comprobar(capturar(args.puerto, args.espera), N_CAPTURA)
    print(f"hil: {r.muestras} muestras recibidas, {r.iguales} iguales al modelo")
    print(f"hil: CRC {'correcto' if r.crc_ok else 'INCORRECTO'}; máximo {r.ciclos} ciclos/muestra")
    if r.primera_diferencia:
        print(f"hil: primera diferencia en la {r.primera_diferencia}")
    return 0 if r.correcto and r.muestras == N_CAPTURA else 1


if __name__ == "__main__":
    sys.exit(main())
