# demo_examples

**Español** · Una guitarra sintética (arpegio de Em9, cuerdas Karplus-Strong) procesada por los programas del núcleo SOFIFI, con el modelo bit-exact. Se regeneran con `.venv/bin/python scripts/generar_demos.py`: el audio sale igual cada vez.

**English** · A synthetic guitar (Em9 arpeggio, Karplus-Strong strings) processed by the SOFIFI core programs using the bit-exact model. Regenerate them with `.venv/bin/python scripts/generar_demos.py`: the audio is the same every time.

**简体中文** · 一段合成吉他（Em9 琶音，Karplus-Strong 弦模型）经 SOFIFI 内核程序（逐位精确模型）处理的结果。可用 `.venv/bin/python scripts/generar_demos.py` 重新生成，每次得到的音频都相同。

| Fichero / File / 文件 | Programa | pot0 decay | pot1 damping | pot2 mezcla/mix | pot3 shimmer/modulación | freeze |
|---|---|---|---|---|---|---|
| `demo_guitarra.ogg` | — (seca / dry / 干声) | | | | | |
| `demo_plate.ogg` | `plate.sasm` | 0,70 | 0,30 | 0,45 | | |
| `demo_shimmer.ogg` | `shimmer.sasm` | 0,75 | 0,25 | 0,55 | 0,60 | |
| `demo_freeze.ogg` | `freeze.sasm` | 0,60 | 0,30 | 0,50 | | 2,5 s → 8 s |
| `demo_hall.ogg` | `hall.sasm` | 0,75 | 0,35 | 0,45 | | |
| `demo_cloud.ogg` | `cloud.sasm` | 0,70 | 0,30 | 0,55 | 0,60 | |
| `demo_cinta.ogg` | `cinta.sasm` | 0,45 (tiempo/time) | 0,55 (realimentación/feedback) | 0,40 | 0,50 (wow) | |
| `demo_reverse.ogg` | `reverse.sasm` | 0,60 (tono/tone) | 0,40 (realimentación/feedback) | 0,50 | | |
| `demo_lofi.ogg` | `lofi.sasm` | 0,60 (muestreo/sample rate) | 0,70 (8 bit) | 0,70 | 0,40 (tono/tone) | |
| `demo_swell.ogg` | `swell.sasm` | 0,70 | 0,30 | 0,50 | 0,40 (subida/rise) | |
| `demo_chorus.ogg` | `chorus.sasm` | 0,30 (velocidad/rate) | 0,60 (profundidad/depth) | 0,50 | | |
| `demo_flanger.ogg` | `flanger.sasm` | 0,15 (velocidad/rate) | 0,80 (profundidad/depth) | 0,50 | 0,60 (realimentación/feedback) | |
| `demo_phaser.ogg` | `phaser.sasm` | 0,20 (velocidad/rate) | 0,90 (profundidad/depth) | 0,50 | 0,50 (realimentación/feedback) | |
| `demo_tremolo.ogg` | `tremolo.sasm` | 0,30 (velocidad/rate) | 0,70 (profundidad/depth) | 0,60 (panorama/pan) | | |
| `demo_vibrato.ogg` | `vibrato.sasm` | 0,40 (velocidad/rate) | 0,50 (profundidad/depth) | 1 | | |
| `demo_octava.ogg` | `octava.sasm` | 0,60 (−12) | 0,40 (+12) | 0,80 (seco/dry) | | |
| `demo_armonizador.ogg` | `armonizador.sasm` | 0,75 (+7) | 0,30 (realimentación/feedback) | 0,45 | | |
| `demo_doblador.ogg` | `doblador.sasm` | 0,50 (±12 cents) | | 0,50 | | |
| `demo_escalera.ogg` | `escalera.sasm` | 0,95 (+12) | 0,60 (realimentación/feedback) | 0,45 | 0,40 (tiempo/time) | |
| `demo_shimmer_quinta.ogg` | `shimmer_quinta.sasm` | 0,75 | 0,25 | 0,55 | 0,60 | |

Ogg Vorbis a 48 828 Hz (ADR 0005); el render es bit-exact en 24 bit. Ogg Vorbis at 48,828 Hz; the render is bit-exact at 24 bits. Ogg Vorbis，48,828 Hz；渲染在 24 位下逐位精确。
