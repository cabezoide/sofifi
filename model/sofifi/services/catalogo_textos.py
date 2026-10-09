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
    "aceite": ("oil", "油", "オイル"),
    "afinación": ("tuning", "调音", "チューニング"),
    "ancho": ("width", "宽度", "幅"),
    "apertura": ("bloom time", "绽放时间", "開く時間"),
    "arranque": ("spin-up time", "启动时间", "始動時間"),
    "bits": ("bits", "位数", "ビット"),
    "cabezas": ("heads", "磁头", "ヘッド"),
    "cantidad de shimmer": ("shimmer amount", "shimmer 量", "シマー量"),
    "capas": ("layers", "层叠", "レイヤー"),
    "captura": ("capture", "捕捉", "キャプチャー"),
    "ciclo": ("duty cycle", "占空比", "デューティ比"),
    "cierre": ("release", "释放", "リリース"),
    "compresión": ("compression", "压缩", "圧縮"),
    "cruce": ("crossfeed", "交叉混合", "クロスフィード"),
    "damping": ("damping", "阻尼", "ダンピング"),
    "decay": ("decay", "衰减", "ディケイ"),
    "densidad": ("density", "密度", "密度"),
    "deriva": ("drift", "漂移", "ドリフト"),
    "desafinación": ("detune", "失谐", "デチューン"),
    "desplazamiento": ("frequency shift", "移频", "周波数シフト"),
    "difusión": ("diffusion", "扩散", "拡散"),
    "dispersión": ("spread", "离散度", "広がり"),
    "ducking": ("ducking", "闪避", "ダッキング"),
    "duración": ("length", "时长", "長さ"),
    "eco": ("echo", "回声", "エコー"),
    "edad": ("age", "老化", "エイジング"),
    "ensemble": ("ensemble", "合奏", "アンサンブル"),
    "equilibrio": ("balance", "平衡", "バランス"),
    "erosión": ("erosion", "侵蚀", "侵食"),
    "excitación": ("excitation", "激励", "励起"),
    "forma": ("shape", "波形", "波形"),
    "frecuencia": ("frequency", "频率", "周波数"),
    "frenada": ("brake time", "制动时间", "ブレーキ時間"),
    "ganancia": ("gain", "增益", "ゲイン"),
    "giro": ("rotation", "旋转", "回転"),
    "glide": ("glide", "滑音", "グライド"),
    "inclinación": ("slope", "斜率", "傾き"),
    "intervalo": ("interval", "音程", "音程"),
    "mezcla": ("mix", "干湿比", "ミックス"),
    "modo": ("mode", "模式", "モード"),
    "modulación": ("modulation", "调制", "モジュレーション"),
    "muestreo": ("sample rate", "采样率", "サンプリング周波数"),
    "nivel": ("level", "电平", "レベル"),
    "notas": ("notes", "音数", "音数"),
    "octava alta": ("upper octave", "高八度", "上のオクターブ"),
    "octava baja": ("lower octave", "低八度", "下のオクターブ"),
    "panorama": ("pan", "声像", "パン"),
    "probabilidad": ("probability", "概率", "確率"),
    "profundidad": ("depth", "深度", "深さ"),
    "proporción": ("ratio", "比例", "比率"),
    "puerta": ("low-pass gate", "低通门", "ローパスゲート"),
    "realimentación": ("feedback", "反馈", "フィードバック"),
    "repeticiones": ("repeats", "重复次数", "リピート回数"),
    "resonancia": ("resonance", "谐振", "レゾナンス"),
    "saturación": ("saturation", "饱和", "サチュレーション"),
    "seco": ("dry", "干声", "ドライ"),
    "segunda toma": ("second tap", "第二抽头", "セカンドタップ"),
    "segunda voz": ("second voice", "第二声部", "第2声部"),
    "semilla": ("seed", "种子", "シード"),
    "sensibilidad": ("sensitivity", "灵敏度", "感度"),
    "sentido": ("direction", "方向", "方向"),
    "suavizado": ("smoothing", "平滑", "スムージング"),
    "subdivisión": ("subdivision", "细分", "音符分割"),
    "subida": ("rise time", "上升时间", "立ち上がり"),
    "suciedad": ("dirt", "脏污", "汚れ"),
    "sustain": ("sustain", "延音", "サステイン"),
    "tiempo": ("time", "时间", "タイム"),
    "tilt": ("tilt", "倾斜", "チルト"),
    "tono": ("tone", "音色", "トーン"),
    "umbral": ("threshold", "阈值", "スレッショルド"),
    "vaciado": ("release", "释放", "リリース"),
    "velocidad": ("rate", "速度", "速さ"),
    "vibrato": ("vibrato", "颤音", "ビブラート"),
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
        "cadenas_titulo": "## Cadenas",
        "cadenas_intro": "Una cadena une dos programas en uno, en serie (→) o en paralelo (‖), "
        "sin cambiar el RTL (ADR 0013). Están en `presets/cadenas.toml`; `sofifi cadena` las procesa. "
        "{n} caben hoy y {s} esperan la SDRAM: solo les falta memoria.",
        "cadenas_cabecera": "| Cadena | Programas | Ciclos | Memoria | Registros | LFOs | Estado |",
        "cabe": "cabe",
        "sdram": "espera la SDRAM",
    },
    "en": {
        "titulo": "# Core programs",
        "total": "{n} programs and {p} presets. Each program is a text file in `programas/`; "
        "the presets are in `presets/banco.toml`. Program and preset names are in Spanish.",
        "coste": "The cycles are the RTL upper limit, of {c} per sample (`model/sofifi/domain/coste.py`). "
        "The memory has {m} words.",
        "cabecera": "| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |",
        "cadenas_titulo": "## Chains",
        "cadenas_intro": "A chain joins two programs into one, in series (→) or in parallel (‖), "
        "with no change to the RTL (ADR 0013, Spanish). The chains are in `presets/cadenas.toml`; "
        "`sofifi cadena` processes them. {n} fit today and {s} wait for the SDRAM: they only need memory.",
        "cadenas_cabecera": "| Chain | Programs | Cycles | Memory | Registers | LFOs | Status |",
        "cabe": "fits",
        "sdram": "waits for the SDRAM",
    },
    "zh-CN": {
        "titulo": "# 核心程序",
        "total": "{n} 个程序与 {p} 个预设。每个程序都是 `programas/` 中的一个文本文件；"
        "预设位于 `presets/banco.toml`。程序名与预设名为西班牙语。",
        "coste": "周期数为 RTL 的上限，每个样本 {c} 个（`model/sofifi/domain/coste.py`）。"
        "存储器共 {m} 个字。",
        "cabecera": "| 程序 | 作用 | 旋钮 | 预设 | 指令数 | 周期 | 存储器 |",
        "cadenas_titulo": "## 链",
        "cadenas_intro": "链把两个程序合成一个，串联（→）或并联（‖），不改动 RTL（ADR 0013，西班牙语）。"
        "链位于 `presets/cadenas.toml`；用 `sofifi cadena` 处理。今天有 {n} 条可以装入，{s} 条等待 SDRAM：它们只缺存储器。",
        "cadenas_cabecera": "| 链 | 程序 | 周期 | 存储器 | 寄存器 | LFO | 状态 |",
        "cabe": "可装入",
        "sdram": "等待 SDRAM",
    },
    "ja": {
        "titulo": "# コアのプログラム",
        "total": "{n} のプログラムと {p} のプリセット。各プログラムは `programas/` のテキストファイルで、"
        "プリセットは `presets/banco.toml` にあります。プログラム名とプリセット名はスペイン語です。",
        "coste": "サイクル数は RTL の上限で、1 サンプルあたり {c}（`model/sofifi/domain/coste.py`）。"
        "メモリーは {m} ワードです。",
        "cabecera": "| プログラム | 働き | ノブ | プリセット | 命令数 | サイクル | メモリー |",
        "cadenas_titulo": "## チェーン",
        "cadenas_intro": "チェーンは 2 つのプログラムを直列（→）または並列（‖）で 1 つにまとめます。"
        "RTL は変えません（ADR 0013、スペイン語）。チェーンは `presets/cadenas.toml` にあり、"
        "`sofifi cadena` で処理します。現在 {n} 本が収まり、{s} 本は SDRAM を待っています：足りないのはメモリーだけです。",
        "cadenas_cabecera": "| チェーン | プログラム | サイクル | メモリー | レジスタ | LFO | 状態 |",
        "cabe": "収まる",
        "sdram": "SDRAM 待ち",
    },
}
