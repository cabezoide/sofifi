# SPDX-License-Identifier: MIT
"""Compuerta ``ratchets`` (SPEC_RAIZ §9.1, P4): las magnitudes no empeoran en silencio.

Cada entrada de ``docs/ratchets.yaml`` nombra una ``medida`` de este módulo, un
``liston`` y una ``direccion``. Si la medida queda peor que el listón, rojo. Si
mejora por encima de ``aviso_holgura``, aviso: hay que mover el listón para no
regalar lo ganado a la siguiente entrega.

Siempre imprime la foto de todas las medidas disponibles (P9: primero la
medición, después el objetivo), aunque no tengan listón.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _versionados(*patrones: str) -> list[Path]:
    salida = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", *patrones],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split()
    return [ROOT / s for s in salida if (ROOT / s).is_file()]


def _max_lineas(*patrones: str) -> float:
    ficheros = _versionados(*patrones)
    if not ficheros:
        return 0.0
    return float(max(len(f.read_text(encoding="utf-8").splitlines()) for f in ficheros))


def cobertura_modelo() -> float:
    informe = ROOT / ".coverage.json"
    if not informe.is_file():
        raise RuntimeError("falta .coverage.json: corre antes el trabajo 'model'")
    datos = json.loads(informe.read_text(encoding="utf-8"))
    return float(datos["totals"]["percent_covered"])


def lineas_max_modelo() -> float:
    return _max_lineas("model/ambient/*.py")


def lineas_max_rtl() -> float:
    return _max_lineas("rtl/*.v", "rtl/*.sv")


MEDIDAS: dict[str, Callable[[], float]] = {
    "cobertura_modelo": cobertura_modelo,
    "lineas_max_modelo": lineas_max_modelo,
    "lineas_max_rtl": lineas_max_rtl,
}


def main() -> int:
    datos = yaml.safe_load((ROOT / "docs" / "ratchets.yaml").read_text(encoding="utf-8")) or {}
    entradas = datos.get("ratchets") or []
    errores: list[str] = []

    print("Foto de medidas:")
    valores: dict[str, float] = {}
    for nombre, fn in MEDIDAS.items():
        try:
            valores[nombre] = fn()
            print(f"  {nombre:<22} {valores[nombre]:.2f}")
        except RuntimeError as exc:
            print(f"  {nombre:<22} sin dato ({exc})")

    for e in entradas:
        medida = e["medida"]
        if medida not in MEDIDAS:
            errores.append(f"{e['id']}: medida desconocida '{medida}'")
            continue
        if medida not in valores:
            errores.append(f"{e['id']}: no se pudo medir '{medida}'")
            continue
        v, liston = valores[medida], float(e["liston"])
        peor = v > liston if e["direccion"] == "menor_mejor" else v < liston
        if peor:
            errores.append(
                f"{e['id']} {e['nombre']}: {v:.2f} empeora el listón {liston:.2f}."
                " Salidas: arreglarlo, o mover el listón ampliando su 'motivo'."
            )
        holgura = e.get("aviso_holgura")
        if holgura is not None and abs(v - liston) > float(holgura) and not peor:
            print(f"AVISO {e['id']}: mejora de {abs(v - liston):.2f}; mueve el listón a {v:.2f}.")

    if errores:
        print("\n".join(errores))
        return 1
    print(f"ratchets: {len(entradas)} listones respetados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
