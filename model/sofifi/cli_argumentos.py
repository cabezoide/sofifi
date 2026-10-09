# SPDX-License-Identifier: MIT
"""Argumentos y textos de ayuda de la CLI ``sofifi`` (``sofifi.cli`` los usa).

Solo describe las órdenes: no elige adaptadores ni hace E/S. La guía de todas
las órdenes está en ``docs/scripts.md``.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def analizador() -> argparse.ArgumentParser:
    """El analizador de ``sofifi`` con sus diez órdenes."""
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
    return p
