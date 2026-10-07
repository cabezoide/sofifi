# SPDX-License-Identifier: MIT
"""Tests-contrato de arquitectura (SPEC_RAIZ §4.3, ADR 0003).

Se leen los fuentes con ``ast``: no se importa el módulo, no hay red ni disco
aparte de leer el código. Entraron en verde con el grafo vacío; su trabajo es
impedir la primera violación, no arrastrar deuda.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

PAQUETE = Path(__file__).resolve().parent.parent / "ambient"
RAIZ = "ambient"

# Capa → capas de ambient que NO puede importar.
PROHIBIDO: dict[str, set[str]] = {
    "domain": {"ports", "adapters", "services", "cli"},
    "ports": {"adapters", "services", "cli"},
    "adapters": {"services", "cli"},
    "services": {"adapters", "cli"},
}
# El dominio es DSP puro: nada que toque el mundo.
IO_PROHIBIDO_EN_DOMINIO = {
    "os",
    "io",
    "sys",
    "wave",
    "pathlib",
    "subprocess",
    "socket",
    "shutil",
    "tempfile",
    "soundfile",
    "random",
    "time",
    "datetime",
}


def _modulos() -> list[tuple[str, Path]]:
    res = []
    for ruta in sorted(PAQUETE.rglob("*.py")):
        rel = ruta.relative_to(PAQUETE.parent).with_suffix("")
        partes = list(rel.parts)
        if partes[-1] == "__init__":
            partes.pop()
        res.append((".".join(partes), ruta))
    return res


def _capa(modulo: str) -> str | None:
    partes = modulo.split(".")
    return partes[1] if len(partes) > 1 else None


def _imports_cabecera(ruta: Path, modulo: str) -> set[str]:
    """Imports de nivel de módulo (los perezosos dentro de funciones no son ciclo)."""
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    es_paquete = ruta.name == "__init__.py"
    res: set[str] = set()
    for nodo in arbol.body:
        if isinstance(nodo, ast.Import):
            res.update(a.name for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.level:
                base = modulo.split(".")
                base = base if es_paquete else base[:-1]
                base = base[: len(base) - (nodo.level - 1)]
                destino = ".".join([*base, nodo.module] if nodo.module else base)
            else:
                destino = nodo.module or ""
            res.add(destino)
            res.update(f"{destino}.{a.name}" for a in nodo.names)
    return res


def _todos_los_imports(ruta: Path) -> set[str]:
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    res: set[str] = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            res.update(a.name.split(".")[0] for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and not nodo.level and nodo.module:
            res.add(nodo.module.split(".")[0])
    return res


MODULOS = _modulos()


@pytest.mark.parametrize(("modulo", "ruta"), MODULOS, ids=[m for m, _ in MODULOS])
def test_las_capas_no_se_filtran(modulo: str, ruta: Path) -> None:
    capa = _capa(modulo)
    if capa not in PROHIBIDO:
        return
    for imp in _imports_cabecera(ruta, modulo) | _todos_los_imports(ruta):
        if imp.startswith(f"{RAIZ}."):
            destino = imp.split(".")[1]
            assert destino not in PROHIBIDO[capa], f"{modulo} ({capa}) importa {imp}"


@pytest.mark.parametrize(("modulo", "ruta"), MODULOS, ids=[m for m, _ in MODULOS])
def test_el_dominio_no_hace_io(modulo: str, ruta: Path) -> None:
    if _capa(modulo) != "domain":
        return
    malos = _todos_los_imports(ruta) & IO_PROHIBIDO_EN_DOMINIO
    assert not malos, f"{modulo} importa I/O en el dominio: {sorted(malos)}"


def test_no_hay_ciclos_de_import_en_cabecera() -> None:
    conocidos = {m for m, _ in MODULOS}
    grafo: dict[str, set[str]] = {}
    for modulo, ruta in MODULOS:
        grafo[modulo] = {i for i in _imports_cabecera(ruta, modulo) if i in conocidos} - {modulo}

    visitando: set[str] = set()
    hecho: set[str] = set()

    def visitar(nodo: str, camino: list[str]) -> None:
        if nodo in hecho:
            return
        assert nodo not in visitando, "ciclo: " + " → ".join([*camino, nodo])
        visitando.add(nodo)
        for vecino in sorted(grafo[nodo]):
            visitar(vecino, [*camino, nodo])
        visitando.discard(nodo)
        hecho.add(nodo)

    for m in sorted(grafo):
        visitar(m, [])


def test_existen_todas_las_capas_y_se_importan() -> None:
    for capa in PROHIBIDO:
        assert (PAQUETE / capa / "__init__.py").is_file(), f"falta la capa {capa}"
        importlib.import_module(f"{RAIZ}.{capa}")


def test_el_detector_ve_imports_absolutos_relativos_y_de_io(tmp_path: Path) -> None:
    """El contrato no puede ser un verde que miente: debe ver una violación sembrada."""
    malo = tmp_path / "ambient" / "domain" / "malo.py"
    malo.parent.mkdir(parents=True)
    malo.write_text(
        "import os\nfrom ambient.adapters import wav\nfrom ..services import render\n",
        encoding="utf-8",
    )
    cabecera = _imports_cabecera(malo, "ambient.domain.malo")
    assert "ambient.adapters" in cabecera
    assert "ambient.services" in cabecera
    assert "os" in _todos_los_imports(malo)
