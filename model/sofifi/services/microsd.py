# SPDX-License-Identifier: MIT
"""`sofifi banco`: escribe y comprueba la imagen de la microSD (Fase 08).

Une el formato (``domain/banco.py``) con los programas y las cadenas del
repositorio. Los errores salen como ``argparse.ArgumentTypeError``, como en el
resto de órdenes de la CLI.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from sofifi.adapters.cadenas import leer_cadenas, programa_o_cadena
from sofifi.domain import banco
from sofifi.domain.ensamblador import ErrorEnsamblado


def listar_imagen(imagen: Path) -> list[str]:
    """Una línea por ranura. Falla si alguna ranura no es válida."""
    datos = imagen.read_bytes()
    lineas = []
    try:
        for k in range(banco.leer_cabecera(datos[: banco.BLOQUE])):
            prog = banco.leer_programa(datos, k)
            lineas.append(f"{k:4d} {prog.nombre}: {len(prog.instrucciones)} instrucciones")
    except banco.ErrorBanco as exc:
        raise argparse.ArgumentTypeError(f"{imagen}: {exc}") from exc
    return lineas


def escribir_imagen(imagen: Path, nombres: list[str], programas: Path, cadenas: Path) -> list[str]:
    """Escribe el banco. Sin nombres, todo lo que cabe; lo demás se omite con aviso."""
    todos = not nombres
    if todos:
        nombres = [r.stem for r in sorted(programas.glob("*.sasm"))]
        nombres += [c.nombre for c in leer_cadenas(cadenas) if c.requiere is None]
    elegidos, lineas = [], []
    for nombre in nombres:
        try:
            prog = programa_o_cadena(nombre, programas, cadenas)
            banco.escribir_banco([prog])  # comprueba el nombre y los ciclos del RTL
        except (ValueError, ErrorEnsamblado) as exc:
            if not todos:
                raise argparse.ArgumentTypeError(f"{nombre}: {exc}") from exc
            lineas.append(f"se omite {nombre}: {exc}")
            continue
        elegidos.append(prog)
    imagen.write_bytes(banco.escribir_banco(elegidos))
    kib = imagen.stat().st_size // 1024
    lineas.append(f"{len(elegidos)} programas → {imagen} ({kib} KiB)")
    return lineas
