# SPDX-License-Identifier: MIT
"""Regenera ``demo_examples/``: una guitarra sintética y su paso por cada programa y cadena.

La guitarra es un arpegio de Em9 con cuerdas Karplus-Strong y semilla fija. El
núcleo es bit-exact y no hay remuestreo (la señal ya está a 48 828 Hz), así que
el audio es determinista.

Las demos se guardan en Ogg Vorbis (ADR 0001, actualización): unas 10 veces
menos que un WAV. El códec da el mismo audio cada vez, pero el fichero cambia
en su número de serie. Por eso un ``.ogg`` solo se reescribe si su audio cambia:
regenerar sin cambios no toca git.

Uso: ``.venv/bin/python scripts/generar_demos.py`` (unos 2 min en 8 núcleos;
necesita ``pip install -e '.[demos]'``). Con ``--readme`` solo escribe las guías
``demo_examples/README*.md``, en cuatro idiomas.
"""

from __future__ import annotations

import hashlib
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import soundfile  # type: ignore[import-untyped]
from sofifi.adapters.archivos import ensamblar_archivo
from sofifi.adapters.cadenas import leer_cadenas, textos_de_programas
from sofifi.adapters.wav import a_pcm16
from sofifi.domain.aritmetica import DATO_MAX, DATO_MIN, FS_WAV, dato
from sofifi.domain.cadena import Cadena, Modo
from sofifi.domain.composicion import ensamblar_cadena, nombre_programa
from sofifi.domain.senal import Controles, Senal
from sofifi.services.catalogo import ficha, mando_traducido
from sofifi.services.render import procesar

ROOT = Path(__file__).resolve().parent.parent
DESTINO = ROOT / "demo_examples"
NOTAS_HZ = (82.41, 123.47, 164.81, 185.00, 246.94, 293.66, 369.99)  # Em9
SEPARACION_S = 0.22
DURACION_S = 4.0
SEMILLA = 7

# (programa, pots, tramos de freeze en segundos, cola en segundos)
DEMOS: tuple[tuple[str, dict[int, str], tuple[tuple[float, float], ...], float], ...] = (
    ("plate", {0: "0.7", 1: "0.3", 2: "0.45"}, (), 4.0),
    ("shimmer", {0: "0.75", 1: "0.25", 2: "0.55", 3: "0.6"}, (), 6.0),
    ("freeze", {0: "0.6", 1: "0.3", 2: "0.5"}, ((2.5, 8.0),), 6.0),
    ("hall", {0: "0.75", 1: "0.35", 2: "0.45"}, (), 5.0),
    ("cloud", {0: "0.7", 1: "0.3", 2: "0.55", 3: "0.6"}, (), 6.0),
    ("cinta", {0: "0.45", 1: "0.55", 2: "0.4", 3: "0.5"}, (), 5.0),
    ("reverse", {0: "0.6", 1: "0.4", 2: "0.5"}, (), 3.0),
    ("lofi", {0: "0.6", 1: "0.7", 2: "0.7", 3: "0.4"}, (), 1.0),
    ("swell", {0: "0.7", 1: "0.3", 2: "0.5", 3: "0.4"}, (), 4.0),
    ("chorus", {0: "0.3", 1: "0.6", 2: "0.5"}, (), 1.0),
    ("flanger", {0: "0.15", 1: "0.8", 2: "0.5", 3: "0.6"}, (), 1.0),
    ("phaser", {0: "0.2", 1: "0.9", 2: "0.5", 3: "0.5"}, (), 1.0),
    ("tremolo", {0: "0.3", 1: "0.7", 2: "0.6"}, (), 1.0),
    ("vibrato", {0: "0.4", 1: "0.5", 2: "1"}, (), 1.0),
    ("octava", {0: "0.6", 1: "0.4", 2: "0.8"}, (), 1.0),
    ("armonizador", {0: "0.75", 1: "0.3", 2: "0.45"}, (), 2.0),
    ("doblador", {0: "0.5", 2: "0.5"}, (), 1.0),
    ("escalera", {0: "0.95", 1: "0.6", 2: "0.45", 3: "0.4"}, (), 4.0),
    ("shimmer_quinta", {0: "0.75", 1: "0.25", 2: "0.55", 3: "0.6"}, (), 6.0),
    ("blackhole", {0: "0.85", 1: "0.35", 2: "0.5"}, (), 8.0),
    ("bloom", {0: "0.8", 1: "0.3", 2: "0.55", 3: "0.4"}, (), 5.0),
    ("gated", {0: "0.8", 1: "0.2", 2: "0.5", 3: "0.5"}, (), 1.0),
    ("infinite", {0: "0.1", 1: "0.3", 2: "0.45"}, (), 6.0),
    ("reverb_inversa", {0: "0.8", 1: "0.3", 2: "0.55", 3: "0.6"}, (), 1.0),
    ("spring", {0: "0.6", 1: "0.4", 2: "0.4"}, (), 3.0),
    ("delay", {0: "0.55", 1: "0.45", 2: "0.4", 3: "0.7"}, (), 4.0),
    ("pingpong", {0: "0.7", 1: "0.5", 2: "0.45"}, (), 4.0),
    ("lluvia", {0: "0.7", 1: "0.4", 2: "0.5"}, (), 4.0),
    ("bbd", {0: "0.6", 1: "0.6", 2: "0.45", 3: "0.5"}, (), 4.0),
    ("ducking", {0: "0.45", 1: "0.5", 2: "0.5", 3: "0.8"}, (), 4.0),
    ("autowah", {0: "0.8", 1: "0.6", 2: "0.8"}, (), 1.0),
    ("compresor", {0: "0.3", 1: "0.8", 2: "1", 3: "0.4"}, (), 1.0),
    ("filtro", {0: "0.25", 1: "0.6", 2: "0.9", 3: "0.8"}, (), 1.0),
    ("puerta", {0: "0.2", 1: "0.4"}, (), 1.0),
    ("saturacion", {0: "0.6", 1: "0.5", 2: "1", 3: "0.7"}, (), 1.0),
    ("ringmod", {0: "0.15", 2: "0.6"}, (), 1.0),
    ("slicer", {0: "0.3", 1: "0.9", 2: "0.4", 3: "0.4"}, (), 1.0),
    ("ancho", {0: "0.8", 1: "0.6"}, (), 1.0),
    ("chorale", {0: "0.75", 1: "0.3", 2: "0.55", 3: "0.3"}, (), 6.0),
    ("resonador", {0: "0.8", 1: "0.7", 2: "0.5"}, (), 4.0),
    ("plate_vivo", {0: "0.75", 1: "0.3", 2: "0.45", 3: "1"}, (), 5.0),
    ("shimmer_energia", {0: "0.8", 1: "0.25", 2: "0.55", 3: "0.9"}, (), 6.0),
    ("freeze_givens", {0: "0.6", 1: "0.3", 2: "0.5", 3: "0.6"}, ((2.5, 8.0),), 6.0),
    # Graba las tres primeras notas, deja sonar el loop y hace un overdub.
    ("looper", {0: "0.8", 1: "0.5", 2: "0", 3: "0.8"}, ((0.0, 0.66), (1.32, 1.98)), 3.0),
    # Nube una octava arriba; el búfer se congela con el arpegio dentro.
    ("granular", {0: "0.6", 1: "0.5", 2: "1", 3: "0.6"}, ((1.6, 7.0),), 3.0),
    ("shimmer_grave", {0: "0.75", 1: "0.3", 2: "0.5", 3: "0.6"}, (), 6.0),
    ("marea", {0: "0.8", 1: "0.3", 2: "0.5", 3: "0.2"}, (), 6.0),
    ("ensemble", {0: "0.75", 1: "0.3", 2: "0.5", 3: "0.7"}, (), 5.0),
    # Cada nota del arpegio vuelve a capturar; tras la última, el acorde queda sonando.
    ("sostenido", {0: "0.2", 1: "0.3", 2: "0.5", 3: "0.3"}, (), 6.0),
    ("shoegaze", {0: "0.85", 1: "0.3", 2: "0.55", 3: "0.8"}, (), 5.0),
    ("bruma", {0: "0.7", 1: "0.55", 2: "0.5", 3: "1"}, (), 5.0),
    ("armonico", {0: "0.3", 1: "0.75", 2: "0.35", 3: "0.5", 4: "0.1", 5: "0.8"}, (), 1.0),
    ("arcoiris", {0: "0.79", 1: "0", 2: "0.5", 3: "0.3", 4: "0.75", 5: "0.6"}, ((2.5, 4.0),), 5.0),
    ("tambor", {0: "0.55", 1: "0.5", 2: "0.45", 3: "0.85", 4: "0.4", 5: "0.6"}, ((3.5, 5.0),), 5.0),
    ("mosaico", {0: "0.6", 1: "0.7", 2: "0.55", 3: "0.5", 4: "0.85", 5: "0.6"}, ((4.0, 8.0),), 6.0),
    # Graba el arpegio entero y lo deja desgastarse vuelta a vuelta hasta la niebla.
    ("erosion", {0: "0.25", 1: "0.6", 2: "0.65", 3: "0.7", 4: "1", 5: "1"}, ((0.0, 0.67),), 6.0),
    ("desplazador", {0: "0.75", 1: "0.45", 2: "0.5", 3: "0.85", 4: "0.7", 5: "0.5"}, (), 6.0),
)
# Cadenas del banco (presets/cadenas.toml, ADR 0013), con sus pots: (nombre, cola en segundos).
DEMOS_CADENAS: tuple[tuple[str, float], ...] = (
    ("Eco y muelle", 4.0),
    ("Flor al revés", 5.0),
    ("Órgano infinito", 6.0),
    ("Shimmer con vibrato", 6.0),
    ("Cuerdas en ola", 6.0),
    ("Fuzz en la nube", 5.0),
)
# Calidad de Vorbis: 0 es la mejor. Con 0,3, una demo de 8 s ocupa unos 190 kB.
COMPRESION = 0.3


def guitarra() -> Senal:
    rng = np.random.default_rng(SEMILLA)
    y = np.zeros(int(FS_WAV * DURACION_S))
    for i, f in enumerate(NOTAS_HZ):
        inicio = int(i * SEPARACION_S * FS_WAV)
        periodo = int(FS_WAV / f)
        cuerda = rng.uniform(-1, 1, periodo)
        salida = np.zeros(len(y) - inicio)
        for k in range(len(salida)):
            j = k % periodo
            salida[k] = cuerda[j]
            cuerda[j] = 0.996 * 0.5 * (cuerda[j] + cuerda[(k + 1) % periodo])
        y[inicio:] += 0.12 * salida
    # Cuantizada a 16 bit (como una grabación típica) y alineada a S.23.
    pcm16 = np.trunc(np.clip(y, -1, 1) * 32767).astype(np.int64)
    muestras = np.clip(pcm16 << 8, DATO_MIN, DATO_MAX)
    return Senal(FS_WAV, (tuple(int(v) for v in muestras),))


def escribir_ogg(ruta: Path, senal: Senal) -> bool:
    """Escribe ``ruta`` si su audio cambia. Devuelve True si la ha escrito."""
    with tempfile.TemporaryDirectory() as tmp:
        nuevo = Path(tmp) / ruta.name
        soundfile.write(
            nuevo,
            a_pcm16(senal),
            senal.fs_hz,
            format="OGG",
            subtype="VORBIS",
            compression_level=COMPRESION,
        )
        if ruta.exists():
            antes = soundfile.read(ruta, dtype="int16")[0]
            despues = soundfile.read(nuevo, dtype="int16")[0]
            if antes.shape == despues.shape and np.array_equal(antes, despues):
                return False
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_bytes(nuevo.read_bytes())
    return True


def _demo(demo: tuple[str, dict[int, str], tuple[tuple[float, float], ...], float]) -> str:
    """Renderiza una demo y la escribe si su audio cambió. Corre en un proceso aparte."""
    nombre, pots, tramos, cola = demo
    controles = Controles(
        tuple(dato(pots.get(i, "0")) for i in range(6)),
        tuple((round(a * FS_WAV), round(b * FS_WAV)) for a, b in tramos),
    )
    programa = ensamblar_archivo(ROOT / "programas" / f"{nombre}.sasm")
    salida = procesar(programa, guitarra(), controles, round(cola * FS_WAV))
    destino = DESTINO / f"demo_{nombre}.ogg"
    escrita = escribir_ogg(destino, salida)
    return f"{nombre} → {destino.relative_to(ROOT)}" + ("" if escrita else " (igual)")


def _cadenas() -> dict[str, Cadena]:
    return {c.nombre: c for c in leer_cadenas(ROOT / "presets" / "cadenas.toml")}


def _demo_cadena(demo: tuple[str, float]) -> str:
    """Como ``_demo``, para una cadena del banco con los pots que trae."""
    nombre, cola = demo
    cadena = _cadenas()[nombre]
    carpeta = ROOT / "programas"
    programa = ensamblar_cadena(
        cadena, textos_de_programas(carpeta), lambda n: (carpeta / n).read_text(encoding="utf-8")
    )
    controles = Controles(tuple(dato(v) for v in cadena.posiciones))
    salida = procesar(programa, guitarra(), controles, round(cola * FS_WAV))
    destino = DESTINO / f"demo_{nombre_programa(cadena)}.ogg"
    escrita = escribir_ogg(destino, salida)
    return f"{nombre} → {destino.relative_to(ROOT)}" + ("" if escrita else " (igual)")


GUIA = {
    "es": (
        "Una guitarra sintética (arpegio de Em9, cuerdas Karplus-Strong) procesada por cada "
        "programa del núcleo con el modelo bit-exact. Se regeneran con "
        "`.venv/bin/python scripts/generar_demos.py`: el audio sale igual cada vez.",
        "| Fichero | Programa | Mandos | Footswitch |",
        "Ogg Vorbis a 48 828 Hz (ADR 0005); el render es bit-exact en 24 bit. "
        "Los mandos y los programas están en `docs/programas.md`.",
    ),
    "en": (
        "A synthetic guitar (an Em9 arpeggio, Karplus-Strong strings) through each core program, "
        "with the bit-exact model. Generate them again with "
        "`.venv/bin/python scripts/generar_demos.py`: the audio is the same each time.",
        "| File | Program | Knobs | Footswitch |",
        "Ogg Vorbis at 48,828 Hz (ADR 0005, Spanish); the render is bit-exact at 24 bits. "
        "The knobs and the programs are in `docs/programas.en.md`.",
    ),
    "zh-CN": (
        "一段合成吉他（Em9 琶音，Karplus-Strong 弦模型）经内核的每个程序处理，使用逐位精确模型。"
        "可用 `.venv/bin/python scripts/generar_demos.py` 重新生成，每次得到的音频都相同。",
        "| 文件 | 程序 | 旋钮 | 脚踏开关 |",
        "Ogg Vorbis，48,828 Hz（ADR 0005，西班牙语）；渲染在 24 位下逐位精确。"
        "旋钮与程序见 `docs/programas.zh-CN.md`。",
    ),
    "ja": (
        "合成ギター（Em9 のアルペジオ、Karplus-Strong の弦）を、"
        "ビット精度のモデルでコアの各プログラムに通したものです。"
        "`.venv/bin/python scripts/generar_demos.py` で再生成でき、"
        "毎回同じ音声になります。",
        "| ファイル | プログラム | ノブ | フットスイッチ |",
        "Ogg Vorbis、48,828 Hz（ADR 0005、スペイン語）。レンダリングは 24 ビットでビット精度です。"
        "ノブとプログラムは `docs/programas.ja.md` にあります。",
    ),
}


def _decimal(v: str, idioma: str) -> str:
    texto = f"{float(v):.2f}"
    return texto.replace(".", ",") if idioma == "es" else texto


def guias() -> dict[Path, str]:
    """``demo_examples/README*.md`` en cuatro idiomas, desde ``DEMOS`` y el catálogo (ADR 0007)."""
    fichas = {
        n: ficha(
            n,
            (ROOT / "programas" / f"{n}.sasm").read_text(encoding="utf-8"),
            ensamblar_archivo(ROOT / "programas" / f"{n}.sasm"),
        )
        for n, *_ in DEMOS
    }
    textos: dict[str, str] = {}
    for idioma, (intro, cabecera, pie) in GUIA.items():
        filas = ["| `demo_guitarra.ogg` | — | — | — |"]
        for nombre, pots, tramos, _ in DEMOS:
            etiquetas = dict(m.split(": ", 1) for m in fichas[nombre].mandos)
            mandos = " · ".join(
                f"{mando_traducido(f'{k}: {etiquetas[str(k)]}', idioma).split(': ', 1)[1]} "
                f"{_decimal(v, idioma)}"
                for k, v in sorted(pots.items())
                if str(k) in etiquetas
            )
            pulsador = ", ".join(
                f"{_decimal(str(a), idioma)} → {_decimal(str(b), idioma)} s" for a, b in tramos
            )
            filas.append(f"| `demo_{nombre}.ogg` | `{nombre}` | {mandos} | {pulsador or '—'} |")
        cadenas = _cadenas()
        for nombre, _ in DEMOS_CADENAS:
            c = cadenas[nombre]
            union = " → " if c.modo is Modo.SERIE else " ‖ "
            programas = union.join(f"`{e.programa}`" for e in c.eslabones)
            posiciones = " · ".join(
                f"pot{k} {_decimal(str(float(v)), idioma)}" for k, v in enumerate(c.posiciones)
            )
            filas.append(
                f"| `demo_{nombre_programa(c)}.ogg` | {nombre}: {programas} | {posiciones} | — |"
            )
        textos[idioma] = "\n".join(
            ["# demo_examples", "", intro, "", cabecera, "|---|---|---|---|", *filas, "", pie, ""]
        )
    sha = hashlib.sha256(textos["es"].encode("utf-8")).hexdigest()[:12]
    res = {DESTINO / "README.md": textos["es"]}
    for idioma in ("en", "zh-CN", "ja"):
        sello = f"<!-- i18n: fuente=demo_examples/README.md sha={sha} estado=al_dia -->\n"
        res[DESTINO / f"README.{idioma}.md"] = sello + textos[idioma]
    return res


def main() -> int:
    for ruta, texto in guias().items():
        ruta.write_text(texto, encoding="utf-8")
    if sys.argv[1:] == ["--readme"]:
        return 0
    seca = guitarra()
    destino = DESTINO / "demo_guitarra.ogg"
    print(
        f"seca → {destino.relative_to(ROOT)}" + ("" if escribir_ogg(destino, seca) else " (igual)")
    )
    # Un proceso por núcleo: cada demo es independiente y el modelo usa un solo núcleo.
    with ProcessPoolExecutor() as procesos:
        for linea in procesos.map(_demo, DEMOS):
            print(linea)
        for linea in procesos.map(_demo_cadena, DEMOS_CADENAS):
            print(linea)
    return 0


if __name__ == "__main__":
    sys.exit(main())
