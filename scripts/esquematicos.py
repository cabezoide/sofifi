# SPDX-License-Identifier: MIT
# ruff: noqa: E501 — la tabla de textos de las guías (_GUIA) tiene frases largas
"""Genera ``schematics/``: un esquemático en PDF por cada módulo de ``rtl/``.

Los esquemáticos se generan desde el RTL; no se dibujan a mano. Por módulo:

1. Yosys lee todo ``rtl/`` (con ``SIMULACION``, como el lint) y elabora el módulo
   sin aplanar: los submódulos salen como cajas con su nombre.
2. ``proc; opt; clean`` deja celdas de nivel de palabra: sumadores, comparadores,
   multiplexores, flip-flops y memorias.
3. netlistsvg (MIT, en ``herramientas/esquematicos``) dibuja la red con los
   símbolos de la notación electrónica.
4. chrome-headless-shell convierte el SVG en un PDF vectorial, con un cajetín.

``schematics/README.md`` lista cada PDF con la huella (sha256) de su fuente.
``--comprobar`` dice qué esquemáticos están desactualizados, sin generar nada.

Uso::

    .venv/bin/python scripts/esquematicos.py              # regenera los que cambian
    .venv/bin/python scripts/esquematicos.py --todos      # regenera todos
    .venv/bin/python scripts/esquematicos.py --comprobar  # solo comprueba

Requisitos: ``npm install`` en ``herramientas/esquematicos`` y chrome-headless-shell
(caché de Playwright).
"""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RTL = RAIZ / "rtl"
DESTINO = RAIZ / "schematics"
INDICE = DESTINO / "README.md"
TRABAJO = RAIZ / "build" / "esquematicos"
NETLISTSVG = RAIZ / "herramientas" / "esquematicos" / "node_modules" / ".bin" / "netlistsvg"
NETLISTSVG_JS = NETLISTSVG.parent.parent / "netlistsvg" / "bin" / "netlistsvg.js"
# netlistsvg recorre las redes con recursión: con las redes anchas del núcleo
# (Fase 07) desborda la pila de node. Se le da más pila, y al proceso también.
PILA_NODE_KB = 200_000


def _pila_maxima() -> None:
    import resource

    _, duro = resource.getrlimit(resource.RLIMIT_STACK)
    resource.setrlimit(resource.RLIMIT_STACK, (duro, duro))


YOSYS = RAIZ / ".venv" / "bin" / "yowasp-yosys"
CHROME = sorted(
    Path.home().glob(".cache/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell")
)
LADO_MAX = 14000  # puntos de PDF; 1 px CSS = 0,75 puntos
_MODULO = re.compile(r"^\s*module\s+(\w+)", re.MULTILINE)
_SELLO = re.compile(
    r"\| `(?P<pdf>[^`]+\.pdf)` \| `(?P<fuente>[^`]+)` \| `(?P<sha>[0-9a-f]{12})` \|"
)


@dataclass(frozen=True)
class Modulo:
    nombre: str
    fuente: Path
    descripcion: str

    @property
    def pdf(self) -> Path:
        return DESTINO / self.fuente.parent.name / f"{self.nombre}.pdf"

    @property
    def sha(self) -> str:
        return hashlib.sha256(self.fuente.read_bytes()).hexdigest()[:12]


def _descripcion(texto: str) -> str:
    """Primera frase del primer párrafo de comentario, sin la licencia."""
    parrafo: list[str] = []
    for linea in texto.splitlines():
        if not linea.strip().startswith("//"):
            if parrafo:
                break
            continue
        limpia = linea.strip().removeprefix("//").strip()
        if "SPDX" in limpia:
            continue
        if not limpia:
            if parrafo:
                break
            continue
        parrafo.append(limpia)
    frase = " ".join(parrafo)
    corte = frase.find(". ")
    return frase if corte < 0 else frase[: corte + 1]


def modulos() -> list[Modulo]:
    res = []
    for fuente in sorted(RTL.glob("*/*.v")):
        texto = fuente.read_text(encoding="utf-8")
        for nombre in _MODULO.findall(texto):
            res.append(Modulo(nombre, fuente, _descripcion(texto)))
    return res


def _svg(m: Modulo) -> str:
    TRABAJO.mkdir(parents=True, exist_ok=True)
    fuentes = " ".join(str(f.relative_to(RAIZ)) for f in sorted(RTL.glob("*/*.v")))
    json = TRABAJO / f"{m.nombre}.json"
    svg = TRABAJO / f"{m.nombre}.svg"
    guion = (
        f"read_verilog -sv -DSIMULACION {fuentes}; hierarchy -top {m.nombre}; "
        f"proc; opt; clean; write_json {json.relative_to(RAIZ)}"
    )
    subprocess.run([str(YOSYS), "-q", "-p", guion], cwd=RAIZ, check=True, timeout=600)
    subprocess.run(
        ["node", f"--stack-size={PILA_NODE_KB}", str(NETLISTSVG_JS), str(json), "-o", str(svg)],
        check=True,
        timeout=600,
        preexec_fn=_pila_maxima,
    )
    return svg.read_text(encoding="utf-8")


def _pdf(m: Modulo, svg: str) -> None:
    ancho = float(re.search(r'width="([\d.]+)"', svg).group(1))  # type: ignore[union-attr]
    alto = float(re.search(r'height="([\d.]+)"', svg).group(1))  # type: ignore[union-attr]
    # Los lectores de PDF admiten hasta 14 400 puntos (200 pulgadas) por lado. El
    # dibujo es vectorial: se escala para caber sin perder detalle.
    escala = min(1.0, LADO_MAX / ((alto + 190) * 0.75), LADO_MAX / ((max(ancho, 700) + 80) * 0.75))
    ancho_pag, alto_pag = (max(ancho, 700) + 80) * escala, (alto + 190) * escala
    fuente = m.fuente.relative_to(RAIZ)
    pagina = f"""<!doctype html><meta charset="utf-8">
<style>
@page {{ size: {ancho_pag}px {alto_pag}px; margin: 0 }}
body {{ zoom: {escala}; margin: 0; padding: 30px 40px;
  font-family: "IBM Plex Mono", monospace; color: #111 }}
.cajetin {{ border: 2px solid #111; display: grid; grid-template-columns: 1fr auto;
  margin-bottom: 24px; font-size: 13px }}
.cajetin div {{ padding: 6px 10px; border-right: 1px solid #111 }}
.cajetin div:last-child {{ border-right: 0 }}
h1 {{ margin: 0; font-size: 22px }}
</style>
<div class="cajetin">
  <div><h1>{html.escape(m.nombre)}</h1>{html.escape(m.descripcion)}</div>
  <div>SOFIFI · esquemático generado<br>fuente: {fuente}<br>sha256: {m.sha}</div>
</div>
{svg}
"""
    m.pdf.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        entrada = Path(tmp) / "pagina.html"
        entrada.write_text(pagina, encoding="utf-8")
        subprocess.run(
            [
                str(CHROME[-1]),
                "--no-sandbox",
                "--headless",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--print-to-pdf={m.pdf}",
                entrada.as_uri(),
            ],
            check=True,
            timeout=300,
            capture_output=True,
        )


_GUIA = {
    "es": {
        "titulo": "# Esquemáticos del RTL",
        "intro": "Un PDF por cada módulo de `rtl/`, en notación electrónica. Se generan desde el\n"
        "Verilog con Yosys y netlistsvg; no se dibujan a mano (ADR 0012).",
        "leer": "## Cómo se leen",
        "simbolos": [
            "**Trapecio con `+`, `-`, `*`, `<`, `==`:** sumador, restador, multiplicador o comparador.",
            "**Trapecio con varias entradas y una selección:** multiplexor (`$mux`, `$pmux`).",
            "**Rectángulo con un triángulo en el reloj:** flip-flop o registro (`$dff`, `$adff`, `$sdff`).",
            "**Puertas AND, OR, XOR y NOT:** lógica de un bit, con sus símbolos estándar.",
            "**Rectángulo con un nombre de módulo:** un submódulo; tiene su propio PDF.",
            "**Flechas a izquierda y derecha:** puertos de entrada y de salida del módulo.",
        ],
        "grandes": "Los módulos grandes (`nucleo`, `tabla_hermite`) tienen cientos de celdas: el\n"
        "PDF es vectorial y se puede ampliar sin perder detalle.",
        "regenerar": "## Regenerar",
        "pasos": [
            "Instalar netlistsvg una vez: `cd herramientas/esquematicos && npm install`.",
            "Correr `.venv/bin/python scripts/esquematicos.py`. Solo regenera los que cambiaron.",
            "`--comprobar` dice qué esquemáticos están desactualizados.",
        ],
        "indice": "## Índice",
        "cabecera": "| PDF | Fuente | sha256 de la fuente | Qué es |",
        "nota": "",
    },
    "en": {
        "titulo": "# RTL schematics",
        "intro": "One PDF for each module in `rtl/`, in electronic notation. Yosys and netlistsvg\n"
        "generate them from the Verilog; nobody draws them by hand (ADR 0012, Spanish).",
        "leer": "## How to read them",
        "simbolos": [
            "**Trapezoid with `+`, `-`, `*`, `<`, `==`:** adder, subtractor, multiplier or comparator.",
            "**Trapezoid with several inputs and one select:** multiplexer (`$mux`, `$pmux`).",
            "**Rectangle with a triangle on the clock:** flip-flop or register (`$dff`, `$adff`, `$sdff`).",
            "**AND, OR, XOR and NOT gates:** one-bit logic, with their standard symbols.",
            "**Rectangle with a module name:** a submodule; it has its own PDF.",
            "**Arrows on the left and on the right:** input and output ports of the module.",
        ],
        "grandes": "The large modules (`nucleo`, `tabla_hermite`) have hundreds of cells. The PDF is\n"
        "vector graphics: you can zoom in and keep all the detail.",
        "regenerar": "## Generate them again",
        "pasos": [
            "Install netlistsvg one time: `cd herramientas/esquematicos && npm install`.",
            "Run `.venv/bin/python scripts/esquematicos.py`. It generates only the changed ones.",
            "`--comprobar` tells which schematics are out of date.",
        ],
        "indice": "## Index",
        "cabecera": "| PDF | Source | sha256 of the source | What it is |",
        "nota": "The PDF title blocks and the descriptions in this table come from the Verilog comments, in Spanish.",
    },
    "zh-CN": {
        "titulo": "# RTL 原理图",
        "intro": "`rtl/` 中每个模块一个 PDF，采用电子电路符号。由 Yosys 和 netlistsvg 从 Verilog\n"
        "生成，不手工绘制（ADR 0012，西班牙语）。",
        "leer": "## 阅读方法",
        "simbolos": [
            "**带 `+`、`-`、`*`、`<`、`==` 的梯形：** 加法器、减法器、乘法器或比较器。",
            "**有多个输入和一个选择端的梯形：** 多路选择器（`$mux`、`$pmux`）。",
            "**时钟端带三角形的矩形：** 触发器或寄存器（`$dff`、`$adff`、`$sdff`）。",
            "**与门、或门、异或门和非门：** 单比特逻辑，使用标准符号。",
            "**带模块名的矩形：** 子模块，有自己的 PDF。",
            "**左右两侧的箭头：** 模块的输入与输出端口。",
        ],
        "grandes": "大型模块（`nucleo`、`tabla_hermite`）有数百个单元。PDF 为矢量图，\n"
        "放大后细节不会丢失。",
        "regenerar": "## 重新生成",
        "pasos": [
            "安装一次 netlistsvg：`cd herramientas/esquematicos && npm install`。",
            "运行 `.venv/bin/python scripts/esquematicos.py`，只会重新生成有变化的原理图。",
            "`--comprobar` 列出已过时的原理图。",
        ],
        "indice": "## 索引",
        "cabecera": "| PDF | 源文件 | 源文件 sha256 | 说明 |",
        "nota": "PDF 的标题栏和本表中的说明来自 Verilog 注释，为西班牙语。",
    },
    "ja": {
        "titulo": "# RTL の回路図",
        "intro": "`rtl/` の各モジュールに 1 つの PDF を、電子回路の記号で用意しています。Yosys と\n"
        "netlistsvg が Verilog から生成し、手では描きません（ADR 0012、スペイン語）。",
        "leer": "## 読み方",
        "simbolos": [
            "**`+`、`-`、`*`、`<`、`==` の付いた台形：** 加算器、減算器、乗算器、比較器。",
            "**複数の入力と 1 つの選択を持つ台形：** マルチプレクサー（`$mux`、`$pmux`）。",
            "**クロックに三角形の付いた長方形：** フリップフロップまたはレジスター（`$dff`、`$adff`、`$sdff`）。",
            "**AND、OR、XOR、NOT ゲート：** 1 ビットの論理。標準の記号です。",
            "**モジュール名の付いた長方形：** サブモジュール。専用の PDF があります。",
            "**左右の矢印：** モジュールの入力ポートと出力ポート。",
        ],
        "grandes": "大きなモジュール（`nucleo`、`tabla_hermite`）には数百のセルがあります。PDF は\n"
        "ベクター形式なので、拡大しても細部は失われません。",
        "regenerar": "## 再生成",
        "pasos": [
            "netlistsvg を 1 回だけインストールします：`cd herramientas/esquematicos && npm install`。",
            "`.venv/bin/python scripts/esquematicos.py` を実行します。変更のあったものだけを再生成します。",
            "`--comprobar` は古くなった回路図を表示します。",
        ],
        "indice": "## 索引",
        "cabecera": "| PDF | ソース | ソースの sha256 | 内容 |",
        "nota": "PDF の表題欄とこの表の説明は Verilog のコメントから取ったもので、スペイン語です。",
    },
}


def _indice(lista: list[Modulo], idioma: str = "es") -> str:
    t = _GUIA[idioma]
    filas = "\n".join(
        f"| `{m.pdf.relative_to(DESTINO)}` | `{m.fuente.relative_to(RAIZ)}` | `{m.sha}` "
        f"| {m.descripcion} |"
        for m in lista
    )
    simbolos = "\n".join(f"- {x}" for x in t["simbolos"])
    pasos = "\n".join(f"{k}. {x}" for k, x in enumerate(t["pasos"], start=1))
    nota = f"\n{t['nota']}\n" if t["nota"] else ""
    return (
        "<!-- GENERADO por scripts/esquematicos.py. No se edita a mano. -->\n\n"
        f"{t['titulo']}\n\n{t['intro']}\n\n{t['leer']}\n\n{simbolos}\n\n{t['grandes']}\n\n"
        f"{t['regenerar']}\n\n{pasos}\n\n{t['indice']}\n{nota}\n{t['cabecera']}\n|---|---|---|---|\n"
        f"{filas}\n"
    )


def _indices(lista: list[Modulo]) -> dict[Path, str]:
    """Las cuatro guías (ADR 0007); las traducciones llevan el sello del índice español."""
    es = _indice(lista, "es")
    sha = hashlib.sha256(es.encode("utf-8")).hexdigest()[:12]
    res = {INDICE: es}
    for idioma in ("en", "zh-CN", "ja"):
        sello = f"<!-- i18n: fuente=schematics/README.md sha={sha} estado=al_dia -->\n"
        res[DESTINO / f"README.{idioma}.md"] = sello + _indice(lista, idioma)
    return res


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--todos", action="store_true", help="regenera todos")
    p.add_argument("--comprobar", action="store_true", help="solo comprueba")
    args = p.parse_args()
    lista = modulos()
    sellos = {}
    if INDICE.exists():
        sellos = {m["pdf"]: m["sha"] for m in _SELLO.finditer(INDICE.read_text(encoding="utf-8"))}
    viejos = [
        m
        for m in lista
        if args.todos or not m.pdf.exists() or sellos.get(str(m.pdf.relative_to(DESTINO))) != m.sha
    ]
    if args.comprobar:
        for m in viejos:
            print(f"esquemáticos: desactualizado {m.pdf.relative_to(RAIZ)}")
        print(f"esquemáticos: {len(lista) - len(viejos)} de {len(lista)} al día")
        return 1 if viejos else 0
    if not NETLISTSVG.exists() or not CHROME:
        print(
            "esquemáticos: falta netlistsvg (npm install) o chrome-headless-shell", file=sys.stderr
        )
        return 1
    for m in viejos:
        _pdf(m, _svg(m))
        print(f"{m.nombre} → {m.pdf.relative_to(RAIZ)}")
    for ruta, texto in _indices(lista).items():
        ruta.write_text(texto, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
