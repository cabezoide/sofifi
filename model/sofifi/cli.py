# SPDX-License-Identifier: MIT
"""Entrada de línea de mandos; raíz de composición: único sitio que elige adaptadores.

sofifi asm       PROGRAMA.sasm  SALIDA_BASE
sofifi catalogo  (regenera docs/programas.md)
sofifi render  PROGRAMA.sasm  ENTRADA.wav  SALIDA.wav
               [--preset NOMBRE] [--pot N=V] [--freeze A:B] [--cola S]
sofifi presets [PROGRAMA]
"""

from __future__ import annotations

import argparse
import sys
from fractions import Fraction
from pathlib import Path

from sofifi.adapters.archivos import FuenteProgramaArchivo, SumideroHex, ensamblar_archivo
from sofifi.adapters.presets import leer_banco
from sofifi.adapters.wav import FuenteWav, SumideroWav
from sofifi.domain.aritmetica import CICLOS_POR_MUESTRA, FS_WAV, dato
from sofifi.domain.coste import ciclos_rtl
from sofifi.domain.ensamblador import ErrorEnsamblado
from sofifi.domain.isa import NUM_POTS
from sofifi.domain.senal import Controles
from sofifi.services.catalogo import RUTA_CATALOGO, ficha, markdown
from sofifi.services.render import exportar_microcodigo, renderizar
from sofifi.services.tablas import (
    PROGRAMAS_EN_ROM,
    RUTA_TABLA_HERMITE,
    ruta_programa,
    verilog_programa,
    verilog_tabla_hermite,
)

RUTA_BANCO = Path("presets/banco.toml")


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
    sub.add_parser("tablas", help="regenera las tablas y programas en ROM del RTL")
    sub.add_parser("catalogo", help="regenera docs/programas.md desde programas/*.sasm")
    r = sub.add_parser("render", help="procesa un WAV con un programa")
    r.add_argument("programa", type=Path)
    r.add_argument("entrada", type=Path)
    r.add_argument("salida", type=Path)
    r.add_argument("--pot", action="append", default=[], metavar="potN=V")
    r.add_argument("--freeze", action="append", default=[], metavar="INICIO:FIN", help="segundos")
    r.add_argument("--cola", type=float, default=0.0, help="segundos de silencio al final")
    r.add_argument(
        "--preset", metavar="NOMBRE", help="mandos de presets/banco.toml (antes de --pot)"
    )
    pr = sub.add_parser("presets", help="lista los presets de presets/banco.toml")
    pr.add_argument("programa", nargs="?", help="solo los de este programa")
    args = p.parse_args(argv)
    try:
        if args.orden == "presets":
            banco = leer_banco(RUTA_BANCO)
            for programa in [args.programa] if args.programa else sorted(banco):
                for nombre, valores in banco.get(programa, {}).items():
                    print(f"{programa}/{nombre}: " + " ".join(f"{float(v):.2f}" for v in valores))
        elif args.orden == "catalogo":
            fichas = [
                ficha(r.stem, r.read_text(encoding="utf-8"), ensamblar_archivo(r))
                for r in sorted(Path("programas").glob("*.sasm"))
            ]
            presets = {p: len(v) for p, v in leer_banco(RUTA_BANCO).items()}
            Path(RUTA_CATALOGO).write_text(markdown(fichas, presets), encoding="utf-8")
            print(f"{len(fichas)} programas → {RUTA_CATALOGO}")
        elif args.orden == "tablas":
            Path(RUTA_TABLA_HERMITE).write_text(verilog_tabla_hermite(), encoding="utf-8")
            print(f"tabla Hermite → {RUTA_TABLA_HERMITE}")
            for nombre in PROGRAMAS_EN_ROM:
                programa = ensamblar_archivo(Path("programas") / f"{nombre}.sasm")
                Path(ruta_programa(nombre)).write_text(verilog_programa(programa), encoding="utf-8")
                print(f"{nombre} → {ruta_programa(nombre)}")
        elif args.orden == "asm":
            prog = exportar_microcodigo(
                FuenteProgramaArchivo(args.programa), SumideroHex(args.salida)
            )
            print(
                f"{prog.nombre}: {len(prog.instrucciones)} instrucciones, "
                f"{ciclos_rtl(prog)} de {CICLOS_POR_MUESTRA} ciclos del RTL, "
                f"{prog.palabras_memoria} palabras de memoria"
            )
        else:
            pots_preset: list[str] = []
            if args.preset:
                del_programa = leer_banco(RUTA_BANCO).get(args.programa.stem, {})
                if args.preset not in del_programa:
                    raise argparse.ArgumentTypeError(
                        f"--preset {args.preset}: no está en [{args.programa.stem}] de {RUTA_BANCO}"
                    )
                pots_preset = [f"pot{k}={v}" for k, v in enumerate(del_programa[args.preset])]
            controles = Controles(_pots(pots_preset + args.pot), _tramos(args.freeze))
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
