# SPDX-License-Identifier: MIT
"""Compuerta ``ratchets`` (SPEC_RAIZ §9.1, P4): las magnitudes no empeoran en silencio.

Cuándo: trabajo duro de ``scripts/ci_local.sh``. Corre después de ``model``,
porque lee ``.coverage.json``. ``make optimizacion`` lo corre tras la síntesis.

Cada entrada de ``docs/ratchets.yaml`` nombra una ``medida`` de este módulo, un
``liston`` y una ``direccion``. Si la medida queda peor que el listón, rojo. Si
mejora por encima de ``aviso_holgura``, aviso: hay que mover el listón para no
regalar lo ganado a la siguiente entrega.

Siempre imprime la foto de todas las medidas disponibles (P9: primero la
medición, después el objetivo), aunque no tengan listón.

Además de las de ``MEDIDAS``, hay una medida por top y celda,
``recursos:<top>:<celda>`` (por ejemplo ``recursos:hola_uart:LUT4``), que lee
``build/<top>_recursos.json``: lo deja el trabajo ``optimizacion`` (ADR 0010).
Sin ese fichero, el listón sale como ``NO CORRIÓ`` y no bloquea.

Uso::

    .venv/bin/python scripts/check_ratchets.py

No tiene opciones y no escribe nada. Salida: 0 bien; 1 un listón empeora o una
medida no se puede medir.
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
    return _max_lineas("model/sofifi/*.py")


def lineas_max_rtl() -> float:
    return _max_lineas("rtl/*.v", "rtl/*.sv")


MEDIDAS: dict[str, Callable[[], float]] = {
    "cobertura_modelo": cobertura_modelo,
    "lineas_max_modelo": lineas_max_modelo,
    "lineas_max_rtl": lineas_max_rtl,
}

CELDAS_FOTO = ("LUT4", "ALU", "DFF", "BSRAM", "MULTALU27X18")


def _recursos(top: str, celda: str) -> Callable[[], float]:
    def medir() -> float:
        informe = ROOT / "build" / f"{top}_recursos.json"
        if not informe.is_file():
            raise RuntimeError(f"falta {informe.name}: corre antes el trabajo 'optimizacion'")
        recursos = json.loads(informe.read_text(encoding="utf-8"))["recursos"]
        return float(recursos.get(celda, {}).get("usado", 0))

    return medir


def medidas(entradas: list[dict[str, str]]) -> dict[str, Callable[[], float]]:
    """``MEDIDAS`` más las de recursos: las de los listones y la foto de cada top."""
    todas = dict(MEDIDAS)
    tops = ROOT / "rtl" / "top" / "tops.txt"
    nombres = [n.split("#", 1)[0].split()[:1] for n in tops.read_text("utf-8").splitlines()]
    for top in (n[0] for n in nombres if n):
        for celda in CELDAS_FOTO:
            todas[f"recursos:{top}:{celda}"] = _recursos(top, celda)
    for e in entradas:
        partes = str(e["medida"]).split(":")
        if len(partes) == 3 and partes[0] == "recursos":
            todas[e["medida"]] = _recursos(partes[1], partes[2])
    return todas


def main() -> int:
    datos = yaml.safe_load((ROOT / "docs" / "ratchets.yaml").read_text(encoding="utf-8")) or {}
    entradas = datos.get("ratchets") or []
    errores: list[str] = []

    print("Foto de medidas:")
    valores: dict[str, float] = {}
    disponibles = medidas(entradas)
    for nombre, fn in disponibles.items():
        try:
            valores[nombre] = fn()
            print(f"  {nombre:<26} {valores[nombre]:.2f}")
        except RuntimeError as exc:
            print(f"  {nombre:<26} sin dato ({exc})")

    for e in entradas:
        medida = e["medida"]
        if medida not in disponibles:
            errores.append(f"{e['id']}: medida desconocida '{medida}'")
            continue
        if medida not in valores:
            if medida.startswith("recursos:"):
                # Sin síntesis no hay dato. La síntesis es compuerta de release
                # (ADR 0010): se dice, no se finge un verde.
                print(f"NO CORRIÓ {e['id']}: falta la síntesis (make optimizacion)")
                continue
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
