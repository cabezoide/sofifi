# SPDX-License-Identifier: MIT
"""Entrada de línea de mandos; raíz de composición: único sitio que elige adaptadores.

sofifi asm     PROGRAMA.sasm  SALIDA_BASE
sofifi render  PROGRAMA.sasm  ENTRADA.wav  SALIDA.wav  [--pot N=V] [--freeze A:B] [--cola S]
"""

from __future__ import annotations

import argparse
import sys
from fractions import Fraction
from pathlib import Path

from sofifi.adapters.archivos import FuenteProgramaArchivo, SumideroHex
from sofifi.adapters.wav import FuenteWav, SumideroWav
from sofifi.domain.aritmetica import FS_WAV, dato
from sofifi.domain.ensamblador import ErrorEnsamblado
from sofifi.domain.isa import NUM_POTS
from sofifi.domain.senal import Controles
from sofifi.services.render import exportar_microcodigo, renderizar


def _pots(valores: list[str]) -> tuple[int, ...]:
    pots = [0] * NUM_POTS
    for v in valores:
        nombre, _, numero = v.partition("=")
        indice = int(nombre.removeprefix("pot"))
        valor = Fraction(numero)
        if not (0 <= indice < NUM_POTS and 0 <= valor <= 1):
            raise argparse.ArgumentTypeError(
                f"--pot {v}: se espera potN=V con N<{NUM_POTS} y V en [0,1]"
            )
        pots[indice] = dato(valor)
    return tuple(pots)


def _tramos(valores: list[str]) -> tuple[tuple[int, int], ...]:
    tramos = []
    for v in valores:
        a, _, b = v.partition(":")
        tramos.append((round(float(a) * FS_WAV), round(float(b) * FS_WAV)))
    return tuple(tramos)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="sofifi", description="Modelo bit-exact del núcleo SOFIFI")
    sub = p.add_subparsers(dest="orden", required=True)
    a = sub.add_parser("asm", help="ensambla a microcódigo (.hex + .json)")
    a.add_argument("programa", type=Path)
    a.add_argument("salida", type=Path)
    r = sub.add_parser("render", help="procesa un WAV con un programa")
    r.add_argument("programa", type=Path)
    r.add_argument("entrada", type=Path)
    r.add_argument("salida", type=Path)
    r.add_argument("--pot", action="append", default=[], metavar="potN=V")
    r.add_argument("--freeze", action="append", default=[], metavar="INICIO:FIN", help="segundos")
    r.add_argument("--cola", type=float, default=0.0, help="segundos de silencio al final")
    args = p.parse_args(argv)
    try:
        if args.orden == "asm":
            prog = exportar_microcodigo(
                FuenteProgramaArchivo(args.programa), SumideroHex(args.salida)
            )
            print(
                f"{prog.nombre}: {len(prog.instrucciones)} instrucciones, {prog.ciclos} ciclos, "
                f"{prog.palabras_memoria} palabras de memoria"
            )
        else:
            controles = Controles(_pots(args.pot), _tramos(args.freeze))
            informe = renderizar(
                FuenteProgramaArchivo(args.programa),
                FuenteWav(args.entrada),
                SumideroWav(args.salida),
                controles,
                round(args.cola * FS_WAV),
            )
            print(f"{informe.programa}: {informe.muestras} muestras → {args.salida}")
    except (ErrorEnsamblado, argparse.ArgumentTypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
