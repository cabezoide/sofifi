# SPDX-License-Identifier: MIT
"""Prueba de la microSD en la placa (Fase 08): carga ranuras y las compara con el modelo.

Uso (antes, escribir la imagen en la tarjeta: docs/microsd.md)::

    make prog TOP=prueba_sd
    .venv/bin/python scripts/prueba_sd.py --imagen build/banco.img

Pide el estado a rtl/top/prueba_sd.v ('S'): qué revisión del PMOD TF respondió
y el código de error de sd_spi. Después carga cada ranura ('L' + 2 bytes) y
compara las instrucciones, la memoria y el CRC-32 del microcódigo escrito con lo
que lee el modelo de la misma imagen (sofifi.domain.banco). Termina con código
0 si todas coinciden.
"""

from __future__ import annotations

import argparse
import sys
import time
import zlib
from pathlib import Path

import serial
from sofifi.domain.banco import BLOQUE, leer_cabecera, leer_programa
from sofifi.domain.isa import codificar

ERRORES_SD = {
    0: "ninguno",
    1: "CMD0",
    2: "CMD8 (¿tarjeta de la versión 1?)",
    3: "ACMD41",
    4: "CMD58",
    5: "CMD17",
    6: "token de datos",
}
MOTIVOS = {
    1: "error de la SD",
    2: "cabecera",
    3: "CRC de la cabecera",
    4: "ranura fuera del banco",
    5: "metadatos",
    6: "LFO",
    7: "código de operación o salto",
    8: "CRC",
    9: "CRC en la escritura",
}


def lineas(s: serial.Serial, letras: str, espera: float = 5.0) -> dict[str, int]:
    """Lee líneas "<letra> <hex>" hasta tener todas las ``letras`` o una F."""
    vistas: dict[str, int] = {}
    fin = time.monotonic() + espera
    while time.monotonic() < fin and not (set(letras) <= set(vistas) or "F" in vistas):
        t = s.readline().decode("ascii", "replace").strip()
        if len(t) == 10 and t[1] == " ":
            vistas[t[0]] = int(t[2:], 16)
    return vistas


def crc_microcodigo(palabras: list[int]) -> int:
    return zlib.crc32(b"".join(p.to_bytes(7, "big") for p in palabras))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--imagen", type=Path, required=True, help="la imagen escrita en la tarjeta")
    ap.add_argument("--puerto", default="/dev/ttyUSB1")
    ap.add_argument("--ranuras", type=int, nargs="*", help="por defecto, todas")
    args = ap.parse_args(argv)
    imagen = args.imagen.read_bytes()
    numero = leer_cabecera(imagen[:BLOQUE])
    fallos = 0
    with serial.Serial(args.puerto, 115_200, timeout=0.5) as s:
        s.reset_input_buffer()
        s.write(b"S")
        estado = lineas(s, "ME")
        revision = estado.get("M")
        error = ERRORES_SD.get(estado.get("E", -1), estado)
        print(f"sd: revisión del PMOD TF {revision or 'ninguna'}; error {error}")
        if not revision:
            return 1
        for k in args.ranuras if args.ranuras is not None else range(numero):
            s.write(b"L" + k.to_bytes(2, "big"))
            r = lineas(s, "IPX")
            if 0 <= k < numero:
                p = leer_programa(imagen, k)
                esperado = {
                    "I": len(p.instrucciones),
                    "P": p.palabras_memoria,
                    "X": crc_microcodigo([codificar(i) for i in p.instrucciones]),
                }
                ok = all(r.get(c) == v for c, v in esperado.items())
                nombre = p.nombre
            else:  # una ranura fuera del banco debe rechazarse
                ok, nombre = r.get("F") == 4, "(fuera del banco)"
            fallos += not ok
            detalle = f"motivo {MOTIVOS.get(r['F'], r['F'])}" if "F" in r else f"{r}"
            print(f"[{k}] {nombre}: {'igual' if ok else 'DISTINTO'} ({detalle})")
    print(f"sd: {'todo igual al modelo' if not fallos else f'{fallos} ranuras distintas'}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
