# demo_examples

Una guitarra sintética (arpegio de Em9, cuerdas Karplus-Strong) procesada por cada programa del núcleo con el modelo bit-exact. Se regeneran con `.venv/bin/python scripts/generar_demos.py`: el audio sale igual cada vez.

| Fichero | Programa | Mandos | Footswitch |
|---|---|---|---|
| `demo_guitarra.ogg` | — | — | — |
| `demo_plate.ogg` | `plate` | decay 0,70 · damping 0,30 · mezcla 0,45 | — |
| `demo_shimmer.ogg` | `shimmer` | decay 0,75 · damping 0,25 · mezcla 0,55 · cantidad de shimmer 0,60 | — |
| `demo_freeze.ogg` | `freeze` | decay 0,60 · damping 0,30 · mezcla 0,50 | 2,50 → 8,00 s |
| `demo_hall.ogg` | `hall` | decay 0,75 · damping 0,35 · mezcla 0,45 | — |
| `demo_cloud.ogg` | `cloud` | decay 0,70 · damping 0,30 · mezcla 0,55 · modulación 0,60 | — |
| `demo_cinta.ogg` | `cinta` | tiempo 0,45 · realimentación 0,55 · mezcla 0,40 · wow y flutter 0,50 | — |
| `demo_reverse.ogg` | `reverse` | tono 0,60 · realimentación 0,40 · mezcla 0,50 | — |
| `demo_lofi.ogg` | `lofi` | muestreo 0,60 · bits 0,70 · mezcla 0,70 · tono 0,40 | — |
| `demo_swell.ogg` | `swell` | decay 0,70 · damping 0,30 · mezcla 0,50 · subida 0,40 | — |
| `demo_chorus.ogg` | `chorus` | velocidad 0,30 · profundidad 0,60 · mezcla 0,50 | — |
| `demo_flanger.ogg` | `flanger` | velocidad 0,15 · profundidad 0,80 · mezcla 0,50 · realimentación 0,60 | — |
| `demo_phaser.ogg` | `phaser` | velocidad 0,20 · profundidad 0,90 · mezcla 0,50 · realimentación 0,50 | — |
| `demo_tremolo.ogg` | `tremolo` | velocidad 0,30 · profundidad 0,70 · panorama 0,60 | — |
| `demo_vibrato.ogg` | `vibrato` | velocidad 0,40 · profundidad 0,50 · mezcla 1,00 | — |
| `demo_octava.ogg` | `octava` | octava baja 0,60 · octava alta 0,40 · seco 0,80 | — |
| `demo_armonizador.ogg` | `armonizador` | intervalo 0,75 · realimentación 0,30 · mezcla 0,45 | — |
| `demo_doblador.ogg` | `doblador` | desafinación 0,50 · mezcla 0,50 | — |
| `demo_escalera.ogg` | `escalera` | intervalo 0,95 · realimentación 0,60 · mezcla 0,45 · tiempo 0,40 | — |
| `demo_shimmer_quinta.ogg` | `shimmer_quinta` | decay 0,75 · damping 0,25 · mezcla 0,55 · cantidad de shimmer 0,60 | — |
| `demo_blackhole.ogg` | `blackhole` | decay 0,85 · damping 0,35 · mezcla 0,50 | — |
| `demo_bloom.ogg` | `bloom` | decay 0,80 · damping 0,30 · mezcla 0,55 · apertura 0,40 | — |
| `demo_gated.ogg` | `gated` | decay 0,80 · damping 0,20 · mezcla 0,50 · duración 0,50 | — |
| `demo_infinite.ogg` | `infinite` | vaciado 0,10 · damping 0,30 · mezcla 0,45 | — |
| `demo_reverb_inversa.ogg` | `reverb_inversa` | decay 0,80 · damping 0,30 · mezcla 0,55 · duración 0,60 | — |
| `demo_spring.ogg` | `spring` | decay 0,60 · damping 0,40 · mezcla 0,40 | — |
| `demo_delay.ogg` | `delay` | tiempo 0,55 · realimentación 0,45 · mezcla 0,40 · tono 0,70 | — |
| `demo_pingpong.ogg` | `pingpong` | tiempo 0,70 · realimentación 0,50 · mezcla 0,45 | — |
| `demo_lluvia.ogg` | `lluvia` | difusión 0,70 · realimentación 0,40 · mezcla 0,50 | — |
| `demo_bbd.ogg` | `bbd` | tiempo 0,60 · realimentación 0,60 · mezcla 0,45 · modulación 0,50 | — |
| `demo_ducking.ogg` | `ducking` | tiempo 0,45 · realimentación 0,50 · mezcla 0,50 · ducking 0,80 | — |
| `demo_autowah.ogg` | `autowah` | sensibilidad 0,80 · resonancia 0,60 · mezcla 0,80 | — |
| `demo_compresor.ogg` | `compresor` | umbral 0,30 · compresión 0,80 · mezcla 1,00 · ganancia 0,40 | — |
| `demo_filtro.ogg` | `filtro` | velocidad 0,25 · resonancia 0,60 · mezcla 0,90 · profundidad 0,80 | — |
| `demo_puerta.ogg` | `puerta` | umbral 0,20 · cierre 0,40 | — |
| `demo_saturacion.ogg` | `saturacion` | ganancia 0,60 · tono 0,50 · mezcla 1,00 · nivel 0,70 | — |
| `demo_ringmod.ogg` | `ringmod` | frecuencia 0,15 · mezcla 0,60 | — |
| `demo_slicer.ogg` | `slicer` | velocidad 0,30 · profundidad 0,90 · ciclo 0,40 · suavizado 0,40 | — |
| `demo_ancho.ogg` | `ancho` | ancho 0,80 · tilt 0,60 | — |
| `demo_chorale.ogg` | `chorale` | decay 0,75 · damping 0,30 · mezcla 0,55 · vocal 0,30 | — |
| `demo_resonador.ogg` | `resonador` | sustain 0,80 · excitación 0,70 · mezcla 0,50 | — |
| `demo_plate_vivo.ogg` | `plate_vivo` | decay 0,75 · damping 0,30 · mezcla 0,45 · vida 1,00 | — |
| `demo_shimmer_energia.ogg` | `shimmer_energia` | decay 0,80 · damping 0,25 · mezcla 0,55 · cantidad de shimmer 0,90 | — |
| `demo_freeze_givens.ogg` | `freeze_givens` | decay 0,60 · damping 0,30 · mezcla 0,50 · giro 0,60 | 2,50 → 8,00 s |

Ogg Vorbis a 48 828 Hz (ADR 0005); el render es bit-exact en 24 bit. Los mandos y los programas están en `docs/programas.md`.
