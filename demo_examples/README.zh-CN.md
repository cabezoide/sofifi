<!-- i18n: fuente=demo_examples/README.md sha=652d4c2773fe estado=al_dia -->
# demo_examples

一段合成吉他（Em9 琶音，Karplus-Strong 弦模型）经内核的每个程序处理，使用逐位精确模型。可用 `.venv/bin/python scripts/generar_demos.py` 重新生成，每次得到的音频都相同。

| 文件 | 程序 | 旋钮 | 脚踏开关 |
|---|---|---|---|
| `demo_guitarra.ogg` | — | — | — |
| `demo_plate.ogg` | `plate` | 衰减 0.70 · 阻尼 0.30 · 干湿比 0.45 | — |
| `demo_shimmer.ogg` | `shimmer` | 衰减 0.75 · 阻尼 0.25 · 干湿比 0.55 · shimmer 量 0.60 | — |
| `demo_freeze.ogg` | `freeze` | 衰减 0.60 · 阻尼 0.30 · 干湿比 0.50 | 2.50 → 8.00 s |
| `demo_hall.ogg` | `hall` | 衰减 0.75 · 阻尼 0.35 · 干湿比 0.45 | — |
| `demo_cloud.ogg` | `cloud` | 衰减 0.70 · 阻尼 0.30 · 干湿比 0.55 · 调制 0.60 | — |
| `demo_cinta.ogg` | `cinta` | 时间 0.45 · 反馈 0.55 · 干湿比 0.40 · wow 与 flutter 0.50 | — |
| `demo_reverse.ogg` | `reverse` | 音色 0.60 · 反馈 0.40 · 干湿比 0.50 | — |
| `demo_lofi.ogg` | `lofi` | 采样率 0.60 · 位数 0.70 · 干湿比 0.70 · 音色 0.40 | — |
| `demo_swell.ogg` | `swell` | 衰减 0.70 · 阻尼 0.30 · 干湿比 0.50 · 上升时间 0.40 | — |
| `demo_chorus.ogg` | `chorus` | 速度 0.30 · 深度 0.60 · 干湿比 0.50 | — |
| `demo_flanger.ogg` | `flanger` | 速度 0.15 · 深度 0.80 · 干湿比 0.50 · 反馈 0.60 | — |
| `demo_phaser.ogg` | `phaser` | 速度 0.20 · 深度 0.90 · 干湿比 0.50 · 反馈 0.50 | — |
| `demo_tremolo.ogg` | `tremolo` | 速度 0.30 · 深度 0.70 · 声像 0.60 | — |
| `demo_vibrato.ogg` | `vibrato` | 速度 0.40 · 深度 0.50 · 干湿比 1.00 | — |
| `demo_octava.ogg` | `octava` | 低八度 0.60 · 高八度 0.40 · 干声 0.80 | — |
| `demo_armonizador.ogg` | `armonizador` | 音程 0.75 · 反馈 0.30 · 干湿比 0.45 | — |
| `demo_doblador.ogg` | `doblador` | 失谐 0.50 · 干湿比 0.50 | — |
| `demo_escalera.ogg` | `escalera` | 音程 0.95 · 反馈 0.60 · 干湿比 0.45 · 时间 0.40 | — |
| `demo_shimmer_quinta.ogg` | `shimmer_quinta` | 衰减 0.75 · 阻尼 0.25 · 干湿比 0.55 · shimmer 量 0.60 | — |
| `demo_blackhole.ogg` | `blackhole` | 衰减 0.85 · 阻尼 0.35 · 干湿比 0.50 | — |
| `demo_bloom.ogg` | `bloom` | 衰减 0.80 · 阻尼 0.30 · 干湿比 0.55 · 绽放时间 0.40 | — |
| `demo_gated.ogg` | `gated` | 衰减 0.80 · 阻尼 0.20 · 干湿比 0.50 · 时长 0.50 | — |
| `demo_infinite.ogg` | `infinite` | 释放 0.10 · 阻尼 0.30 · 干湿比 0.45 | — |
| `demo_reverb_inversa.ogg` | `reverb_inversa` | 衰减 0.80 · 阻尼 0.30 · 干湿比 0.55 · 时长 0.60 | — |
| `demo_spring.ogg` | `spring` | 衰减 0.60 · 阻尼 0.40 · 干湿比 0.40 | — |
| `demo_delay.ogg` | `delay` | 时间 0.55 · 反馈 0.45 · 干湿比 0.40 · 音色 0.70 | — |
| `demo_pingpong.ogg` | `pingpong` | 时间 0.70 · 反馈 0.50 · 干湿比 0.45 | — |
| `demo_lluvia.ogg` | `lluvia` | 扩散 0.70 · 反馈 0.40 · 干湿比 0.50 | — |
| `demo_bbd.ogg` | `bbd` | 时间 0.60 · 反馈 0.60 · 干湿比 0.45 · 调制 0.50 | — |
| `demo_ducking.ogg` | `ducking` | 时间 0.45 · 反馈 0.50 · 干湿比 0.50 · 闪避 0.80 | — |
| `demo_autowah.ogg` | `autowah` | 灵敏度 0.80 · 谐振 0.60 · 干湿比 0.80 | — |
| `demo_compresor.ogg` | `compresor` | 阈值 0.30 · 压缩 0.80 · 干湿比 1.00 · 增益 0.40 | — |
| `demo_filtro.ogg` | `filtro` | 速度 0.25 · 谐振 0.60 · 干湿比 0.90 · 深度 0.80 | — |
| `demo_puerta.ogg` | `puerta` | 阈值 0.20 · 释放 0.40 | — |
| `demo_saturacion.ogg` | `saturacion` | 增益 0.60 · 音色 0.50 · 干湿比 1.00 · 电平 0.70 | — |
| `demo_ringmod.ogg` | `ringmod` | 频率 0.15 · 干湿比 0.60 | — |
| `demo_slicer.ogg` | `slicer` | 速度 0.30 · 深度 0.90 · 占空比 0.40 · 平滑 0.40 | — |
| `demo_ancho.ogg` | `ancho` | 宽度 0.80 · 倾斜 0.60 | — |
| `demo_chorale.ogg` | `chorale` | 衰减 0.75 · 阻尼 0.30 · 干湿比 0.55 · 元音 0.30 | — |
| `demo_resonador.ogg` | `resonador` | 延音 0.80 · 激励 0.70 · 干湿比 0.50 | — |
| `demo_plate_vivo.ogg` | `plate_vivo` | 衰减 0.75 · 阻尼 0.30 · 干湿比 0.45 · 生动度 1.00 | — |
| `demo_shimmer_energia.ogg` | `shimmer_energia` | 衰减 0.80 · 阻尼 0.25 · 干湿比 0.55 · shimmer 量 0.90 | — |
| `demo_freeze_givens.ogg` | `freeze_givens` | 衰减 0.60 · 阻尼 0.30 · 干湿比 0.50 · 旋转 0.60 | 2.50 → 8.00 s |
| `demo_looper.ogg` | `looper` | 电平 0.80 · 速度 0.50 · 方向 0.00 · 反馈 0.80 | 0.00 → 0.66 s, 1.32 → 1.98 s |
| `demo_granular.ogg` | `granular` | 时长 0.60 · 扩散 0.50 · 音程 1.00 · 干湿比 0.60 | 1.60 → 7.00 s |
| `demo_shimmer_grave.ogg` | `shimmer_grave` | 衰减 0.75 · 阻尼 0.30 · 干湿比 0.50 · shimmer 量 0.60 | — |
| `demo_marea.ogg` | `marea` | 衰减 0.80 · 阻尼 0.30 · 干湿比 0.50 · 速度 0.20 | — |
| `demo_ensemble.ogg` | `ensemble` | 衰减 0.75 · 阻尼 0.30 · 干湿比 0.50 · 合奏 0.70 | — |
| `demo_sostenido.ogg` | `sostenido` | 层叠 0.20 · 阻尼 0.30 · 干湿比 0.50 · 捕捉 0.30 | — |
| `demo_shoegaze.ogg` | `shoegaze` | 衰减 0.85 · 阻尼 0.30 · 干湿比 0.55 · 饱和 0.80 | — |
| `demo_bruma.ogg` | `bruma` | 扩散 0.70 · 反馈 0.55 · 干湿比 0.50 · 磁头 1.00 | — |
| `demo_cadena_eco_y_muelle.ogg` | Eco y muelle: `delay` → `spring` | pot0 0.55 · pot1 0.40 · pot2 0.35 · pot3 0.60 · pot4 0.40 · pot5 0.00 | — |
| `demo_cadena_flor_al_reves.ogg` | Flor al revés: `reverse` → `bloom` | pot0 0.60 · pot1 0.40 · pot2 0.50 · pot3 0.80 · pot4 0.55 · pot5 0.40 | — |
| `demo_cadena_organo_infinito.ogg` | Órgano infinito: `octava` → `infinite` | pot0 0.60 · pot1 0.40 · pot2 0.00 · pot3 0.10 · pot4 0.50 · pot5 0.00 | — |
| `demo_cadena_shimmer_con_vibrato.ogg` | Shimmer con vibrato: `vibrato` → `shimmer` | pot0 0.30 · pot1 0.40 · pot2 0.00 · pot3 0.75 · pot4 0.55 · pot5 0.60 | — |
| `demo_cadena_cuerdas_en_ola.ogg` | Cuerdas en ola: `tremolo` → `ensemble` | pot0 0.15 · pot1 0.70 · pot2 0.00 · pot3 0.80 · pot4 0.50 · pot5 0.70 | — |
| `demo_cadena_fuzz_en_la_nube.ogg` | Fuzz en la nube: `saturacion` → `cloud` | pot0 0.60 · pot1 0.00 · pot2 0.00 · pot3 0.70 · pot4 0.50 · pot5 0.60 | — |

Ogg Vorbis，48,828 Hz（ADR 0005，西班牙语）；渲染在 24 位下逐位精确。旋钮与程序见 `docs/programas.zh-CN.md`。
