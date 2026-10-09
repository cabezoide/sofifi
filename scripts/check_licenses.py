# SPDX-License-Identifier: MIT
"""Compuerta ``licenses`` (ADR 0002, SPEC_RAIZ §8.2).

Cuándo: trabajo duro de ``scripts/ci_local.sh`` (pre-push y ``make ci``).

Comprueba tres cosas:

1. Todo fichero fuente versionado declara ``SPDX-License-Identifier`` en sus
   primeras líneas (``.py``, ``.sh``, ``.v``, ``.sv``, ``.vh``, ``.svh``,
   ``.sasm`` y los hooks).
2. Un fichero con licencia distinta de MIT está declarado en ``docs/terceros.yaml``
   con esa misma licencia.
3. Ninguna entrada de ``docs/terceros.yaml`` con ``uso: portado`` tiene una licencia
   fuera de la lista permisiva: el copyleft se estudia, no se copia.

Uso::

    .venv/bin/python scripts/check_licenses.py

No tiene opciones y no escribe nada. Salida: 0 bien; 1 hay errores.

No comprueba que el código portado sea fiel a su origen ni que la atribución en
``NOTICE`` sea completa; eso es revisión humana del PR que porta.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml
from sin_opciones import exigir_sin_opciones

ROOT = Path(__file__).resolve().parent.parent
TERCEROS = ROOT / "docs" / "terceros.yaml"

LICENCIA_PROPIA = "MIT"
PERMISIVAS = {
    "MIT",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "Apache-2.0",
    "ISC",
    "Unlicense",
    "CC0-1.0",
    "LicenseRef-PublicDomain",
    "LicenseRef-STK-4.3",
    "LicenseRef-Spin-Open-Reverb",
}
USOS = {"estudiado", "portado"}
CAMPOS = {"id", "nombre", "url", "licencia", "uso", "motivo"}
EXTENSIONES = {".py", ".sh", ".v", ".sv", ".vh", ".svh", ".sasm"}
LINEAS_CABECERA = 5


def ficheros_fuente() -> list[Path]:
    salida = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split()
    rutas = []
    for rel in salida:
        ruta = ROOT / rel
        if not ruta.is_file():
            continue
        if ruta.suffix in EXTENSIONES or rel.startswith("scripts/hooks/"):
            rutas.append(ruta)
    return rutas


def spdx_de(ruta: Path) -> str | None:
    with ruta.open(encoding="utf-8", errors="replace") as fh:
        for _ in range(LINEAS_CABECERA):
            linea = fh.readline()
            if "SPDX-License-Identifier:" in linea:
                return linea.split("SPDX-License-Identifier:", 1)[1].strip(" */\n")
    return None


def main() -> int:
    errores: list[str] = []
    datos = yaml.safe_load(TERCEROS.read_text(encoding="utf-8")) or {}
    entradas = datos.get("terceros") or []

    ids: set[str] = set()
    declarados: dict[str, str] = {}
    for e in entradas:
        faltan = CAMPOS - set(e)
        if faltan:
            errores.append(f"terceros.yaml: entrada {e.get('id')} sin campos {sorted(faltan)}")
            continue
        if e["id"] in ids:
            errores.append(f"terceros.yaml: id repetido {e['id']}")
        ids.add(e["id"])
        if e["uso"] not in USOS:
            errores.append(f"terceros.yaml: {e['id']} uso '{e['uso']}' no está en {sorted(USOS)}")
        if e["uso"] == "portado" and e["licencia"] not in PERMISIVAS:
            errores.append(
                f"terceros.yaml: {e['id']} se declara PORTADO con licencia {e['licencia']},"
                " que no es permisiva (ADR 0002)"
            )
        for f in e.get("ficheros") or []:
            declarados[f] = e["licencia"]

    fuentes = ficheros_fuente()
    for ruta in fuentes:
        rel = ruta.relative_to(ROOT).as_posix()
        lic = spdx_de(ruta)
        if lic is None:
            errores.append(f"{rel}: falta 'SPDX-License-Identifier' en las primeras líneas")
        elif lic != LICENCIA_PROPIA and declarados.get(rel) != lic:
            errores.append(f"{rel}: licencia {lic} no declarada en docs/terceros.yaml")

    for f in declarados:
        if not (ROOT / f).is_file():
            errores.append(f"terceros.yaml: fichero declarado inexistente {f}")

    if errores:
        print("\n".join(errores))
        print("Salidas: añadir la cabecera SPDX / declarar el origen, o no portar ese código.")
        return 1
    print(f"licenses: {len(fuentes)} fuentes con SPDX; {len(entradas)} terceros declarados.")
    return 0


if __name__ == "__main__":
    exigir_sin_opciones(__doc__)
    sys.exit(main())
