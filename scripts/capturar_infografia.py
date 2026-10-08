# SPDX-License-Identifier: MIT
"""Captura una sección de una infografía como PNG a escala 2 (para el README).

Uso::

    .venv/bin/python scripts/capturar_infografia.py \\
        docs/infografias/sofifi.html portada docs/img/portada.png
    .venv/bin/python scripts/capturar_infografia.py --todas   # 3 secciones × 4 idiomas

Cada captura anota en ``docs/img/capturas.json`` la huella del HTML del que
sale. La compuerta ``cierre`` (``scripts/check_cierre.py``) la compara con la
infografía actual.

La sección es el ``id`` de un hijo directo de ``.envoltorio`` (``portada``,
``porque``, ``ruta``). Solo biblioteca estándar y chrome-headless-shell (caché
de Playwright):

1. Una copia de la página oculta las demás secciones.
2. Un primer paso de Chrome (``--dump-dom``) mide la altura de la sección.
3. El segundo paso captura una ventana de 1 080 px de ancho y esa altura, a escala 2.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MANIFIESTO = RAIZ / "docs" / "img" / "capturas.json"
SECCIONES = ("portada", "porque", "ruta")
IDIOMAS = ("es", "en", "zh-CN", "ja")
CHROME = sorted(
    Path.home().glob(".cache/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell")
)
ANCHO = 1080


def _chrome(*args: str) -> str:
    resultado = subprocess.run(
        [
            str(CHROME[-1]),
            "--no-sandbox",
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return resultado.stdout


def capturar(html: Path, seccion: str, salida: Path) -> None:
    texto = html.read_text(encoding="utf-8")
    estilo = (
        f".envoltorio > *:not(#{seccion}){{display:none}}"
        f" #{seccion}{{border-bottom:0}} .envoltorio{{padding-block:24px}}"
    )
    medir = (
        "<script>addEventListener('load',()=>{document.title='ALTO:'+"
        "Math.ceil(document.querySelector('.grano').getBoundingClientRect().height)})</script>"
    )
    texto = texto.replace("</style>", estilo + "</style>", 1).replace("</body>", "") + medir
    with tempfile.TemporaryDirectory() as tmp:
        pagina = Path(tmp) / "pagina.html"
        pagina.write_text(texto, encoding="utf-8")
        dom = _chrome(
            f"--window-size={ANCHO},800",
            "--virtual-time-budget=5000",
            "--dump-dom",
            pagina.as_uri(),
        )
        m = re.search(r"ALTO:(\d+)", dom)
        if not m:
            raise RuntimeError("no se pudo medir la altura de la sección")
        salida.parent.mkdir(parents=True, exist_ok=True)
        _chrome(
            "--force-device-scale-factor=2",
            f"--window-size={ANCHO},{m.group(1)}",
            "--virtual-time-budget=5000",
            f"--screenshot={salida.resolve()}",
            pagina.as_uri(),
        )


def anotar(html: Path, salida: Path) -> None:
    """Guarda en el manifiesto de qué HTML (y de qué versión) sale la captura."""
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8")) if MANIFIESTO.is_file() else {}
    clave = salida.resolve().relative_to(RAIZ).as_posix()
    manifiesto[clave] = {
        "html": html.resolve().relative_to(RAIZ).as_posix(),
        "sha": hashlib.sha256(html.read_bytes()).hexdigest()[:12],
    }
    texto = json.dumps(dict(sorted(manifiesto.items())), ensure_ascii=False, indent=2)
    MANIFIESTO.write_text(texto + "\n", encoding="utf-8")


def todas() -> list[tuple[Path, str, Path]]:
    trabajos = []
    for idioma in IDIOMAS:
        sufijo = "" if idioma == "es" else f".{idioma}"
        carpeta = RAIZ / "docs" / "img" / ("" if idioma == "es" else idioma)
        html = RAIZ / "docs" / "infografias" / f"sofifi{sufijo}.html"
        trabajos += [(html, s, carpeta / f"{s}.png") for s in SECCIONES]
    return trabajos


def main() -> int:
    if sys.argv[1:] == ["--todas"] and CHROME:
        trabajos = todas()
    elif len(sys.argv) == 4 and CHROME:
        trabajos = [(Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]))]
    else:
        print(__doc__, file=sys.stderr)
        return 1
    for html, seccion, salida in trabajos:
        capturar(html, seccion, salida)
        anotar(html, salida)
        print(f"{seccion} → {salida.resolve().relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
