# SPDX-License-Identifier: MIT
"""Las compuertas ``check_*`` no tienen opciones: esto lo hace cumplir.

Sin argumentos, la compuerta corre. Con ``-h`` o ``--help`` imprime su
docstring y sale con 0. Con otro argumento imprime el docstring en la salida de
error y sale con 2, sin correr. Así ``check_optimizacion.py --help`` ya no
sintetiza todos los tops.
"""

from __future__ import annotations

import sys


def exigir_sin_opciones(ayuda: str | None) -> None:
    """Termina el proceso si hay argumentos; vuelve si no hay ninguno."""
    argumentos = sys.argv[1:]
    if not argumentos:
        return
    pide_ayuda = argumentos in (["-h"], ["--help"])
    print(ayuda or "", file=sys.stdout if pide_ayuda else sys.stderr)
    if not pide_ayuda:
        print(f"opción desconocida: {' '.join(argumentos)}; no tiene opciones", file=sys.stderr)
    sys.exit(0 if pide_ayuda else 2)
