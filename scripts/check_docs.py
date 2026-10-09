# SPDX-License-Identifier: MIT
"""Compuerta ``docs``: los mapas se contrastan contra el territorio (SPEC_RAIZ §3.3, P8).

Cuándo: trabajo duro de ``scripts/ci_local.sh`` (pre-push y ``make ci``).
También corre solo con ``make docs``.

Subcomprobaciones:

- ``rutas``: toda ruta citada entre comillas invertidas en los mapas existe.
- ``make``: todo ``make <objetivo>`` citado existe en el Makefile.
- ``adr-citas``: todo "ADR NNNN" citado en el repo existe.
- ``adr-indice``: ``docs/adr/README.md`` lista exactamente los ADR que hay.
- ``fases``: cada fila del control tiene spec, y el título coincide con el H1.
- ``version``: la versión del README es ``0.<última fase cerrada>``.
- ``hook``: el pre-push delega en ``--no-soft`` y no tiene lista de trabajos propia.
- ``registros``: los YAML de registro tienen los campos obligatorios e ids únicos.
- ``mediciones``: ninguna medición ha caducado (P5).

Los mapas son los ficheros de ``MAPAS``. Un documento fuera de esa lista no se
comprueba.

Uso::

    .venv/bin/python scripts/check_docs.py

No tiene opciones y no escribe nada. Salida: 0 si todo es coherente; 1 si hay
errores (uno por línea).

No comprueba que la prosa sea correcta, solo que lo que cita existe.
"""

from __future__ import annotations

import csv
import datetime as dt
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

MAPAS = [
    "README.md",
    "README.en.md",
    "README.zh-CN.md",
    "AGENTS.md",
    "CLAUDE.md",
    "SECURITY.md",
    "docs/EXTENDING.md",
    "docs/scripts.md",
    "docs/scripts.en.md",
    "docs/scripts.zh-CN.md",
    "docs/scripts.ja.md",
    "demo_examples/README.md",
    "docs/security/CUMPLIMIENTO.md",
    "model/AGENTS.md",
    "rtl/AGENTS.md",
    "sim/AGENTS.md",
]
EXT_RUTA = (".md", ".py", ".sh", ".yaml", ".yml", ".csv", ".v", ".sv", ".toml", ".txt", ".cst")
RE_TICK = re.compile(r"`([^`\s]+)`")
RE_MAKE = re.compile(r"\bmake ([a-z][a-z0-9-]*)")
RE_ADR = re.compile(r"\bADR[ -](\d{4})\b")
RE_ADR_FICHERO = re.compile(r"^(\d{4})-[a-z0-9-]+\.md$")

REGISTROS = {
    "docs/ratchets.yaml": (
        "ratchets",
        {"id", "nombre", "medida", "liston", "direccion", "motivo"},
    ),
    "docs/promesas.yaml": (
        "promesas",
        {"id", "claim", "source", "verifier", "kind", "status", "scope", "motivo"},
    ),
    "docs/madurez.yaml": (
        "capacidades",
        {"id", "capacidad", "nivel", "scope", "no_cubre", "brecha"},
    ),
    "docs/mediciones.yaml": (
        "mediciones",
        {
            "id",
            "caracteristica",
            "nombre",
            "valor",
            "unidad",
            "umbral",
            "direccion",
            "fecha",
            "caduca_en_dias",
            "como",
            "entorno",
            "no_dice",
        },
    ),
}
CADUCIDAD_MAXIMA_DIAS = 365


def parece_ruta(token: str) -> bool:
    # Los marcadores de posición se escriben con <…> y no son rutas reales.
    if token.startswith(("http", "-", "$", "~")) or any(c in token for c in "*{<"):
        return False
    if "/" in token:
        return True
    return token.endswith(EXT_RUTA) and token[0].isalpha()


def comprobar_rutas(errores: list[str]) -> None:
    for mapa in MAPAS:
        ruta_mapa = ROOT / mapa
        if not ruta_mapa.is_file():
            errores.append(f"rutas: falta el mapa {mapa}")
            continue
        for token in RE_TICK.findall(ruta_mapa.read_text(encoding="utf-8")):
            limpio = token.rstrip(".,:;)").split("::")[0]
            limpio = re.sub(r":\d+$", "", limpio)
            if not parece_ruta(limpio):
                continue
            candidatos = [ROOT / limpio, ruta_mapa.parent / limpio]
            if not any(c.exists() for c in candidatos):
                errores.append(f"rutas: {mapa} cita `{token}`, que no existe")


def objetivos_make() -> set[str]:
    texto = (ROOT / "Makefile").read_text(encoding="utf-8")
    return set(re.findall(r"^([a-z][a-z0-9-]*):", texto, flags=re.M))


def comprobar_make(errores: list[str]) -> None:
    objetivos = objetivos_make()
    for mapa in MAPAS:
        ruta = ROOT / mapa
        if ruta.is_file():
            for obj in RE_MAKE.findall(ruta.read_text(encoding="utf-8")):
                if obj not in objetivos:
                    errores.append(f"make: {mapa} cita 'make {obj}', que no existe")


def adrs_existentes() -> dict[str, Path]:
    res = {}
    for p in (ROOT / "docs" / "adr").iterdir():
        m = RE_ADR_FICHERO.match(p.name)
        if m:
            res[m.group(1)] = p
    return res


def comprobar_adr(errores: list[str]) -> None:
    existentes = adrs_existentes()
    for md in ROOT.rglob("*.md"):
        if any(parte.startswith(".") for parte in md.relative_to(ROOT).parts):
            continue
        if md.name == "SPEC_RAIZ.md":
            continue
        for num in RE_ADR.findall(md.read_text(encoding="utf-8")):
            if num not in existentes:
                rel = md.relative_to(ROOT)
                errores.append(f"adr-citas: {rel} cita ADR {num}, que no existe")
    indice = (ROOT / "docs" / "adr" / "README.md").read_text(encoding="utf-8")
    en_indice = set(re.findall(r"\]\((\d{4})-[a-z0-9-]+\.md\)", indice))
    for num in sorted(set(existentes) - en_indice):
        errores.append(f"adr-indice: ADR {num} no está en docs/adr/README.md")
    for num in sorted(en_indice - set(existentes)):
        errores.append(f"adr-indice: el índice lista ADR {num}, que no existe")
    for enlace in re.findall(r"\]\((\d{4}-[a-z0-9-]+\.md)\)", indice):
        if not (ROOT / "docs" / "adr" / enlace).is_file():
            errores.append(f"adr-indice: enlace roto {enlace}")


def h1(ruta: Path) -> str:
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.startswith("# "):
            return linea[2:].strip()
    return ""


def comprobar_fases(errores: list[str]) -> str | None:
    control = ROOT / "docs" / "fases" / "estado_fases.csv"
    with control.open(encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh, delimiter=";"))
    ultima_cerrada: str | None = None
    for fila in filas:
        spec = ROOT / "docs" / "fases" / fila["spec"]
        if not spec.is_file():
            errores.append(f"fases: la fila {fila['fase']} cita spec inexistente {fila['spec']}")
            continue
        esperado = f"Fase {fila['fase']} — {fila['titulo']}"
        if h1(spec) != esperado:
            errores.append(f"fases: H1 de {fila['spec']} es '{h1(spec)}', se esperaba '{esperado}'")
        if fila["estado"] != "cerrada":
            errores.append(
                f"fases: la fila {fila['fase']} no está cerrada; lo planificado no entra"
            )
        ultima_cerrada = fila["fase"]
    return ultima_cerrada


def comprobar_version(errores: list[str], ultima: str | None) -> None:
    m = re.search(r"Versión:\**\s*`?(0\.\d+)`?", (ROOT / "README.md").read_text(encoding="utf-8"))
    if not m:
        errores.append("version: el README no declara 'Versión: 0.N'")
        return
    esperado = f"0.{int(ultima)}" if ultima is not None else None
    if esperado and m.group(1) != esperado:
        errores.append(f"version: README dice {m.group(1)}, la última fase cerrada da {esperado}")


def comprobar_hook(errores: list[str]) -> None:
    hook = (ROOT / "scripts" / "hooks" / "pre-push").read_text(encoding="utf-8")
    if "ci_local.sh" not in hook or "--no-soft" not in hook:
        errores.append("hook: pre-push no delega en 'ci_local.sh --no-soft'")
    ci = (ROOT / "scripts" / "ci_local.sh").read_text(encoding="utf-8")
    trabajos = re.findall(r'^\s*"([a-z-]+):(?:dura|blanda|release)"', ci, flags=re.M)
    codigo_hook = "\n".join(
        linea for linea in hook.splitlines() if not linea.lstrip().startswith("#")
    )
    for t in trabajos:
        if re.search(rf"\b{re.escape(t)}\b", codigo_hook):
            errores.append(f"hook: pre-push menciona el trabajo '{t}': segunda lista (P8)")


def comprobar_registros(errores: list[str]) -> None:
    hoy = dt.date.today()
    for rel, (clave, campos) in REGISTROS.items():
        datos = yaml.safe_load((ROOT / rel).read_text(encoding="utf-8")) or {}
        if clave not in datos:
            errores.append(f"registros: {rel} no tiene la clave '{clave}'")
            continue
        ids: set[str] = set()
        for e in datos[clave] or []:
            faltan = campos - set(e)
            if faltan:
                errores.append(f"registros: {rel} {e.get('id')} sin {sorted(faltan)}")
            if e.get("id") in ids:
                errores.append(f"registros: {rel} id repetido {e.get('id')}")
            ids.add(e.get("id"))
            if clave == "mediciones" and not faltan:
                dias = int(e["caduca_en_dias"])
                if dias > CADUCIDAD_MAXIMA_DIAS:
                    errores.append(f"mediciones: {e['id']} caduca en {dias} días (> tope)")
                fecha = dt.date.fromisoformat(str(e["fecha"]))
                if fecha + dt.timedelta(days=dias) < hoy:
                    errores.append(
                        f"mediciones: {e['id']} CADUCADA ({fecha} + {dias} d)."
                        " Salidas: volver a medir, o bajar la nota de madurez."
                    )


def main() -> int:
    errores: list[str] = []
    comprobar_rutas(errores)
    comprobar_make(errores)
    comprobar_adr(errores)
    ultima = comprobar_fases(errores)
    comprobar_version(errores, ultima)
    comprobar_hook(errores)
    comprobar_registros(errores)
    if errores:
        print("\n".join(errores))
        return 1
    print("docs: mapas, ADRs, fases, versión, hook y registros coherentes con el repo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
