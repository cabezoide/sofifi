<!-- i18n: fuente=demo_examples/README.md sha=74f2450d718c estado=al_dia -->
# demo_examples

A synthetic guitar (an Em9 arpeggio, Karplus-Strong strings) through each core program, with the bit-exact model. Generate them again with `.venv/bin/python scripts/generar_demos.py`: the audio is the same each time.

| File | Program | Knobs | Footswitch |
|---|---|---|---|
| `demo_guitarra.ogg` | — | — | — |
| `demo_plate.ogg` | `plate` | decay 0.70 · damping 0.30 · mix 0.45 | — |
| `demo_shimmer.ogg` | `shimmer` | decay 0.75 · damping 0.25 · mix 0.55 · shimmer amount 0.60 | — |
| `demo_freeze.ogg` | `freeze` | decay 0.60 · damping 0.30 · mix 0.50 | 2.50 → 8.00 s |
| `demo_hall.ogg` | `hall` | decay 0.75 · damping 0.35 · mix 0.45 | — |
| `demo_cloud.ogg` | `cloud` | decay 0.70 · damping 0.30 · mix 0.55 · modulation 0.60 | — |
| `demo_cinta.ogg` | `cinta` | time 0.45 · feedback 0.55 · mix 0.40 · wow and flutter 0.50 | — |
| `demo_reverse.ogg` | `reverse` | tone 0.60 · feedback 0.40 · mix 0.50 | — |
| `demo_lofi.ogg` | `lofi` | sample rate 0.60 · bits 0.70 · mix 0.70 · tone 0.40 | — |
| `demo_swell.ogg` | `swell` | decay 0.70 · damping 0.30 · mix 0.50 · rise time 0.40 | — |
| `demo_chorus.ogg` | `chorus` | rate 0.30 · depth 0.60 · mix 0.50 | — |
| `demo_flanger.ogg` | `flanger` | rate 0.15 · depth 0.80 · mix 0.50 · feedback 0.60 | — |
| `demo_phaser.ogg` | `phaser` | rate 0.20 · depth 0.90 · mix 0.50 · feedback 0.50 | — |
| `demo_tremolo.ogg` | `tremolo` | rate 0.30 · depth 0.70 · pan 0.60 | — |
| `demo_vibrato.ogg` | `vibrato` | rate 0.40 · depth 0.50 · mix 1.00 | — |
| `demo_octava.ogg` | `octava` | lower octave 0.60 · upper octave 0.40 · dry 0.80 | — |
| `demo_armonizador.ogg` | `armonizador` | interval 0.75 · feedback 0.30 · mix 0.45 | — |
| `demo_doblador.ogg` | `doblador` | detune 0.50 · mix 0.50 | — |
| `demo_escalera.ogg` | `escalera` | interval 0.95 · feedback 0.60 · mix 0.45 · time 0.40 | — |
| `demo_shimmer_quinta.ogg` | `shimmer_quinta` | decay 0.75 · damping 0.25 · mix 0.55 · shimmer amount 0.60 | — |
| `demo_blackhole.ogg` | `blackhole` | decay 0.85 · damping 0.35 · mix 0.50 | — |
| `demo_bloom.ogg` | `bloom` | decay 0.80 · damping 0.30 · mix 0.55 · bloom time 0.40 | — |
| `demo_gated.ogg` | `gated` | decay 0.80 · damping 0.20 · mix 0.50 · length 0.50 | — |
| `demo_infinite.ogg` | `infinite` | release 0.10 · damping 0.30 · mix 0.45 | — |
| `demo_reverb_inversa.ogg` | `reverb_inversa` | decay 0.80 · damping 0.30 · mix 0.55 · length 0.60 | — |
| `demo_spring.ogg` | `spring` | decay 0.60 · damping 0.40 · mix 0.40 | — |
| `demo_delay.ogg` | `delay` | time 0.55 · feedback 0.45 · mix 0.40 · tone 0.70 | — |
| `demo_pingpong.ogg` | `pingpong` | time 0.70 · feedback 0.50 · mix 0.45 | — |
| `demo_lluvia.ogg` | `lluvia` | diffusion 0.70 · feedback 0.40 · mix 0.50 | — |
| `demo_bbd.ogg` | `bbd` | time 0.60 · feedback 0.60 · mix 0.45 · modulation 0.50 | — |
| `demo_ducking.ogg` | `ducking` | time 0.45 · feedback 0.50 · mix 0.50 · ducking 0.80 | — |
| `demo_autowah.ogg` | `autowah` | sensitivity 0.80 · resonance 0.60 · mix 0.80 | — |
| `demo_compresor.ogg` | `compresor` | threshold 0.30 · compression 0.80 · mix 1.00 · gain 0.40 | — |
| `demo_filtro.ogg` | `filtro` | rate 0.25 · resonance 0.60 · mix 0.90 · depth 0.80 | — |
| `demo_puerta.ogg` | `puerta` | threshold 0.20 · release 0.40 | — |
| `demo_saturacion.ogg` | `saturacion` | gain 0.60 · tone 0.50 · mix 1.00 · level 0.70 | — |
| `demo_ringmod.ogg` | `ringmod` | frequency 0.15 · mix 0.60 | — |
| `demo_slicer.ogg` | `slicer` | rate 0.30 · depth 0.90 · duty cycle 0.40 · smoothing 0.40 | — |
| `demo_ancho.ogg` | `ancho` | width 0.80 · tilt 0.60 | — |
| `demo_chorale.ogg` | `chorale` | decay 0.75 · damping 0.30 · mix 0.55 · vowel 0.30 | — |
| `demo_resonador.ogg` | `resonador` | sustain 0.80 · excitation 0.70 · mix 0.50 | — |
| `demo_plate_vivo.ogg` | `plate_vivo` | decay 0.75 · damping 0.30 · mix 0.45 · life 1.00 | — |
| `demo_shimmer_energia.ogg` | `shimmer_energia` | decay 0.80 · damping 0.25 · mix 0.55 · shimmer amount 0.90 | — |
| `demo_freeze_givens.ogg` | `freeze_givens` | decay 0.60 · damping 0.30 · mix 0.50 · rotation 0.60 | 2.50 → 8.00 s |
| `demo_looper.ogg` | `looper` | level 0.80 · rate 0.50 · direction 0.00 · feedback 0.80 | 0.00 → 0.66 s, 1.32 → 1.98 s |
| `demo_granular.ogg` | `granular` | length 0.60 · diffusion 0.50 · interval 1.00 · mix 0.60 | 1.60 → 7.00 s |
| `demo_shimmer_grave.ogg` | `shimmer_grave` | decay 0.75 · damping 0.30 · mix 0.50 · shimmer amount 0.60 | — |
| `demo_marea.ogg` | `marea` | decay 0.80 · damping 0.30 · mix 0.50 · rate 0.20 | — |
| `demo_ensemble.ogg` | `ensemble` | decay 0.75 · damping 0.30 · mix 0.50 · ensemble 0.70 | — |
| `demo_sostenido.ogg` | `sostenido` | layers 0.20 · damping 0.30 · mix 0.50 · capture 0.30 | — |
| `demo_shoegaze.ogg` | `shoegaze` | decay 0.85 · damping 0.30 · mix 0.55 · saturation 0.80 | — |
| `demo_bruma.ogg` | `bruma` | diffusion 0.70 · feedback 0.55 · mix 0.50 · heads 1.00 | — |
| `demo_armonico.ogg` | `armonico` | rate 0.30 · depth 0.75 · echo 0.35 · frequency 0.50 · shape 0.10 · width 0.80 | — |
| `demo_arcoiris.ogg` | `arcoiris` | interval 0.79 · second voice 0.00 · mix 0.50 · time 0.30 · feedback 0.75 · tone 0.60 | 2.50 → 4.00 s |
| `demo_tambor.ogg` | `tambor` | rate 0.55 · feedback 0.50 · mix 0.45 · heads 0.85 · age 0.40 · tone 0.60 | 3.50 → 5.00 s |
| `demo_mosaico.ogg` | `mosaico` | lower octave 0.60 · level 0.70 · mix 0.55 · upper octave 0.50 · feedback 0.85 · diffusion 0.60 | 4.00 → 8.00 s |
| `demo_erosion.ogg` | `erosion` | erosion 0.25 · damping 0.60 · mix 0.65 · modulation 0.70 · level 1.00 · length 1.00 | 0.00 → 0.67 s |
| `demo_desplazador.ogg` | `desplazador` | frequency shift 0.75 · time 0.45 · mix 0.50 · feedback 0.85 · tone 0.70 · width 0.50 | — |
| `demo_violin.ogg` | `violin` | rise time 0.50 · time 0.30 · mix 1.00 · depth 0.60 · rate 0.30 · tone 0.50 | — |
| `demo_shimmer_escondido.ogg` | `shimmer_escondido` | decay 0.80 · damping 0.25 · mix 0.55 · shimmer amount 0.80 · ducking 1.00 · tone 0.40 | — |
| `demo_arco.ogg` | `arco` | sustain 0.85 · rise time 0.50 · mix 0.85 · upper octave 0.70 · tone 0.30 · threshold 0.20 | — |
| `demo_oscilador.ogg` | `oscilador` | time 0.12 · feedback 0.70 · mix 0.50 · smoothing 0.70 · tone 0.40 · level 0.20 | 2.00 → 4.00 s |
| `demo_dinamica.ogg` | `dinamica` | decay 0.75 · damping 0.30 · mix 0.45 · depth 0.85 · threshold 0.10 · rate 0.10 | — |
| `demo_acople.ogg` | `acople` | time 0.00 · interval 0.00 · mix 1.00 · rise time 0.15 · tone 0.55 · level 1.00 | — |
| `demo_enjambre.ogg` | `enjambre` | spread 0.40 · feedback 0.70 · mix 0.50 · diffusion 0.60 · tone 0.60 · drift 0.40 | 2.00 → 4.00 s |
| `demo_probabilidad.ogg` | `probabilidad` | time 0.75 · probability 0.50 · mix 0.45 · feedback 0.60 · tone 0.70 · smoothing 0.40 | 3.00 → 5.00 s |
| `demo_dados.ogg` | `dados` | time 0.70 · feedback 0.60 · mix 0.50 · probability 0.40 · tone 0.60 · width 0.70 | 1.50 → 1.60 s, 3.00 → 3.10 s |
| `demo_aureo.ogg` | `aureo` | slope 0.60 · feedback 0.60 · mix 0.45 · tone 0.60 · width 0.90 · diffusion 0.40 | 2.50 → 5.00 s |
| `demo_estelar.ogg` | `estelar` | time 0.45 · feedback 0.75 · mix 0.45 · depth 0.90 · rate 0.25 · resonance 0.40 | — |
| `demo_lata.ogg` | `lata` | time 0.35 · feedback 0.55 · mix 0.45 · depth 0.60 · tone 0.40 · oil 0.50 | 3.00 → 3.60 s |
| `demo_deriva.ogg` | `deriva` | time 0.45 · depth 0.50 · mix 0.45 · rate 0.35 · glide 0.40 · feedback 0.50 | — |
| `demo_dimension.ogg` | `dimension` | mode 0.65 · rate 0.50 · mix 0.50 · depth 0.60 · crossfeed 0.90 · tone 0.70 | — |
| `demo_vibe.ogg` | `vibe` | rate 0.25 · depth 0.80 · mix 0.00 · feedback 0.30 · shape 0.70 · tone 0.35 | 2.00 → 4.00 s |
| `demo_orilla.ogg` | `orilla` | rate 0.35 · depth 0.55 · mix 0.50 · smoothing 0.50 · low-pass gate 0.80 · sensitivity 0.50 | 3.00 → 3.80 s |
| `demo_baldosa.ogg` | `baldosa` | time 0.55 · decay 0.70 · mix 0.45 · modulation 0.50 · tone 0.40 · sample rate 0.30 | 2.60 → 3.40 s |
| `demo_eco_casero.ogg` | `eco_casero` | time 0.75 · feedback 0.55 · mix 0.45 · dirt 0.80 · modulation 0.30 · tone 0.30 | — |
| `demo_relevo.ogg` | `relevo` | time 0.60 · tuning 0.50 · mix 0.60 · vibrato 0.35 · tone 0.60 · level 0.70 | 1.00 → 1.10 s, 4.00 → 4.10 s |
| `demo_frenada.ogg` | `frenada` | time 0.50 · feedback 0.50 · mix 0.45 · brake time 0.50 · spin-up time 0.40 · wow and flutter 0.40 | 2.50 → 3.50 s |
| `demo_resbalon.ogg` | `resbalon` | rate 0.58 · feedback 0.70 · mix 0.55 · length 0.70 · tone 0.40 · time 0.20 | 4.00 → 7.00 s |
| `demo_tartamudeo.ogg` | `tartamudeo` | threshold 0.30 · length 0.45 · mix 0.50 · repeats 0.60 | — |
| `demo_dos_ecos.ogg` | `dos_ecos` | time 0.85 · feedback 0.60 · mix 0.50 · ratio 0.90 · balance 0.50 · diffusion 0.70 | 4.00 → 6.00 s |
| `demo_viento.ogg` | `viento` | rate 0.50 · resonance 0.60 · mix 0.50 · sensitivity 0.70 · frequency 0.50 · level 0.40 | 2.50 → 3.50 s |
| `demo_cadena_eco_y_muelle.ogg` | Eco y muelle: `delay` → `spring` | pot0 0.55 · pot1 0.40 · pot2 0.35 · pot3 0.60 · pot4 0.40 · pot5 0.00 | — |
| `demo_cadena_flor_al_reves.ogg` | Flor al revés: `reverse` → `bloom` | pot0 0.60 · pot1 0.40 · pot2 0.50 · pot3 0.80 · pot4 0.55 · pot5 0.40 | — |
| `demo_cadena_organo_infinito.ogg` | Órgano infinito: `octava` → `infinite` | pot0 0.60 · pot1 0.40 · pot2 0.00 · pot3 0.10 · pot4 0.50 · pot5 0.00 | — |
| `demo_cadena_shimmer_con_vibrato.ogg` | Shimmer con vibrato: `vibrato` → `shimmer` | pot0 0.30 · pot1 0.40 · pot2 0.00 · pot3 0.75 · pot4 0.55 · pot5 0.60 | — |
| `demo_cadena_cuerdas_en_ola.ogg` | Cuerdas en ola: `tremolo` → `ensemble` | pot0 0.15 · pot1 0.70 · pot2 0.00 · pot3 0.80 · pot4 0.50 · pot5 0.70 | — |
| `demo_cadena_fuzz_en_la_nube.ogg` | Fuzz en la nube: `saturacion` → `cloud` | pot0 0.60 · pot1 0.00 · pot2 0.00 · pot3 0.70 · pot4 0.50 · pot5 0.60 | — |

Ogg Vorbis at 48,828 Hz (ADR 0005, Spanish); the render is bit-exact at 24 bits. The knobs and the programs are in `docs/programas.en.md`.
