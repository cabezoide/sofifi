<!-- i18n: fuente=docs/programas.md sha=d4dca2838602 estado=al_dia -->
<!-- GENERADO por `sofifi catalogo` desde programas/*.sasm. No se edita a mano:
     model/tests/catalogo_test.py lo compara con su generador. -->

# Core programs

44 programs and 352 presets. Each program is a text file in `programas/`; the presets are in `presets/banco.toml`. Program and preset names are in Spanish.
The cycles are the RTL upper limit, of 2,048 per sample (`model/sofifi/domain/coste.py`). The memory has 43,008 words.

## Reverb

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `blackhole` | A giant hall with a decay of tens of seconds. | 0: decay<br>1: damping<br>2: mix | 8 | 140 | 1,615 | 40,882 |
| `bloom` | The reverb grows slowly after each note, like a flower that opens. | 0: decay<br>1: damping<br>2: mix<br>3: bloom time | 8 | 84 | 979 | 23,520 |
| `chorale` | The plate tail sings a vowel, from "a" to "i". | 0: decay<br>1: damping<br>2: mix<br>3: vowel | 8 | 160 | 1,942 | 37,439 |
| `cloud` | Long diffusers with random modulation: the attack dissolves. | 0: decay<br>1: damping<br>2: mix<br>3: modulation | 8 | 96 | 1,385 | 42,814 |
| `freeze` | A plate that freezes the tail with the footswitch. | 0: decay<br>1: damping<br>2: mix | 8 | 103 | 1,378 | 37,439 |
| `freeze_givens` | A freeze that moves without losing energy: the frozen tail turns between the branches. | 0: decay<br>1: damping<br>2: mix<br>3: rotation | 8 | 136 | 1,708 | 37,439 |
| `gated` | A reverb that stops suddenly after each attack, as in the 1980s. | 0: decay<br>1: damping<br>2: mix<br>3: length | 8 | 133 | 1,657 | 37,439 |
| `hall` | A network of 8 delays with a Householder matrix: a large hall. | 0: decay<br>1: damping<br>2: mix | 8 | 137 | 1,585 | 34,522 |
| `infinite` | A plate that does not decay: each note adds to a layer that does not stop. | 0: release<br>1: damping<br>2: mix | 8 | 95 | 1,300 | 37,439 |
| `plate` | Dattorro plate with a modulated tank. | 0: decay<br>1: damping<br>2: mix | 8 | 86 | 1,202 | 37,439 |
| `plate_vivo` | A plate whose modulation drifts at random: the tail never repeats. | 0: decay<br>1: damping<br>2: mix<br>3: life | 8 | 127 | 1,599 | 37,439 |
| `resonador` | Four strings tuned to E major that vibrate in sympathy with the playing. | 0: sustain<br>1: excitation<br>2: mix<br>3: tuning | 8 | 89 | 924 | 1 |
| `reverb_inversa` | Reverse reverb: after each attack, the tail grows and stops suddenly. | 0: decay<br>1: damping<br>2: mix<br>3: length | 8 | 133 | 1,657 | 37,439 |
| `shimmer` | A plate with +12 in the feedback: each turn goes up one octave. | 0: decay<br>1: damping<br>2: mix<br>3: shimmer amount | 8 | 108 | 1,553 | 41,539 |
| `shimmer_energia` | A shimmer that controls itself: the more octave it collects, the less it adds. | 0: decay<br>1: damping<br>2: mix<br>3: shimmer amount | 8 | 117 | 1,643 | 41,539 |
| `shimmer_quinta` | Fifth shimmer: each turn goes up 7 semitones, like a chord that opens. | 0: decay<br>1: damping<br>2: mix<br>3: shimmer amount | 8 | 108 | 1,553 | 41,539 |
| `spring` | Spring reverb: the sound drips, with the treble before the bass. | 0: decay<br>1: damping<br>2: mix | 8 | 95 | 1,273 | 1,850 |

## Delay

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `bbd` | Dark analog echo: each repeat loses treble and saturates. | 0: time<br>1: feedback<br>2: mix<br>3: modulation | 8 | 44 | 563 | 14,674 |
| `cinta` | Tape echo from 0.18 to 0.85 s with wow, flutter and saturation. | 0: time<br>1: feedback<br>2: mix<br>3: wow and flutter | 8 | 50 | 665 | 41,600 |
| `delay` | Clean digital echo from 20 to 690 ms, with tone in the feedback. | 0: time<br>1: feedback<br>2: mix<br>3: tone | 8 | 38 | 455 | 33,749 |
| `ducking` | An echo that moves back while you play and comes back in the silences. | 0: time<br>1: feedback<br>2: mix<br>3: ducking | 8 | 51 | 586 | 33,749 |
| `lluvia` | Six irregular echoes that dissolve in allpass filters: a rain of notes. | 0: diffusion<br>1: feedback<br>2: mix | 8 | 46 | 593 | 35,385 |
| `pingpong` | A stereo echo that jumps from one side to the other. | 0: time<br>1: feedback<br>2: mix | 8 | 38 | 497 | 40,874 |
| `reverse` | Reversed echo in grains of 0.17 s. | 0: tone<br>1: feedback<br>2: mix | 8 | 34 | 470 | 16,388 |

## Modulation

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `chorus` | Three voices with moving delays. | 0: rate<br>1: depth<br>2: mix | 8 | 42 | 578 | 1,101 |
| `flanger` | A very short moving delay with feedback: sweeping combs. | 0: rate<br>1: depth<br>2: mix<br>3: feedback | 8 | 31 | 384 | 247 |
| `phaser` | Four allpass filters with a moving coefficient: sweeping notches. | 0: rate<br>1: depth<br>2: mix<br>3: feedback | 8 | 79 | 802 | 1 |
| `slicer` | It cuts the sound into rhythmic pulses, like a gate that opens and closes. | 0: rate<br>1: depth<br>2: duty cycle<br>3: smoothing | 8 | 37 | 390 | 1 |
| `tremolo` | The volume goes up and down; with pot2, from one side to the other. | 0: rate<br>1: depth<br>2: pan | 8 | 43 | 442 | 1 |
| `vibrato` | The pitch goes up and down. | 0: rate<br>1: depth<br>2: mix | 8 | 27 | 344 | 125 |

## Pitch

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `armonizador` | One voice at −12, −7, −5, +5, +7 or +12 semitones, with feedback. | 0: interval<br>1: feedback<br>2: mix | 8 | 55 | 632 | 4,100 |
| `doblador` | Two voices detuned by a few cents, one on each side: it widens the sound. | 0: detune<br>2: mix | 8 | 32 | 540 | 1,028 |
| `escalera` | An echo in which each repeat goes up or down an interval: a staircase. | 0: interval<br>1: feedback<br>2: mix<br>3: time | 8 | 67 | 799 | 39,313 |
| `octava` | Octaver: one octave down and one up, each with its own level. | 0: lower octave<br>1: upper octave<br>2: dry | 8 | 25 | 470 | 4,100 |

## Dynamics

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `compresor` | Compressor: it lowers the loud parts, keeps the soft ones and sustains the notes. | 0: threshold<br>1: compression<br>2: mix<br>3: gain | 8 | 57 | 596 | 1 |
| `puerta` | Noise gate: it silences the hum between notes and lets the playing through. | 0: threshold<br>1: release | 8 | 29 | 317 | 1 |
| `swell` | Each note starts in silence and rises, before a plate. | 0: decay<br>1: damping<br>2: mix<br>3: rise time | 8 | 116 | 1,490 | 37,439 |

## Texture

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `lofi` | Fewer samples per second and fewer bits, with aliasing. | 0: sample rate<br>1: bits<br>2: mix<br>3: tone | 8 | 81 | 800 | 1 |
| `ringmod` | Ring modulator: it multiplies the guitar by a sine; it sounds metallic. | 0: frequency<br>2: mix | 8 | 33 | 362 | 1 |
| `saturacion` | Overdrive-type saturation: from a warm glow to a thick distortion. | 0: gain<br>1: tone<br>2: mix<br>3: level | 8 | 42 | 462 | 1 |

## Filter

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `ancho` | Makes a mono guitar wide in stereo and tilts the tone between bass and treble. | 0: width<br>1: tilt | 8 | 26 | 304 | 636 |
| `autowah` | Automatic wah: the harder you play, the higher the filter goes. | 0: sensitivity<br>1: resonance<br>2: mix | 8 | 43 | 464 | 1 |
| `filtro` | A resonant low-pass filter that goes up and down by itself, with an LFO. | 0: rate<br>1: resonance<br>2: mix<br>3: depth | 8 | 60 | 608 | 1 |

## Looper

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `looper` | A 0.67 s micro-looper with overdub, ½×, 2× and reverse. | 0: level<br>1: rate<br>2: direction<br>3: feedback | 8 | 85 | 809 | 1 |
