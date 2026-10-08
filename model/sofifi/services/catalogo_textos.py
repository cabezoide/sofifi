# SPDX-License-Identifier: MIT
# ruff: noqa: E501 — tablas de traducción: partir las frases las haría ilegibles
"""Textos del catálogo en los cuatro idiomas (ADR 0007): títulos, familias y mandos.

El español es la fuente. Los resúmenes de cada programa no están aquí: salen de
la cabecera de cada ``.sasm`` (``; resumen.en:``, ``; resumen.zh-CN:``, ``; resumen.ja:``).
"""

from __future__ import annotations

IDIOMAS = ("es", "en", "zh-CN", "ja")

FAMILIAS: dict[str, tuple[str, str, str, str]] = {
    "reverb": ("Reverb", "Reverb", "混响", "リバーブ"),
    "delay": ("Delay", "Delay", "延迟", "ディレイ"),
    "modulación": ("Modulación", "Modulation", "调制", "モジュレーション"),
    "pitch": ("Pitch", "Pitch", "音高", "ピッチ"),
    "dinámica": ("Dinámica", "Dynamics", "动态", "ダイナミクス"),
    "textura": ("Textura", "Texture", "质感", "テクスチャー"),
    "filtro": ("Filtro", "Filter", "滤波", "フィルター"),
    "looper": ("Looper", "Looper", "循环器", "ルーパー"),
}

MANDOS: dict[str, tuple[str, str, str]] = {
    "afinación": ("tuning", "调音", "チューニング"),
    "ancho": ("width", "宽度", "幅"),
    "apertura": ("bloom time", "绽放时间", "開く時間"),
    "bits": ("bits", "位数", "ビット"),
    "cantidad de shimmer": ("shimmer amount", "shimmer 量", "シマー量"),
    "ciclo": ("duty cycle", "占空比", "デューティ比"),
    "cierre": ("release", "释放", "リリース"),
    "compresión": ("compression", "压缩", "圧縮"),
    "damping": ("damping", "阻尼", "ダンピング"),
    "decay": ("decay", "衰减", "ディケイ"),
    "desafinación": ("detune", "失谐", "デチューン"),
    "difusión": ("diffusion", "扩散", "拡散"),
    "ducking": ("ducking", "闪避", "ダッキング"),
    "duración": ("length", "时长", "長さ"),
    "excitación": ("excitation", "激励", "励起"),
    "frecuencia": ("frequency", "频率", "周波数"),
    "ganancia": ("gain", "增益", "ゲイン"),
    "giro": ("rotation", "旋转", "回転"),
    "intervalo": ("interval", "音程", "音程"),
    "mezcla": ("mix", "干湿比", "ミックス"),
    "modulación": ("modulation", "调制", "モジュレーション"),
    "muestreo": ("sample rate", "采样率", "サンプリング周波数"),
    "nivel": ("level", "电平", "レベル"),
    "octava alta": ("upper octave", "高八度", "上のオクターブ"),
    "octava baja": ("lower octave", "低八度", "下のオクターブ"),
    "panorama": ("pan", "声像", "パン"),
    "profundidad": ("depth", "深度", "深さ"),
    "realimentación": ("feedback", "反馈", "フィードバック"),
    "resonancia": ("resonance", "谐振", "レゾナンス"),
    "seco": ("dry", "干声", "ドライ"),
    "sentido": ("direction", "方向", "方向"),
    "sensibilidad": ("sensitivity", "灵敏度", "感度"),
    "suavizado": ("smoothing", "平滑", "スムージング"),
    "subida": ("rise time", "上升时间", "立ち上がり"),
    "sustain": ("sustain", "延音", "サステイン"),
    "tiempo": ("time", "时间", "タイム"),
    "tilt": ("tilt", "倾斜", "チルト"),
    "tono": ("tone", "音色", "トーン"),
    "umbral": ("threshold", "阈值", "スレッショルド"),
    "vaciado": ("release", "释放", "リリース"),
    "velocidad": ("rate", "速度", "速さ"),
    "vida": ("life", "生动度", "ゆらぎ"),
    "vocal": ("vowel", "元音", "母音"),
    "wow y flutter": ("wow and flutter", "wow 与 flutter", "ワウとフラッター"),
}

# Textos fijos por idioma: (título, frase con el total, presets, ciclos, columnas).
TEXTOS: dict[str, dict[str, str]] = {
    "es": {
        "titulo": "# Programas del núcleo",
        "total": "{n} programas y {p} presets. Cada programa es un fichero de texto en `programas/`; "
        "los presets están en `presets/banco.toml`.",
        "coste": "Los ciclos son la cota del RTL, de {c} por muestra (`model/sofifi/domain/coste.py`). "
        "La memoria es de {m} palabras.",
        "cabecera": "| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |",
    },
    "en": {
        "titulo": "# Core programs",
        "total": "{n} programs and {p} presets. Each program is a text file in `programas/`; "
        "the presets are in `presets/banco.toml`. Program and preset names are in Spanish.",
        "coste": "The cycles are the RTL upper limit, of {c} per sample (`model/sofifi/domain/coste.py`). "
        "The memory has {m} words.",
        "cabecera": "| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |",
    },
    "zh-CN": {
        "titulo": "# 核心程序",
        "total": "{n} 个程序与 {p} 个预设。每个程序都是 `programas/` 中的一个文本文件；"
        "预设位于 `presets/banco.toml`。程序名与预设名为西班牙语。",
        "coste": "周期数为 RTL 的上限，每个样本 {c} 个（`model/sofifi/domain/coste.py`）。"
        "存储器共 {m} 个字。",
        "cabecera": "| 程序 | 作用 | 旋钮 | 预设 | 指令数 | 周期 | 存储器 |",
    },
    "ja": {
        "titulo": "# コアのプログラム",
        "total": "{n} のプログラムと {p} のプリセット。各プログラムは `programas/` のテキストファイルで、"
        "プリセットは `presets/banco.toml` にあります。プログラム名とプリセット名はスペイン語です。",
        "coste": "サイクル数は RTL の上限で、1 サンプルあたり {c}（`model/sofifi/domain/coste.py`）。"
        "メモリーは {m} ワードです。",
        "cabecera": "| プログラム | 働き | ノブ | プリセット | 命令数 | サイクル | メモリー |",
    },
}
