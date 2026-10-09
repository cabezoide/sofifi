# SPDX-License-Identifier: MIT
"""Entrada de línea de mandos; raíz de composición: único sitio que elige adaptadores.

sofifi asm       PROGRAMA.sasm  SALIDA_BASE
sofifi catalogo  (regenera docs/programas.md)
sofifi render  PROGRAMA.sasm  ENTRADA.wav  SALIDA.wav
               [--preset NOMBRE] [--pot N=V] [--freeze A:B] [--cola S]
sofifi presets [PROGRAMA]
sofifi cadenas                     (lista presets/cadenas.toml: coste y si cabe)
sofifi componer NOMBRE SALIDA.sasm (la cadena como un programa, ADR 0013)
sofifi cadena  NOMBRE  ENTRADA.wav  SALIDA.wav  [--pot N=V] [--freeze A:B] [--cola S]
sofifi rom     NOMBRE  SALIDA.v   (programa o cadena como ROM programa_hil, para `make hil`)
sofifi banco   SALIDA.img [NOMBRE...]   (banco de la microSD; sin nombres, todo lo que cabe)
sofifi banco   --leer IMAGEN.img        (comprueba un banco y lista sus programas)
"""

from __future__ import annotations

import argparse
import sys
from fractions import Fraction
from pathlib import Path

from sofifi.adapters.archivos import FuenteProgramaArchivo, SumideroHex, ensamblar_archivo
from sofifi.adapters.cadenas import (
    FuenteCadena,
    leer_cadenas,
    programa_o_cadena,
    textos_de_programas,
)
from sofifi.adapters.microsd import escribir_imagen, listar_imagen
from sofifi.adapters.presets import leer_banco
from sofifi.adapters.wav import FuenteWav, SumideroWav
from sofifi.cli_argumentos import analizador
from sofifi.domain.aritmetica import CICLOS_POR_MUESTRA, FS_WAV, dato
from sofifi.domain.cadena import Cadena
from sofifi.domain.composicion import componer, recursos
from sofifi.domain.coste import ciclos_rtl
from sofifi.domain.ensamblador import ErrorEnsamblado
from sofifi.domain.isa import NUM_POTS
from sofifi.domain.senal import Controles
from sofifi.services.catalogo import catalogos, ficha, ficha_cadena
from sofifi.services.render import exportar_microcodigo, renderizar
from sofifi.services.tablas import (
    PROGRAMAS_EN_ROM,
    RUTA_TABLA_HERMITE,
    ruta_programa,
    verilog_programa,
    verilog_tabla_hermite,
)


def buscar_raiz(desde: Path) -> Path:
    """La raíz del repositorio: la primera carpeta, desde ``desde`` hacia arriba,
    con ``programas/`` y ``presets/banco.toml``. Si ninguna la tiene, la del paquete.

    Se busca desde el directorio actual para que, en un worktree, la CLI use los
    ficheros de ese worktree y no los del repositorio donde se instaló.
    """
    for carpeta in (desde, *desde.parents):
        if (carpeta / "programas").is_dir() and (carpeta / "presets" / "banco.toml").is_file():
            return carpeta
    return Path(__file__).resolve().parents[2]


RAIZ = buscar_raiz(Path.cwd())
RUTA_BANCO = RAIZ / "presets" / "banco.toml"
PALABRAS_HIL = 38_912  # memoria de retardo de hil_nucleo: 38 bloques, el resto es captura
RUTA_CADENAS = RAIZ / "presets" / "cadenas.toml"
PROGRAMAS = RAIZ / "programas"


def _cadena(nombre: str) -> Cadena:
    for c in leer_cadenas(RUTA_CADENAS):
        if c.nombre == nombre:
            return c
    raise argparse.ArgumentTypeError(
        f"«{nombre}» no está en presets/cadenas.toml (ver: sofifi cadenas)"
    )


def _incluir(nombre: str) -> str:
    return (PROGRAMAS / nombre).read_text(encoding="utf-8")


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
    args = analizador().parse_args(argv)
    try:
        if args.orden == "banco":
            if args.leer:
                lineas = listar_imagen(args.imagen)
            else:
                lineas = escribir_imagen(args.imagen, args.nombres, PROGRAMAS, RUTA_CADENAS)
            print("\n".join(lineas))
            return 0
        if args.orden == "rom":
            try:
                prog = programa_o_cadena(args.nombre, PROGRAMAS, RUTA_CADENAS)
            except ValueError as exc:
                raise argparse.ArgumentTypeError(str(exc)) from exc
            if prog.palabras_memoria > PALABRAS_HIL:
                raise argparse.ArgumentTypeError(
                    f"{args.nombre}: {prog.palabras_memoria} palabras; "
                    f"hil_nucleo tiene {PALABRAS_HIL}"
                )
            origen = f"«{args.nombre}» ({prog.nombre})"
            args.salida.write_text(verilog_programa(prog, "programa_hil", origen), encoding="utf-8")
            print(
                f"{args.nombre}: {len(prog.instrucciones)} instrucciones, "
                f"{ciclos_rtl(prog)} ciclos del RTL, {prog.palabras_memoria} palabras"
                f" → {args.salida}"
            )
            return 0
        if args.orden == "presets":
            banco = leer_banco(RUTA_BANCO)
            for programa in [args.programa] if args.programa else sorted(banco):
                for nombre, valores in banco.get(programa, {}).items():
                    print(f"{programa}/{nombre}: " + " ".join(f"{float(v):.2f}" for v in valores))
        elif args.orden == "cadenas":
            textos = textos_de_programas(PROGRAMAS)
            for c in leer_cadenas(RUTA_CADENAS):
                gasto = recursos(c, textos, _incluir)
                falta = gasto.excedidos()
                estado = "cabe" if not falta else "no cabe: " + ", ".join(falta)
                programas = (" → " if c.modo.value == "serie" else " ‖ ").join(
                    e.programa for e in c.eslabones
                )
                print(
                    f"{c.nombre}: {programas}; {gasto.ciclos} ciclos, {gasto.memoria} palabras,"
                    f" {gasto.registros} registros, {gasto.lfos} LFOs; {estado}"
                )
        elif args.orden == "componer":
            texto = componer(_cadena(args.nombre), textos_de_programas(PROGRAMAS), _incluir)
            args.salida.write_text(texto, encoding="utf-8")
            print(f"{args.nombre} → {args.salida}")
        elif args.orden == "cadena":
            c = _cadena(args.nombre)
            pots_cadena = [f"pot{k}={v}" for k, v in enumerate(c.posiciones)]
            informe = renderizar(
                FuenteCadena(c, PROGRAMAS),
                FuenteWav(args.entrada),
                SumideroWav(args.salida),
                Controles(_pots(pots_cadena + args.pot), _tramos(args.freeze)),
                round(args.cola * FS_WAV),
            )
            print(f"{informe.programa}: {informe.muestras} muestras → {args.salida}")
        elif args.orden == "catalogo":
            fichas = [
                ficha(r.stem, r.read_text(encoding="utf-8"), ensamblar_archivo(r))
                for r in sorted(PROGRAMAS.glob("*.sasm"))
            ]
            presets = {p: len(v) for p, v in leer_banco(RUTA_BANCO).items()}
            textos = textos_de_programas(PROGRAMAS)
            cadenas = [
                ficha_cadena(c, recursos(c, textos, _incluir)) for c in leer_cadenas(RUTA_CADENAS)
            ]
            for ruta, texto in catalogos(fichas, presets, cadenas).items():
                (RAIZ / ruta).write_text(texto, encoding="utf-8")
                print(f"{len(fichas)} programas → {ruta}")
        elif args.orden == "tablas":
            (RAIZ / RUTA_TABLA_HERMITE).write_text(verilog_tabla_hermite(), encoding="utf-8")
            print(f"tabla Hermite → {RUTA_TABLA_HERMITE}")
            for nombre in PROGRAMAS_EN_ROM:
                programa = ensamblar_archivo(PROGRAMAS / f"{nombre}.sasm")
                destino = RAIZ / ruta_programa(nombre)
                destino.write_text(verilog_programa(programa), encoding="utf-8")
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
                        f"--preset {args.preset}: no está en [{args.programa.stem}]"
                        " de presets/banco.toml"
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
