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
| `demo_looper.ogg` | `looper` | nivel 0,80 · velocidad 0,50 · sentido 0,00 · realimentación 0,80 | 0,00 → 0,66 s, 1,32 → 1,98 s |
| `demo_granular.ogg` | `granular` | duración 0,60 · difusión 0,50 · intervalo 1,00 · mezcla 0,60 | 1,60 → 7,00 s |
| `demo_shimmer_grave.ogg` | `shimmer_grave` | decay 0,75 · damping 0,30 · mezcla 0,50 · cantidad de shimmer 0,60 | — |
| `demo_marea.ogg` | `marea` | decay 0,80 · damping 0,30 · mezcla 0,50 · velocidad 0,20 | — |
| `demo_ensemble.ogg` | `ensemble` | decay 0,75 · damping 0,30 · mezcla 0,50 · ensemble 0,70 | — |
| `demo_sostenido.ogg` | `sostenido` | capas 0,20 · damping 0,30 · mezcla 0,50 · captura 0,30 | — |
| `demo_shoegaze.ogg` | `shoegaze` | decay 0,85 · damping 0,30 · mezcla 0,55 · saturación 0,80 | — |
| `demo_bruma.ogg` | `bruma` | difusión 0,70 · realimentación 0,55 · mezcla 0,50 · cabezas 1,00 | — |
| `demo_armonico.ogg` | `armonico` | velocidad 0,30 · profundidad 0,75 · eco 0,35 · frecuencia 0,50 · forma 0,10 · ancho 0,80 | — |
| `demo_arcoiris.ogg` | `arcoiris` | intervalo 0,79 · segunda voz 0,00 · mezcla 0,50 · tiempo 0,30 · realimentación 0,75 · tono 0,60 | 2,50 → 4,00 s |
| `demo_tambor.ogg` | `tambor` | velocidad 0,55 · realimentación 0,50 · mezcla 0,45 · cabezas 0,85 · edad 0,40 · tono 0,60 | 3,50 → 5,00 s |
| `demo_mosaico.ogg` | `mosaico` | octava baja 0,60 · nivel 0,70 · mezcla 0,55 · octava alta 0,50 · realimentación 0,85 · difusión 0,60 | 4,00 → 8,00 s |
| `demo_erosion.ogg` | `erosion` | erosión 0,25 · damping 0,60 · mezcla 0,65 · modulación 0,70 · nivel 1,00 · duración 1,00 | 0,00 → 0,67 s |
| `demo_desplazador.ogg` | `desplazador` | desplazamiento 0,75 · tiempo 0,45 · mezcla 0,50 · realimentación 0,85 · tono 0,70 · ancho 0,50 | — |
| `demo_violin.ogg` | `violin` | subida 0,50 · tiempo 0,30 · mezcla 1,00 · profundidad 0,60 · velocidad 0,30 · tono 0,50 | — |
| `demo_shimmer_escondido.ogg` | `shimmer_escondido` | decay 0,80 · damping 0,25 · mezcla 0,55 · cantidad de shimmer 0,80 · ducking 1,00 · tono 0,40 | — |
| `demo_arco.ogg` | `arco` | sustain 0,85 · subida 0,50 · mezcla 0,85 · octava alta 0,70 · tono 0,30 · umbral 0,20 | — |
| `demo_oscilador.ogg` | `oscilador` | tiempo 0,12 · realimentación 0,70 · mezcla 0,50 · suavizado 0,70 · tono 0,40 · nivel 0,20 | 2,00 → 4,00 s |
| `demo_dinamica.ogg` | `dinamica` | decay 0,75 · damping 0,30 · mezcla 0,45 · profundidad 0,85 · umbral 0,10 · velocidad 0,10 | — |
| `demo_acople.ogg` | `acople` | tiempo 0,00 · intervalo 0,00 · mezcla 1,00 · subida 0,15 · tono 0,55 · nivel 1,00 | — |
| `demo_enjambre.ogg` | `enjambre` | dispersión 0,40 · realimentación 0,70 · mezcla 0,50 · difusión 0,60 · tono 0,60 · deriva 0,40 | 2,00 → 4,00 s |
| `demo_probabilidad.ogg` | `probabilidad` | tiempo 0,75 · probabilidad 0,50 · mezcla 0,45 · realimentación 0,60 · tono 0,70 · suavizado 0,40 | 3,00 → 5,00 s |
| `demo_dados.ogg` | `dados` | tiempo 0,70 · realimentación 0,60 · mezcla 0,50 · probabilidad 0,40 · tono 0,60 · ancho 0,70 | 1,50 → 1,60 s, 3,00 → 3,10 s |
| `demo_aureo.ogg` | `aureo` | inclinación 0,60 · realimentación 0,60 · mezcla 0,45 · tono 0,60 · ancho 0,90 · difusión 0,40 | 2,50 → 5,00 s |
| `demo_estelar.ogg` | `estelar` | tiempo 0,45 · realimentación 0,75 · mezcla 0,45 · profundidad 0,90 · velocidad 0,25 · resonancia 0,40 | — |
| `demo_lata.ogg` | `lata` | tiempo 0,35 · realimentación 0,55 · mezcla 0,45 · profundidad 0,60 · tono 0,40 · aceite 0,50 | 3,00 → 3,60 s |
| `demo_deriva.ogg` | `deriva` | tiempo 0,45 · profundidad 0,50 · mezcla 0,45 · velocidad 0,35 · glide 0,40 · realimentación 0,50 | — |
| `demo_dimension.ogg` | `dimension` | modo 0,65 · velocidad 0,50 · mezcla 0,50 · profundidad 0,60 · cruce 0,90 · tono 0,70 | — |
| `demo_vibe.ogg` | `vibe` | velocidad 0,25 · profundidad 0,80 · mezcla 0,00 · realimentación 0,30 · forma 0,70 · tono 0,35 | 2,00 → 4,00 s |
| `demo_orilla.ogg` | `orilla` | velocidad 0,35 · profundidad 0,55 · mezcla 0,50 · suavizado 0,50 · puerta 0,80 · sensibilidad 0,50 | 3,00 → 3,80 s |
| `demo_baldosa.ogg` | `baldosa` | tiempo 0,55 · decay 0,70 · mezcla 0,45 · modulación 0,50 · tono 0,40 · muestreo 0,30 | 2,60 → 3,40 s |
| `demo_eco_casero.ogg` | `eco_casero` | tiempo 0,75 · realimentación 0,55 · mezcla 0,45 · suciedad 0,80 · modulación 0,30 · tono 0,30 | — |
| `demo_relevo.ogg` | `relevo` | tiempo 0,60 · afinación 0,50 · mezcla 0,60 · vibrato 0,35 · tono 0,60 · nivel 0,70 | 1,00 → 1,10 s, 4,00 → 4,10 s |
| `demo_frenada.ogg` | `frenada` | tiempo 0,50 · realimentación 0,50 · mezcla 0,45 · frenada 0,50 · arranque 0,40 · wow y flutter 0,40 | 2,50 → 3,50 s |
| `demo_resbalon.ogg` | `resbalon` | velocidad 0,58 · realimentación 0,70 · mezcla 0,55 · duración 0,70 · tono 0,40 · tiempo 0,20 | 4,00 → 7,00 s |
| `demo_tartamudeo.ogg` | `tartamudeo` | umbral 0,30 · duración 0,45 · mezcla 0,50 · repeticiones 0,60 | — |
| `demo_dos_ecos.ogg` | `dos_ecos` | tiempo 0,85 · realimentación 0,60 · mezcla 0,50 · proporción 0,90 · equilibrio 0,50 · difusión 0,70 | 4,00 → 6,00 s |
| `demo_viento.ogg` | `viento` | velocidad 0,50 · resonancia 0,60 · mezcla 0,50 · sensibilidad 0,70 · frecuencia 0,50 · nivel 0,40 | 2,50 → 3,50 s |
| `demo_compas.ogg` | `compas` | tiempo 0,60 · realimentación 0,45 · mezcla 0,45 · subdivisión 0,10 · segunda toma 1,00 · tono 0,70 | 0,50 → 0,55 s, 1,00 → 1,05 s |
| `demo_espiral.ogg` | `espiral` | intervalo 0,92 · segunda voz 0,08 · mezcla 0,55 · tiempo 0,40 · realimentación 0,70 · decay 0,60 | 3,00 → 4,50 s |
| `demo_swell_ritmico.ogg` | `swell_ritmico` | subida 0,40 · forma 0,20 · mezcla 0,50 · decay 0,70 · deriva 0,40 · sensibilidad 0,50 | 0,00 → 0,05 s, 0,22 → 0,27 s |
| `demo_semilla.ogg` | `semilla` | decay 0,80 · damping 0,35 · mezcla 0,50 · semilla 0,60 · densidad 0,80 · modulación 0,45 | 4,00 → 6,50 s |
| `demo_arpegio.ogg` | `arpegio` | velocidad 0,45 · notas 1,00 · mezcla 0,50 · modo 0,00 · eco 0,40 · decay 0,60 | 3,00 → 5,00 s |
| `demo_cadena_eco_y_muelle.ogg` | Eco y muelle: `delay` → `spring` | pot0 0,55 · pot1 0,40 · pot2 0,35 · pot3 0,60 · pot4 0,40 · pot5 0,00 | — |
| `demo_cadena_flor_al_reves.ogg` | Flor al revés: `reverse` → `bloom` | pot0 0,60 · pot1 0,40 · pot2 0,50 · pot3 0,80 · pot4 0,55 · pot5 0,40 | — |
| `demo_cadena_organo_infinito.ogg` | Órgano infinito: `octava` → `infinite` | pot0 0,60 · pot1 0,40 · pot2 0,00 · pot3 0,10 · pot4 0,50 · pot5 0,00 | — |
| `demo_cadena_shimmer_con_vibrato.ogg` | Shimmer con vibrato: `vibrato` → `shimmer` | pot0 0,30 · pot1 0,40 · pot2 0,00 · pot3 0,75 · pot4 0,55 · pot5 0,60 | — |
| `demo_cadena_cuerdas_en_ola.ogg` | Cuerdas en ola: `tremolo` → `ensemble` | pot0 0,15 · pot1 0,70 · pot2 0,00 · pot3 0,80 · pot4 0,50 · pot5 0,70 | — |
| `demo_cadena_fuzz_en_la_nube.ogg` | Fuzz en la nube: `saturacion` → `cloud` | pot0 0,60 · pot1 0,00 · pot2 0,00 · pot3 0,70 · pot4 0,50 · pot5 0,60 | — |

Ogg Vorbis a 48 828 Hz (ADR 0005); el render es bit-exact en 24 bit. Los mandos y los programas están en `docs/programas.md`.
