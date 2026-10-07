# SPDX-License-Identifier: MIT
"""Lee la UART del depurador BL616 y comprueba que la placa habla (Fase 02).

El BL616 expone dos puertos: el primero (``/dev/ttyUSB0``) es JTAG y el segundo
(``/dev/ttyUSB1``) es la UART de la FPGA.

Uso::

    make uart                                        # 5 s en /dev/ttyUSB1, exige "SOFIFI"
    .venv/bin/python scripts/leer_uart.py --segundos 30 --puerto /dev/ttyUSB1

Termina con código 0 si recibe al menos una línea con ``--esperar``. Con dos o más
líneas de ``hola_uart`` estima además el periodo entre mensajes: es una medida
gruesa del reloj de la placa (la marca de tiempo es la del PC).
"""

from __future__ import annotations

import argparse
import re
import sys
import time

import serial

LINEA_HOLA = re.compile(r"SOFIFI ([0-9A-F]{8})")


def leer(puerto: str, baudios: int, segundos: float) -> list[tuple[float, str]]:
    """Devuelve las líneas recibidas con la marca de tiempo del PC."""
    lineas: list[tuple[float, str]] = []
    with serial.Serial(puerto, baudios, timeout=0.2) as s:
        s.reset_input_buffer()
        fin = time.monotonic() + segundos
        while time.monotonic() < fin:
            crudo = s.readline()
            if crudo:
                lineas.append((time.monotonic(), crudo.decode("ascii", "replace").strip()))
    return lineas


def periodo_medio(lineas: list[tuple[float, str]]) -> float | None:
    """Segundos por incremento del contador, entre la primera y la última línea válida."""
    validas = [(t, int(m.group(1), 16)) for t, txt in lineas if (m := LINEA_HOLA.fullmatch(txt))]
    if len(validas) < 2 or validas[-1][1] == validas[0][1]:
        return None
    (t0, c0), (t1, c1) = validas[0], validas[-1]
    return (t1 - t0) / (c1 - c0)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--puerto", default="/dev/ttyUSB1")
    ap.add_argument("--baudios", type=int, default=115_200)
    ap.add_argument("--segundos", type=float, default=5.0)
    ap.add_argument("--esperar", default="SOFIFI", help="texto que debe aparecer")
    args = ap.parse_args(argv)

    lineas = leer(args.puerto, args.baudios, args.segundos)
    for _, txt in lineas:
        print(txt)
    periodo = periodo_medio(lineas)
    if periodo is not None:
        print(f"# periodo medio: {periodo:.4f} s por mensaje", file=sys.stderr)
    if any(args.esperar in txt for _, txt in lineas):
        return 0
    print(f"# no llegó {args.esperar!r} en {args.segundos} s por {args.puerto}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
