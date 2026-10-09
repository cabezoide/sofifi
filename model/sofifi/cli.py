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

RUTA_BANCO = Path("presets/banco.toml")
PALABRAS_HIL = 38_912  # memoria de retardo de hil_nucleo: 38 bloques, el resto es captura
RUTA_CADENAS = Path("presets/cadenas.toml")
PROGRAMAS = Path("programas")


def _cadena(nombre: str) -> Cadena:
    for c in leer_cadenas(RUTA_CADENAS):
        if c.nombre == nombre:
            return c
    raise argparse.ArgumentTypeError(f"«{nombre}» no está en {RUTA_CADENAS} (ver: sofifi cadenas)")


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
    p = argparse.ArgumentParser(
        prog="sofifi",
        description="Modelo bit-exact del núcleo SOFIFI. Se ejecuta desde la raíz del repositorio.",
        epilog="Guía de todas las órdenes: docs/scripts.md. Código de salida: 0 bien, 1 error.",
    )
    sub = p.add_subparsers(dest="orden", required=True)
    crudo = argparse.RawDescriptionHelpFormatter
    a = sub.add_parser(
        "asm",
        help="ensambla a microcódigo (.hex + .json) y da los ciclos del RTL",
        description="Ensambla un programa .sasm. Escribe SALIDA.hex y SALIDA.json.\n"
        "Ejemplo: sofifi asm programas/plate.sasm build/plate",
        formatter_class=crudo,
    )
    a.add_argument("programa", type=Path, help="programa .sasm")
    a.add_argument("salida", type=Path, help="ruta base de la salida, sin extensión")
    sub.add_parser(
        "tablas",
        help="regenera las tablas y programas en ROM del RTL",
        description="Escribe la tabla Hermite y los programas en ROM de rtl/.\n"
        "Se ejecuta después de cambiar la aritmética o un programa en ROM.",
        formatter_class=crudo,
    )
    sub.add_parser(
        "catalogo",
        help="regenera docs/programas.md desde programas/*.sasm",
        description="Escribe docs/programas.md y sus tres traducciones desde programas/*.sasm,\n"
        "presets/banco.toml y presets/cadenas.toml.",
        formatter_class=crudo,
    )
    r = sub.add_parser(
        "render",
        help="procesa un WAV con un programa",
        description="Procesa un WAV con un programa .sasm y escribe el WAV de salida.\n"
        "Ejemplo: sofifi render programas/plate.sasm seca.wav plate.wav --preset 'Placa corta'",
        formatter_class=crudo,
    )
    r.add_argument("programa", type=Path, help="programa .sasm")
    r.add_argument("entrada", type=Path, help="WAV de entrada")
    r.add_argument("salida", type=Path, help="WAV de salida")
    r.add_argument(
        "--pot", action="append", default=[], metavar="potN=V", help="mando N en [0, 1]; repetible"
    )
    r.add_argument(
        "--freeze", action="append", default=[], metavar="INICIO:FIN", help="pulsador, en segundos"
    )
    r.add_argument("--cola", type=float, default=0.0, help="segundos de silencio al final")
    r.add_argument(
        "--preset", metavar="NOMBRE", help="mandos de presets/banco.toml (antes de --pot)"
    )
    pr = sub.add_parser(
        "presets",
        help="lista los presets de presets/banco.toml",
        description="Lista los presets: programa/nombre y el valor de cada mando.",
    )
    pr.add_argument("programa", nargs="?", help="solo los de este programa")
    sub.add_parser(
        "cadenas",
        help="lista las cadenas de presets/cadenas.toml y si caben",
        description="Lista cada cadena con sus ciclos, palabras de memoria, registros y LFOs,\n"
        "y dice si cabe en el núcleo (ADR 0013).",
        formatter_class=crudo,
    )
    co = sub.add_parser(
        "componer",
        help="escribe una cadena como un solo programa .sasm",
        description="Escribe una cadena de presets/cadenas.toml como un programa .sasm.\n"
        'Ejemplo: sofifi componer "Eco y muelle" build/eco_y_muelle.sasm',
        formatter_class=crudo,
    )
    co.add_argument("nombre", help="nombre de la cadena (ver: sofifi cadenas)")
    co.add_argument("salida", type=Path, help="programa .sasm de salida")
    ca = sub.add_parser(
        "cadena",
        help="procesa un WAV con una cadena",
        description="Procesa un WAV con una cadena. Los mandos parten de sus posiciones.\n"
        'Ejemplo: sofifi cadena "Eco y muelle" seca.wav eco.wav',
        formatter_class=crudo,
    )
    ca.add_argument("nombre", help="nombre de la cadena (ver: sofifi cadenas)")
    ca.add_argument("entrada", type=Path, help="WAV de entrada")
    ca.add_argument("salida", type=Path, help="WAV de salida")
    ca.add_argument(
        "--pot", action="append", default=[], metavar="potN=V", help="mando N en [0, 1]; repetible"
    )
    ca.add_argument(
        "--freeze", action="append", default=[], metavar="INICIO:FIN", help="pulsador, en segundos"
    )
    ca.add_argument("--cola", type=float, default=0.0, help="segundos de silencio al final")
    ro = sub.add_parser(
        "rom",
        help="ROM programa_hil de un programa o una cadena (make hil)",
        description="Escribe el módulo Verilog programa_hil para el top hil_programa.\n"
        "Lo usa make hil. Ejemplo: sofifi rom marea build/programa_hil.v",
        formatter_class=crudo,
    )
    ro.add_argument("nombre", help="programa (programas/NOMBRE.sasm) o cadena")
    ro.add_argument("salida", type=Path, help="fichero .v de salida")
    ba = sub.add_parser(
        "banco",
        help="banco de programas para la microSD (Fase 08)",
        description="Escribe o comprueba la imagen de la microSD (docs/microsd.md).\n"
        "Ejemplos:\n"
        "  sofifi banco build/banco.img              todo lo que cabe\n"
        "  sofifi banco build/banco.img plate hall   solo esos\n"
        "  sofifi banco --leer build/banco.img       comprueba CRC y límites",
        formatter_class=crudo,
    )
    ba.add_argument("imagen", type=Path, help="imagen .img que se escribe o se lee")
    ba.add_argument("nombres", nargs="*", help="programas o cadenas; sin nombres, todo lo que cabe")
    ba.add_argument("--leer", action="store_true", help="comprueba la imagen y lista su contenido")
    args = p.parse_args(argv)
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
                for r in sorted(Path("programas").glob("*.sasm"))
            ]
            presets = {p: len(v) for p, v in leer_banco(RUTA_BANCO).items()}
            textos = textos_de_programas(PROGRAMAS)
            cadenas = [
                ficha_cadena(c, recursos(c, textos, _incluir)) for c in leer_cadenas(RUTA_CADENAS)
            ]
            for ruta, texto in catalogos(fichas, presets, cadenas).items():
                Path(ruta).write_text(texto, encoding="utf-8")
                print(f"{len(fichas)} programas → {ruta}")
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
