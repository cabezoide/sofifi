# SPDX-License-Identifier: MIT
"""Compuerta ``cierre``: al cerrar una fase, la documentación y las infografías están al día.

La persona propietaria la pidió el 2026-10-08 (ADR 0001, actualización). La
versión del proyecto es la última fase cerrada de ``docs/fases/estado_fases.csv``.

Cuándo: trabajo duro de ``scripts/ci_local.sh`` (pre-push y ``make ci``).

Siempre comprueba:

1. Los README de los cuatro idiomas declaran esa versión (`` `0.N` ``).
2. Las infografías ``sofifi`` de los cuatro idiomas declaran esa versión.
3. Cada captura de ``docs/img/`` se hizo con la infografía tal como está ahora:
   ``scripts/capturar_infografia.py`` anota la huella del HTML en
   ``docs/img/capturas.json``.

En la rama que cierra una fase (``estado_fases.csv`` cambia respecto de
``origin/main``), además:

4. Ninguna traducción está declarada ``desactualizada`` (ADR 0007).
5. ``docs/arquitectura_fpga.md`` tiene la sección de esa fase.
6. La spec de la fase dice que está cerrada.

Uso::

    .venv/bin/python scripts/check_cierre.py

No tiene opciones y no escribe nada. Necesita git (compara con ``origin/main``
o ``main``). Salida: 0 bien; 1 hay errores (uno por línea).
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

from check_i18n import IDIOMAS, RE_SELLO, TRADUCIDOS, huella, traduccion_de
from sin_opciones import exigir_sin_opciones

ROOT = Path(__file__).resolve().parent.parent
CONTROL = "docs/fases/estado_fases.csv"
MANIFIESTO = ROOT / "docs" / "img" / "capturas.json"
SECCIONES = ("portada", "porque", "ruta")
RE_VERSION_INFOGRAFIA = re.compile(r"(?:versión|version|版本|バージョン) 0\.(\d+)")


def ultima_fase() -> tuple[int, str]:
    with (ROOT / CONTROL).open(encoding="utf-8") as f:
        filas = list(csv.DictReader(f, delimiter=";"))
    cerradas = [fila for fila in filas if fila["estado"] == "cerrada"]
    fila = max(cerradas, key=lambda r: int(r["fase"]))
    return int(fila["fase"]), fila["spec"]


def idiomas() -> tuple[str, ...]:
    return ("es", *IDIOMAS)


def con_idioma(rel: str, idioma: str) -> str:
    if idioma == "es":
        return rel
    return traduccion_de(rel, idioma).relative_to(ROOT).as_posix()


def captura(seccion: str, idioma: str) -> str:
    return f"docs/img/{seccion}.png" if idioma == "es" else f"docs/img/{idioma}/{seccion}.png"


def cierra_una_fase() -> bool:
    """True si la rama cambia el control de fases respecto de origin/main (o main)."""
    for base in ("origin/main", "main"):
        r = subprocess.run(
            ["git", "merge-base", "HEAD", base], cwd=ROOT, capture_output=True, text=True
        )
        if r.returncode == 0:
            diff = subprocess.run(
                ["git", "diff", "--quiet", r.stdout.strip(), "--", CONTROL], cwd=ROOT
            )
            return diff.returncode == 1
    return False


def comprobar() -> list[str]:
    errores: list[str] = []
    n, spec = ultima_fase()
    version = f"0.{n}"
    for idioma in idiomas():
        readme = con_idioma("README.md", idioma)
        m = re.search(r"`0\.(\d+)`", (ROOT / readme).read_text(encoding="utf-8"))
        if not m or int(m.group(1)) != n:
            errores.append(f"{readme}: la versión no es `{version}` (última fase cerrada: {n:02d})")
        info = con_idioma("docs/infografias/sofifi.html", idioma)
        m = RE_VERSION_INFOGRAFIA.search((ROOT / info).read_text(encoding="utf-8"))
        if not m or int(m.group(1)) != n:
            errores.append(f"{info}: la versión no es {version}")
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8")) if MANIFIESTO.is_file() else {}
    for idioma in idiomas():
        info = con_idioma("docs/infografias/sofifi.html", idioma)
        for seccion in SECCIONES:
            png = captura(seccion, idioma)
            anotada = manifiesto.get(png, {})
            if not (ROOT / png).is_file():
                errores.append(f"falta la captura {png}")
            elif anotada.get("html") != info or anotada.get("sha") != huella(ROOT / info):
                errores.append(
                    f"{png}: no se capturó de la versión actual de {info}."
                    " Salida: `scripts/capturar_infografia.py --todas`."
                )
    if cierra_una_fase():
        for fuente in TRADUCIDOS:
            for idioma in IDIOMAS:
                trad = traduccion_de(fuente, idioma)
                m = RE_SELLO.match(trad.read_text(encoding="utf-8").splitlines()[0])
                if m and m.group("estado") != "al_dia":
                    rel = trad.relative_to(ROOT).as_posix()
                    errores.append(f"{rel}: al cerrar una fase, ninguna traducción queda atrás")
        arquitectura = (ROOT / "docs" / "arquitectura_fpga.md").read_text(encoding="utf-8")
        if not re.search(rf"^### Fase {n:02d}\b", arquitectura, re.MULTILINE):
            errores.append(f"docs/arquitectura_fpga.md: falta la sección «Fase {n:02d}»")
        texto_spec = (ROOT / "docs" / "fases" / spec).read_text(encoding="utf-8")
        if "> Cerrada el" not in texto_spec:
            errores.append(f"docs/fases/{spec}: la spec no dice «Cerrada el …»")
    return errores


def main() -> int:
    errores = comprobar()
    if errores:
        print("\n".join(errores))
        return 1
    n, _ = ultima_fase()
    print(f"cierre: versión 0.{n} en README e infografías (4 idiomas); capturas al día.")
    return 0


if __name__ == "__main__":
    exigir_sin_opciones(__doc__)
    sys.exit(main())
