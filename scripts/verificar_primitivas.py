# SPDX-License-Identifier: MIT
"""Comprueba en el PC lo que envían los tops de prueba de primitivas (Fase 03).

Cuándo: Fase 03, y cada vez que cambie una primitiva de ``rtl/primitivas/``.

Uso::

    make prog TOP=prueba_dsp && .venv/bin/python scripts/verificar_primitivas.py dsp
    make prog TOP=prueba_bsram && .venv/bin/python scripts/verificar_primitivas.py bsram
    make prog TOP=prueba_pll && .venv/bin/python scripts/verificar_primitivas.py pll
    make prog TOP=prueba_fs && .venv/bin/python scripts/verificar_primitivas.py fs

Cada top envía líneas "<etiqueta> <hexadecimal>":

- ``D``: a (7 dígitos), b (5) y p (12), con signo. Se exige p = a·b y que
  lleguen las 25 combinaciones de casos extremos.
- ``B``: errA, errB, nuevosB, errC y vuelta (4 dígitos cada uno). Se exigen
  errores a 0.
- ``P``: bloqueado (1 dígito) y ciclos del PLL en un segundo del cristal (8).
  Se exige bloqueado = 1 y 100 000 000 ± 100 ciclos.
- ``S``: muestras en un segundo (8). Se exige 48 828 o 48 829 (fs = 48 828,125 Hz).
- ``R``: eco de cada byte enviado al empezar. Se exige el eco exacto y en orden.

Necesita la placa y la UART en ``/dev/ttyUSB1``. No escribe ficheros.
Salida: 0 si todas las líneas son correctas y llegó al menos una; 1 si no.
"""

from __future__ import annotations

import argparse
import sys
import time

import serial
from leer_uart import leer

EXTREMOS_A = (0, 1, -1, (1 << 26) - 1, -(1 << 26))
EXTREMOS_B = (0, 1, -1, (1 << 17) - 1, -(1 << 17))
PLL_ESPERADO = 100_000_000
PLL_TOLERANCIA = 100


def con_signo(valor: int, bits: int) -> int:
    return valor - (1 << bits) if valor & (1 << (bits - 1)) else valor


def operandos_dsp(hexa: str) -> tuple[int, int, int]:
    a = con_signo(int(hexa[0:7], 16), 28)
    b = con_signo(int(hexa[7:12], 16), 20)
    p = con_signo(int(hexa[12:24], 16), 48)
    return a, b, p


def extremos_vistos(lineas: list[str]) -> int:
    """Cuántas de las 25 combinaciones de casos extremos llegaron."""
    pares = {operandos_dsp(t)[:2] for t in lineas if len(t) == 24}
    return sum((a, b) in pares for a in EXTREMOS_A for b in EXTREMOS_B)


def comprobar_dsp(hexa: str) -> str | None:
    if len(hexa) != 24:
        return f"longitud {len(hexa)}"
    a, b, p = operandos_dsp(hexa)
    if not (-(1 << 26) <= a < (1 << 26) and -(1 << 17) <= b < (1 << 17)):
        return f"operando fuera de rango: a={a} b={b}"
    return None if p == a * b else f"a={a} b={b}: p={p}, esperado {a * b}"


def comprobar_bsram(hexa: str) -> str | None:
    if len(hexa) != 20:
        return f"longitud {len(hexa)}"
    err_a, err_b, nuevos_b, err_c, _vuelta = (int(hexa[i : i + 4], 16) for i in range(0, 20, 4))
    if err_a or err_b or err_c:
        return f"errA={err_a} errB={err_b} (nuevos {nuevos_b}) errC={err_c}"
    return None


def comprobar_pll(hexa: str) -> str | None:
    if len(hexa) != 9:
        return f"longitud {len(hexa)}"
    bloqueado, ciclos = int(hexa[0], 16), int(hexa[1:], 16)
    if bloqueado != 1:
        return "el PLL no está bloqueado"
    if abs(ciclos - PLL_ESPERADO) > PLL_TOLERANCIA:
        return f"{ciclos} ciclos por segundo, esperado {PLL_ESPERADO} ± {PLL_TOLERANCIA}"
    return None


def comprobar_fs(hexa: str) -> str | None:
    if len(hexa) != 8:
        return f"longitud {len(hexa)}"
    muestras = int(hexa, 16)
    return None if muestras in (48_828, 48_829) else f"{muestras} muestras por segundo"


ECO = b"SOFIFI\x00\xff\x55"


def verificar_fs(puerto: str, segundos: float) -> int:
    """Envía ECO, exige su eco en orden y comprueba las medidas de fs."""
    lineas: list[str] = []
    with serial.Serial(puerto, 115_200, timeout=0.2) as s:
        s.reset_input_buffer()
        # De uno en uno: prueba_fs guarda un solo eco pendiente, y cada línea de
        # eco tarda ~1 ms mientras los bytes llegan cada 87 µs.
        for byte in ECO:
            s.write(bytes([byte]))
            time.sleep(0.01)
        fin = time.monotonic() + segundos
        while time.monotonic() < fin:
            crudo = s.readline()
            if crudo:
                lineas.append(crudo.decode("ascii", "replace").strip())
    ecos = bytes(int(t[2:], 16) for t in lineas if t.startswith("R ") and len(t) == 10)
    medidas = [t[2:] for t in lineas if t.startswith("S ")]
    errores = [(t, e) for t in medidas[1:] if (e := comprobar_fs(t)) is not None]
    for t, e in errores:
        print(f"ERROR S {t}: {e}")
    print(f"fs: eco {'correcto' if ecos == ECO else f'INCORRECTO: {ecos!r}'}")
    print(f"fs: {len(medidas) - 1} medidas comprobadas, {len(errores)} con error")
    print("fs: muestras por segundo: " + ", ".join(str(int(t, 16)) for t in medidas[1:]))
    return 0 if ecos == ECO and len(medidas) > 1 and not errores else 1


COMPROBADORES = {
    "dsp": ("D", comprobar_dsp),
    "bsram": ("B", comprobar_bsram),
    "pll": ("P", comprobar_pll),
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "prueba",
        choices=[*sorted(COMPROBADORES), "fs"],
        help="top cargado: prueba_bsram, prueba_dsp, prueba_pll o prueba_fs",
    )
    ap.add_argument(
        "--puerto", default="/dev/ttyUSB1", help="UART de la FPGA (por defecto: %(default)s)"
    )
    ap.add_argument(
        "--segundos", type=float, default=10.0, help="tiempo de lectura (por defecto: 10)"
    )
    args = ap.parse_args(argv)

    if args.prueba == "fs":
        return verificar_fs(args.puerto, args.segundos)
    etiqueta, comprobar = COMPROBADORES[args.prueba]
    lineas = [txt for _, txt in leer(args.puerto, 115_200, args.segundos)]
    validas = [t[2:] for t in lineas if t.startswith(etiqueta + " ")]
    # La primera línea puede llegar cortada si la lectura empieza a mitad.
    errores = [(t, e) for t in validas[1:] if (e := comprobar(t)) is not None]
    for t, e in errores[:10]:
        print(f"ERROR {etiqueta} {t}: {e}")
    print(f"{args.prueba}: {len(validas) - 1} líneas comprobadas, {len(errores)} con error")
    if args.prueba == "dsp":
        vistos = extremos_vistos(validas[1:])
        print(f"dsp: {vistos} de 25 combinaciones de casos extremos")
        if vistos < 25:
            return 1
    return 0 if len(validas) > 1 and not errores else 1


if __name__ == "__main__":
    sys.exit(main())
