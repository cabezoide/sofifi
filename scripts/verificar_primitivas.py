# SPDX-License-Identifier: MIT
"""Comprueba en el PC lo que envían los tops de prueba de primitivas (Fase 03).

Uso::

    make prog TOP=prueba_dsp && .venv/bin/python scripts/verificar_primitivas.py dsp
    .venv/bin/python scripts/verificar_primitivas.py bsram --segundos 10
    .venv/bin/python scripts/verificar_primitivas.py pll

Cada top envía líneas "<etiqueta> <hexadecimal>":

- ``D``: a (7 dígitos), b (5) y p (12), con signo. Se exige p = a·b y que
  lleguen las 25 combinaciones de casos extremos.
- ``B``: errA, errB, nuevosB, errC y vuelta (4 dígitos cada uno). Se exigen
  errores a 0.
- ``P``: bloqueado (1 dígito) y ciclos del PLL en un segundo del cristal (8).
  Se exige bloqueado = 1 y 100 000 000 ± 100 ciclos.

Termina con código 0 si todas las líneas son correctas y llegó al menos una.
"""

from __future__ import annotations

import argparse
import sys

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


COMPROBADORES = {
    "dsp": ("D", comprobar_dsp),
    "bsram": ("B", comprobar_bsram),
    "pll": ("P", comprobar_pll),
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("prueba", choices=sorted(COMPROBADORES))
    ap.add_argument("--puerto", default="/dev/ttyUSB1")
    ap.add_argument("--segundos", type=float, default=10.0)
    args = ap.parse_args(argv)

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
