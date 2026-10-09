# SPDX-License-Identifier: MIT
"""Compuerta ``i18n`` (ADR 0007): las traducciones no mienten sobre su frescura.

Cuándo: trabajo duro de ``scripts/ci_local.sh`` (pre-push y ``make ci``).
Se resella una traducción cada vez que se pone al día con su fuente.

Cada documento traducido (``TRADUCIDOS``) tiene una traducción por idioma, y cada
traducción empieza con un sello::

    <!-- i18n: fuente=README.md sha=<12 hex> estado=al_dia -->

Qué bloquea:

- que falte una traducción de un documento traducido;
- un sello mal formado o con una fuente inexistente;
- ``estado=al_dia`` con un ``sha`` que ya no coincide con la fuente. Eso es la mentira.

Qué no bloquea: ``estado=desactualizada``, que es honesto y se publica.
No comprueba la calidad de la traducción.

Uso::

    .venv/bin/python scripts/check_i18n.py                         # comprobar
    .venv/bin/python scripts/check_i18n.py --sellar README.en.md   # resellar

``--sellar`` acepta un fichero por llamada. Escribe solo la primera línea de esa
traducción. Salida: 0 bien; 1 hay errores o falta el sello; 2 argumentos
incorrectos (imprime esta ayuda).
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

IDIOMAS = ("en", "zh-CN", "ja")
# Documentos con traducción (ADR 0007): la documentación pública y técnica.
TRADUCIDOS = (
    "README.md",
    "demo_examples/README.md",
    "schematics/README.md",
    "docs/programas.md",
    "docs/arquitectura_fpga.md",
    "docs/EXTENDING.md",
    "docs/scripts.md",
    "BOM.md",
    "SBOM.md",
    "fails.md",
    "docs/infografias/sofifi.html",
    "docs/infografias/estado-del-arte.html",
)
ESTADOS = ("al_dia", "desactualizada")
RE_SELLO = re.compile(
    r"^<!-- i18n: fuente=(?P<fuente>\S+) sha=(?P<sha>[0-9a-f]{12}) "
    r"estado=(?P<estado>\S+) -->$"
)


def huella(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()[:12]


def traduccion_de(fuente: str, idioma: str) -> Path:
    base = Path(fuente)
    return ROOT / base.with_name(f"{base.stem}.{idioma}{base.suffix}")


def sellar(rel: str) -> int:
    ruta = ROOT / rel
    lineas = ruta.read_text(encoding="utf-8").splitlines(keepends=True)
    m = RE_SELLO.match(lineas[0].rstrip("\n")) if lineas else None
    if not m:
        print(f"{rel}: no tiene sello en la primera línea")
        return 1
    fuente = ROOT / m.group("fuente")
    lineas[0] = f"<!-- i18n: fuente={m.group('fuente')} sha={huella(fuente)} estado=al_dia -->\n"
    ruta.write_text("".join(lineas), encoding="utf-8")
    print(f"{rel}: sellado al_dia con la fuente actual")
    return 0


def comprobar() -> int:
    errores: list[str] = []
    desactualizadas: list[str] = []
    for fuente in TRADUCIDOS:
        ruta_fuente = ROOT / fuente
        for idioma in IDIOMAS:
            trad = traduccion_de(fuente, idioma)
            rel = trad.relative_to(ROOT).as_posix()
            if not trad.is_file():
                errores.append(f"falta la traducción {rel} de {fuente}")
                continue
            primera = trad.read_text(encoding="utf-8").splitlines()[0]
            m = RE_SELLO.match(primera)
            if not m:
                errores.append(f"{rel}: primera línea sin sello i18n válido")
                continue
            if m.group("fuente") != fuente:
                errores.append(f"{rel}: el sello cita {m.group('fuente')}, se esperaba {fuente}")
            if m.group("estado") not in ESTADOS:
                errores.append(f"{rel}: estado '{m.group('estado')}' no está en {ESTADOS}")
            vigente = huella(ruta_fuente)
            if m.group("estado") == "al_dia" and m.group("sha") != vigente:
                errores.append(
                    f"{rel}: dice estar al día, pero {fuente} cambió"
                    f" (sello {m.group('sha')}, fuente {vigente})."
                    f" Salidas: actualizarla y `scripts/check_i18n.py --sellar {rel}`,"
                    " o marcarla estado=desactualizada."
                )
            if m.group("estado") == "desactualizada":
                desactualizadas.append(rel)
    if desactualizadas:
        print("AVISO, traducciones declaradas desactualizadas: " + ", ".join(desactualizadas))
    if errores:
        print("\n".join(errores))
        return 1
    n = len(TRADUCIDOS) * len(IDIOMAS)
    print(f"i18n: {n} traducciones con sello honesto ({', '.join(IDIOMAS)}).")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "--sellar":
        return sellar(argv[1])
    if argv:
        print(__doc__)
        return 2
    return comprobar()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
