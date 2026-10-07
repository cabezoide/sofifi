# SPDX-License-Identifier: MIT
"""Compuerta ``optimizacion`` (ADR 0010): sintetiza cada top y busca lo que sobra.

Para cada top de ``rtl/top/tops.txt`` ejecuta ``scripts/fpga.sh synth`` (que deja
``build/<top>_recursos.json``) y luego:

- **bloquea** si algún reloj no alcanza su frecuencia objetivo;
- imprime **pistas** para la segunda vuelta antes del PR. No bloquean: cada una
  se optimiza o se justifica en la descripción del PR.

Los listones de recursos (que no empeoren) los aplica ``ratchets`` con las medidas
``recursos:<top>:<celda>``, que leen el JSON que deja este trabajo.

No comprueba que el diseño sea mínimo: las pistas son heurísticas, y un diseño
sin pistas aún puede sobrar. Para eso está la segunda vuelta.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TOPS = ROOT / "rtl" / "top" / "tops.txt"

# Umbrales de las pistas. Se eligieron con el caso de la Fase 02: la primera
# versión de hola_uart tenía 146 ALU para 91 DFF y 195 MUX2 para 353 LUT4.
ALU_POR_DFF = 1.0
MUX_POR_LUT = 0.5
HOLGURA_FMAX = 1.2


def leer_tops() -> dict[str, list[str]]:
    tops: dict[str, list[str]] = {}
    for linea in TOPS.read_text(encoding="utf-8").splitlines():
        campos = linea.split("#", 1)[0].split()
        if campos:
            tops[campos[0]] = campos[1:]
    return tops


def usado(recursos: dict[str, Any], celda: str) -> int:
    return int(recursos.get(celda, {}).get("usado", 0))


def pistas(top: str, informe: dict[str, Any]) -> list[str]:
    r = informe["recursos"]
    lut, alu, dff = usado(r, "LUT4"), usado(r, "ALU"), usado(r, "DFF")
    mux = sum(usado(r, c) for c in ("MUX2_LUT5", "MUX2_LUT6", "MUX2_LUT7", "MUX2_LUT8"))
    salida = []
    if dff and alu > ALU_POR_DFF * dff:
        salida.append(
            f"{top}: {alu} ALU para {dff} DFF. Hay más acarreo que registros: ¿aritmética"
            " duplicada, o calculada en paralelo para luego elegir un resultado?"
        )
    if lut and mux > MUX_POR_LUT * lut:
        salida.append(
            f"{top}: {mux} MUX2 anchos para {lut} LUT4. ¿Un multiplexor que elige entre"
            " resultados ya calculados? Elegir antes la entrada y calcular una vez."
        )
    for reloj, f in informe["relojes"].items():
        if f["objetivo_mhz"] <= f["alcanzada_mhz"] < HOLGURA_FMAX * f["objetivo_mhz"]:
            salida.append(
                f"{top}: {reloj} cierra con {f['alcanzada_mhz']} MHz para {f['objetivo_mhz']}."
                " Margen justo: ¿segmentar el camino crítico (ver build/<top>.pnr.log)?"
            )
    return salida


def main() -> int:
    errores: list[str] = []
    todas: list[str] = []
    for top, fuentes in leer_tops().items():
        proc = subprocess.run(
            [str(ROOT / "scripts" / "fpga.sh"), "synth", *fuentes],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            errores.append(f"{top}: la síntesis falla\n{proc.stderr[-2000:]}")
            continue
        informe = json.loads((ROOT / "build" / f"{top}_recursos.json").read_text("utf-8"))
        r = informe["recursos"]
        print(
            f"{top}: {usado(r, 'LUT4')} LUT4 · {usado(r, 'ALU')} ALU · {usado(r, 'DFF')} DFF"
            f" · {usado(r, 'BSRAM')} BSRAM · {usado(r, 'MULT12X12')} MULT12X12"
        )
        for reloj, f in informe["relojes"].items():
            if f["alcanzada_mhz"] < f["objetivo_mhz"]:
                errores.append(
                    f"{top}: {reloj} no cierra timing ({f['alcanzada_mhz']} MHz de"
                    f" {f['objetivo_mhz']})"
                )
        todas += pistas(top, informe)

    for p in todas:
        print(f"PISTA {p}")
    if errores:
        print("\n".join(errores))
        return 1
    print(f"optimizacion: timing cerrado; {len(todas)} pistas para la segunda vuelta.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
