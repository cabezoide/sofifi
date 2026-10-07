# demo_examples

**Español** · Una guitarra sintética (arpegio de Em9, cuerdas Karplus-Strong) procesada por los programas del núcleo SOFIFI, con el modelo bit-exact. Se regeneran byte a byte con `.venv/bin/python scripts/generar_demos.py`.

**English** · A synthetic guitar (Em9 arpeggio, Karplus-Strong strings) processed by the SOFIFI core programs using the bit-exact model. Regenerate them byte for byte with `.venv/bin/python scripts/generar_demos.py`.

**简体中文** · 一段合成吉他（Em9 琶音，Karplus-Strong 弦模型）经 SOFIFI 内核程序（逐位精确模型）处理的结果。可用 `.venv/bin/python scripts/generar_demos.py` 逐字节重新生成。

| Fichero / File / 文件 | Programa | pot0 decay | pot1 damping | pot2 mezcla/mix | pot3 shimmer/modulación | freeze |
|---|---|---|---|---|---|---|
| `demo_guitarra.wav` | — (seca / dry / 干声) | | | | | |
| `demo_plate.wav` | `plate.sasm` | 0,70 | 0,30 | 0,45 | | |
| `demo_shimmer.wav` | `shimmer.sasm` | 0,75 | 0,25 | 0,55 | 0,60 | |
| `demo_freeze.wav` | `freeze.sasm` | 0,60 | 0,30 | 0,50 | | 2,5 s → 8 s |
| `demo_hall.wav` | `hall.sasm` | 0,75 | 0,35 | 0,45 | | |
| `demo_cloud.wav` | `cloud.sasm` | 0,70 | 0,30 | 0,55 | 0,60 | |
| `demo_cinta.wav` | `cinta.sasm` | 0,45 (tiempo/time) | 0,55 (realimentación/feedback) | 0,40 | 0,50 (wow) | |
| `demo_reverse.wav` | `reverse.sasm` | 0,60 (tono/tone) | 0,40 (realimentación/feedback) | 0,50 | | |
| `demo_lofi.wav` | `lofi.sasm` | 0,60 (muestreo/sample rate) | 0,70 (8 bit) | 0,70 | 0,40 (tono/tone) | |
| `demo_swell.wav` | `swell.sasm` | 0,70 | 0,30 | 0,50 | 0,40 (subida/rise) | |

PCM de 16 bit a 48 828 Hz (ADR 0005); el render es bit-exact en 24 bit. 16-bit PCM at 48,828 Hz; the render is bit-exact at 24 bits. 16 位 PCM，48,828 Hz；渲染在 24 位下逐位精确。
