<!-- i18n: fuente=demo_examples/README.md sha=01075f5aa939 estado=al_dia -->
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
| `demo_armonico.ogg` | `armonico` | 速度 0.30 · 深度 0.75 · 回声 0.35 · 频率 0.50 · 波形 0.10 · 宽度 0.80 | — |
| `demo_arcoiris.ogg` | `arcoiris` | 音程 0.79 · 第二声部 0.00 · 干湿比 0.50 · 时间 0.30 · 反馈 0.75 · 音色 0.60 | 2.50 → 4.00 s |
| `demo_tambor.ogg` | `tambor` | 速度 0.55 · 反馈 0.50 · 干湿比 0.45 · 磁头 0.85 · 老化 0.40 · 音色 0.60 | 3.50 → 5.00 s |
| `demo_mosaico.ogg` | `mosaico` | 低八度 0.60 · 电平 0.70 · 干湿比 0.55 · 高八度 0.50 · 反馈 0.85 · 扩散 0.60 | 4.00 → 8.00 s |
| `demo_erosion.ogg` | `erosion` | 侵蚀 0.25 · 阻尼 0.60 · 干湿比 0.65 · 调制 0.70 · 电平 1.00 · 时长 1.00 | 0.00 → 0.67 s |
| `demo_desplazador.ogg` | `desplazador` | 移频 0.75 · 时间 0.45 · 干湿比 0.50 · 反馈 0.85 · 音色 0.70 · 宽度 0.50 | — |
| `demo_violin.ogg` | `violin` | 上升时间 0.50 · 时间 0.30 · 干湿比 1.00 · 深度 0.60 · 速度 0.30 · 音色 0.50 | — |
| `demo_shimmer_escondido.ogg` | `shimmer_escondido` | 衰减 0.80 · 阻尼 0.25 · 干湿比 0.55 · shimmer 量 0.80 · 闪避 1.00 · 音色 0.40 | — |
| `demo_arco.ogg` | `arco` | 延音 0.85 · 上升时间 0.50 · 干湿比 0.85 · 高八度 0.70 · 音色 0.30 · 阈值 0.20 | — |
| `demo_oscilador.ogg` | `oscilador` | 时间 0.12 · 反馈 0.70 · 干湿比 0.50 · 平滑 0.70 · 音色 0.40 · 电平 0.20 | 2.00 → 4.00 s |
| `demo_dinamica.ogg` | `dinamica` | 衰减 0.75 · 阻尼 0.30 · 干湿比 0.45 · 深度 0.85 · 阈值 0.10 · 速度 0.10 | — |
| `demo_acople.ogg` | `acople` | 时间 0.00 · 音程 0.00 · 干湿比 1.00 · 上升时间 0.15 · 音色 0.55 · 电平 1.00 | — |
| `demo_enjambre.ogg` | `enjambre` | 离散度 0.40 · 反馈 0.70 · 干湿比 0.50 · 扩散 0.60 · 音色 0.60 · 漂移 0.40 | 2.00 → 4.00 s |
| `demo_probabilidad.ogg` | `probabilidad` | 时间 0.75 · 概率 0.50 · 干湿比 0.45 · 反馈 0.60 · 音色 0.70 · 平滑 0.40 | 3.00 → 5.00 s |
| `demo_dados.ogg` | `dados` | 时间 0.70 · 反馈 0.60 · 干湿比 0.50 · 概率 0.40 · 音色 0.60 · 宽度 0.70 | 1.50 → 1.60 s, 3.00 → 3.10 s |
| `demo_aureo.ogg` | `aureo` | 斜率 0.60 · 反馈 0.60 · 干湿比 0.45 · 音色 0.60 · 宽度 0.90 · 扩散 0.40 | 2.50 → 5.00 s |
| `demo_estelar.ogg` | `estelar` | 时间 0.45 · 反馈 0.75 · 干湿比 0.45 · 深度 0.90 · 速度 0.25 · 谐振 0.40 | — |
| `demo_lata.ogg` | `lata` | 时间 0.35 · 反馈 0.55 · 干湿比 0.45 · 深度 0.60 · 音色 0.40 · 油 0.50 | 3.00 → 3.60 s |
| `demo_deriva.ogg` | `deriva` | 时间 0.45 · 深度 0.50 · 干湿比 0.45 · 速度 0.35 · 滑音 0.40 · 反馈 0.50 | — |
| `demo_dimension.ogg` | `dimension` | 模式 0.65 · 速度 0.50 · 干湿比 0.50 · 深度 0.60 · 交叉混合 0.90 · 音色 0.70 | — |
| `demo_vibe.ogg` | `vibe` | 速度 0.25 · 深度 0.80 · 干湿比 0.00 · 反馈 0.30 · 波形 0.70 · 音色 0.35 | 2.00 → 4.00 s |
| `demo_orilla.ogg` | `orilla` | 速度 0.35 · 深度 0.55 · 干湿比 0.50 · 平滑 0.50 · 低通门 0.80 · 灵敏度 0.50 | 3.00 → 3.80 s |
| `demo_baldosa.ogg` | `baldosa` | 时间 0.55 · 衰减 0.70 · 干湿比 0.45 · 调制 0.50 · 音色 0.40 · 采样率 0.30 | 2.60 → 3.40 s |
| `demo_eco_casero.ogg` | `eco_casero` | 时间 0.75 · 反馈 0.55 · 干湿比 0.45 · 脏污 0.80 · 调制 0.30 · 音色 0.30 | — |
| `demo_relevo.ogg` | `relevo` | 时间 0.60 · 调音 0.50 · 干湿比 0.60 · 颤音 0.35 · 音色 0.60 · 电平 0.70 | 1.00 → 1.10 s, 4.00 → 4.10 s |
| `demo_frenada.ogg` | `frenada` | 时间 0.50 · 反馈 0.50 · 干湿比 0.45 · 制动时间 0.50 · 启动时间 0.40 · wow 与 flutter 0.40 | 2.50 → 3.50 s |
| `demo_resbalon.ogg` | `resbalon` | 速度 0.58 · 反馈 0.70 · 干湿比 0.55 · 时长 0.70 · 音色 0.40 · 时间 0.20 | 4.00 → 7.00 s |
| `demo_tartamudeo.ogg` | `tartamudeo` | 阈值 0.30 · 时长 0.45 · 干湿比 0.50 · 重复次数 0.60 | — |
| `demo_dos_ecos.ogg` | `dos_ecos` | 时间 0.85 · 反馈 0.60 · 干湿比 0.50 · 比例 0.90 · 平衡 0.50 · 扩散 0.70 | 4.00 → 6.00 s |
| `demo_viento.ogg` | `viento` | 速度 0.50 · 谐振 0.60 · 干湿比 0.50 · 灵敏度 0.70 · 频率 0.50 · 电平 0.40 | 2.50 → 3.50 s |
| `demo_compas.ogg` | `compas` | 时间 0.60 · 反馈 0.45 · 干湿比 0.45 · 细分 0.10 · 第二抽头 1.00 · 音色 0.70 | 0.50 → 0.55 s, 1.00 → 1.05 s |
| `demo_espiral.ogg` | `espiral` | 音程 0.92 · 第二声部 0.08 · 干湿比 0.55 · 时间 0.40 · 反馈 0.70 · 衰减 0.60 | 3.00 → 4.50 s |
| `demo_swell_ritmico.ogg` | `swell_ritmico` | 上升时间 0.40 · 波形 0.20 · 干湿比 0.50 · 衰减 0.70 · 漂移 0.40 · 灵敏度 0.50 | 0.00 → 0.05 s, 0.22 → 0.27 s |
| `demo_semilla.ogg` | `semilla` | 衰减 0.80 · 阻尼 0.35 · 干湿比 0.50 · 种子 0.60 · 密度 0.80 · 调制 0.45 | 4.00 → 6.50 s |
| `demo_arpegio.ogg` | `arpegio` | 速度 0.45 · 音数 1.00 · 干湿比 0.50 · 模式 0.00 · 回声 0.40 · 衰减 0.60 | 3.00 → 5.00 s |
| `demo_cadena_eco_y_muelle.ogg` | Eco y muelle: `delay` → `spring` | pot0 0.55 · pot1 0.40 · pot2 0.35 · pot3 0.60 · pot4 0.40 · pot5 0.00 | — |
| `demo_cadena_flor_al_reves.ogg` | Flor al revés: `reverse` → `bloom` | pot0 0.60 · pot1 0.40 · pot2 0.50 · pot3 0.80 · pot4 0.55 · pot5 0.40 | — |
| `demo_cadena_organo_infinito.ogg` | Órgano infinito: `octava` → `infinite` | pot0 0.60 · pot1 0.40 · pot2 0.00 · pot3 0.10 · pot4 0.50 · pot5 0.00 | — |
| `demo_cadena_shimmer_con_vibrato.ogg` | Shimmer con vibrato: `vibrato` → `shimmer` | pot0 0.30 · pot1 0.40 · pot2 0.00 · pot3 0.75 · pot4 0.55 · pot5 0.60 | — |
| `demo_cadena_cuerdas_en_ola.ogg` | Cuerdas en ola: `tremolo` → `ensemble` | pot0 0.15 · pot1 0.70 · pot2 0.00 · pot3 0.80 · pot4 0.50 · pot5 0.70 | — |
| `demo_cadena_fuzz_en_la_nube.ogg` | Fuzz en la nube: `saturacion` → `cloud` | pot0 0.60 · pot1 0.00 · pot2 0.00 · pot3 0.70 · pot4 0.50 · pot5 0.60 | — |

Ogg Vorbis，48,828 Hz（ADR 0005，西班牙语）；渲染在 24 位下逐位精确。旋钮与程序见 `docs/programas.zh-CN.md`。
