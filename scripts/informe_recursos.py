# SPDX-License-Identifier: MIT
"""Extrae del informe JSON de nextpnr el uso de recursos y la frecuencia alcanzada.

Cuándo: lo llama ``scripts/fpga.sh synth`` al final de cada síntesis. No se
llama a mano.

Uso::

    .venv/bin/python scripts/informe_recursos.py build/<top>.informe.json

Lee el informe de nextpnr y escribe en la salida estándar un JSON con dos
claves: ``recursos`` (celdas usadas y disponibles) y ``relojes`` (MHz
alcanzados y objetivo). ``fpga.sh`` lo guarda en ``build/<top>_recursos.json``.
El argumento es obligatorio. Salida: 0 bien; 2 sin argumento (muestra el uso).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def resumir(informe: dict[str, Any]) -> dict[str, Any]:
    uso = {
        nombre: {"usado": d["used"], "disponible": d["available"]}
        for nombre, d in sorted(informe.get("utilization", {}).items())
        if d.get("used")
    }
    relojes = {
        nombre: {
            "alcanzada_mhz": round(d["achieved"], 2),
            "objetivo_mhz": round(d["constraint"], 2),
        }
        for nombre, d in sorted(informe.get("fmax", {}).items())
    }
    return {"recursos": uso, "relojes": relojes}


def main(argv: list[str]) -> int:
    if len(argv) != 1 or argv[0] in ("-h", "--help"):
        print(__doc__, file=sys.stderr if len(argv) != 1 else sys.stdout)
        return 0 if argv in (["-h"], ["--help"]) else 2
    datos = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    print(json.dumps(resumir(datos), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
