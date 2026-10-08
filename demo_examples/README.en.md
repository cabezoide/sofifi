<!-- i18n: fuente=demo_examples/README.md sha=f4b7e51f3061 estado=al_dia -->
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

Ogg Vorbis at 48,828 Hz (ADR 0005, Spanish); the render is bit-exact at 24 bits. The knobs and the programs are in `docs/programas.en.md`.
