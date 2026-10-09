<!-- i18n: fuente=docs/programas.md sha=a7568d48c090 estado=al_dia -->
<!-- GENERADO por `sofifi catalogo` desde programas/*.sasm. No se edita a mano:
     model/tests/catalogo_test.py lo compara con su generador. -->

# Core programs

51 programs and 408 presets. Each program is a text file in `programas/`; the presets are in `presets/banco.toml`. Program and preset names are in Spanish.
The cycles are the RTL upper limit, of 2,048 per sample (`model/sofifi/domain/coste.py`). The memory has 43,008 words.

## Reverb

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `blackhole` | A giant hall with a decay of tens of seconds. | 0: decay<br>1: damping<br>2: mix | 8 | 140 | 883 | 40,882 |
| `bloom` | The reverb grows slowly after each note, like a flower that opens. | 0: decay<br>1: damping<br>2: mix<br>3: bloom time | 8 | 84 | 637 | 23,520 |
| `chorale` | The plate tail sings a vowel, from "a" to "i". | 0: decay<br>1: damping<br>2: mix<br>3: vowel | 8 | 160 | 1,192 | 37,439 |
| `cloud` | Long diffusers with random modulation: the attack dissolves. | 0: decay<br>1: damping<br>2: mix<br>3: modulation | 8 | 96 | 907 | 42,814 |
| `ensemble` | A three-voice chorus before the plate: the tail sounds like a string section. | 0: decay<br>1: damping<br>2: mix<br>3: ensemble | 8 | 99 | 953 | 38,540 |
| `freeze` | A plate that freezes the tail with the footswitch. | 0: decay<br>1: damping<br>2: mix | 8 | 103 | 940 | 37,439 |
| `freeze_givens` | A freeze that moves without losing energy: the frozen tail turns between the branches. | 0: decay<br>1: damping<br>2: mix<br>3: rotation | 8 | 136 | 1,138 | 37,439 |
| `gated` | A reverb that stops suddenly after each attack, as in the 1980s. | 0: decay<br>1: damping<br>2: mix<br>3: length | 8 | 133 | 1,098 | 37,439 |
| `hall` | A network of 8 delays with a Householder matrix: a large hall. | 0: decay<br>1: damping<br>2: mix | 8 | 137 | 863 | 34,522 |
| `infinite` | A plate that does not decay: each note adds to a layer that does not stop. | 0: release<br>1: damping<br>2: mix | 8 | 95 | 872 | 37,439 |
| `marea` | The plate tail rises and falls in waves, from side to side; the dry signal does not change. | 0: decay<br>1: damping<br>2: mix<br>3: rate | 8 | 137 | 1,126 | 37,439 |
| `plate` | Dattorro plate with a modulated tank. | 0: decay<br>1: damping<br>2: mix | 8 | 86 | 790 | 37,439 |
| `plate_vivo` | A plate whose modulation drifts at random: the tail never repeats. | 0: decay<br>1: damping<br>2: mix<br>3: life | 8 | 127 | 1,054 | 37,439 |
| `resonador` | Four strings tuned to E major that vibrate in sympathy with the playing. | 0: sustain<br>1: excitation<br>2: mix<br>3: tuning | 8 | 89 | 525 | 1 |
| `reverb_inversa` | Reverse reverb: after each attack, the tail grows and stops suddenly. | 0: decay<br>1: damping<br>2: mix<br>3: length | 8 | 133 | 1,098 | 37,439 |
| `shimmer` | A plate with +12 in the feedback: each turn goes up one octave. | 0: decay<br>1: damping<br>2: mix<br>3: shimmer amount | 8 | 108 | 1,037 | 41,539 |
| `shimmer_energia` | A shimmer that controls itself: the more octave it collects, the less it adds. | 0: decay<br>1: damping<br>2: mix<br>3: shimmer amount | 8 | 117 | 1,095 | 41,539 |
| `shimmer_grave` | Downward shimmer: each turn goes down one octave and the tail becomes a deep organ. | 0: decay<br>1: damping<br>2: mix<br>3: shimmer amount | 8 | 108 | 1,037 | 41,539 |
| `shimmer_quinta` | Fifth shimmer: each turn goes up 7 semitones, like a chord that opens. | 0: decay<br>1: damping<br>2: mix<br>3: shimmer amount | 8 | 108 | 1,037 | 41,539 |
| `shoegaze` | A plate that saturates after the tail: a wall of warm noise behind the guitar. | 0: decay<br>1: damping<br>2: mix<br>3: saturation | 8 | 142 | 1,106 | 37,439 |
| `sostenido` | Automatic freeze: each new chord is captured and keeps sounding as a pad. | 0: layers<br>1: damping<br>2: mix<br>3: capture | 8 | 141 | 1,190 | 37,439 |
| `spring` | Spring reverb: the sound drips, with the treble before the bass. | 0: decay<br>1: damping<br>2: mix | 8 | 95 | 832 | 1,850 |

## Delay

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `bbd` | Dark analog echo: each repeat loses treble and saturates. | 0: time<br>1: feedback<br>2: mix<br>3: modulation | 8 | 44 | 408 | 14,674 |
| `bruma` | A four-head echo that blurs on each turn until it becomes a reverb. | 0: diffusion<br>1: feedback<br>2: mix<br>3: heads | 8 | 53 | 536 | 41,553 |
| `cinta` | Tape echo from 0.18 to 0.85 s with wow, flutter and saturation. | 0: time<br>1: feedback<br>2: mix<br>3: wow and flutter | 8 | 50 | 484 | 41,600 |
| `delay` | Clean digital echo from 20 to 690 ms, with tone in the feedback. | 0: time<br>1: feedback<br>2: mix<br>3: tone | 8 | 38 | 309 | 33,749 |
| `ducking` | An echo that moves back while you play and comes back in the silences. | 0: time<br>1: feedback<br>2: mix<br>3: ducking | 8 | 51 | 394 | 33,749 |
| `lluvia` | Six irregular echoes that dissolve in allpass filters: a rain of notes. | 0: diffusion<br>1: feedback<br>2: mix | 8 | 46 | 364 | 35,385 |
| `pingpong` | A stereo echo that jumps from one side to the other. | 0: time<br>1: feedback<br>2: mix | 8 | 38 | 353 | 40,874 |
| `reverse` | Reversed echo in grains of 0.17 s. | 0: tone<br>1: feedback<br>2: mix | 8 | 34 | 301 | 16,388 |

## Modulation

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `chorus` | Three voices with moving delays. | 0: rate<br>1: depth<br>2: mix | 8 | 42 | 416 | 1,101 |
| `flanger` | A very short moving delay with feedback: sweeping combs. | 0: rate<br>1: depth<br>2: mix<br>3: feedback | 8 | 31 | 266 | 247 |
| `phaser` | Four allpass filters with a moving coefficient: sweeping notches. | 0: rate<br>1: depth<br>2: mix<br>3: feedback | 8 | 79 | 513 | 1 |
| `slicer` | It cuts the sound into rhythmic pulses, like a gate that opens and closes. | 0: rate<br>1: depth<br>2: duty cycle<br>3: smoothing | 8 | 37 | 262 | 1 |
| `tremolo` | The volume goes up and down; with pot2, from one side to the other. | 0: rate<br>1: depth<br>2: pan | 8 | 43 | 325 | 1 |
| `vibrato` | The pitch goes up and down. | 0: rate<br>1: depth<br>2: mix | 8 | 27 | 240 | 125 |

## Pitch

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `armonizador` | One voice at −12, −7, −5, +5, +7 or +12 semitones, with feedback. | 0: interval<br>1: feedback<br>2: mix | 8 | 55 | 450 | 4,100 |
| `doblador` | Two voices detuned by a few cents, one on each side: it widens the sound. | 0: detune<br>2: mix | 8 | 32 | 346 | 1,028 |
| `escalera` | An echo in which each repeat goes up or down an interval: a staircase. | 0: interval<br>1: feedback<br>2: mix<br>3: time | 8 | 67 | 582 | 39,313 |
| `octava` | Octaver: one octave down and one up, each with its own level. | 0: lower octave<br>1: upper octave<br>2: dry | 8 | 25 | 296 | 4,100 |

## Dynamics

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `compresor` | Compressor: it lowers the loud parts, keeps the soft ones and sustains the notes. | 0: threshold<br>1: compression<br>2: mix<br>3: gain | 8 | 57 | 394 | 1 |
| `puerta` | Noise gate: it silences the hum between notes and lets the playing through. | 0: threshold<br>1: release | 8 | 29 | 222 | 1 |
| `swell` | Each note starts in silence and rises, before a plate. | 0: decay<br>1: damping<br>2: mix<br>3: rise time | 8 | 116 | 983 | 37,439 |

## Texture

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `granular` | A 4-voice granular cloud with a Hann window, octave pitch and freeze. | 0: length<br>1: diffusion<br>2: interval<br>3: mix | 8 | 188 | 1,209 | 32,769 |
| `lofi` | Fewer samples per second and fewer bits, with aliasing. | 0: sample rate<br>1: bits<br>2: mix<br>3: tone | 8 | 81 | 577 | 1 |
| `ringmod` | Ring modulator: it multiplies the guitar by a sine; it sounds metallic. | 0: frequency<br>2: mix | 8 | 33 | 236 | 1 |
| `saturacion` | Overdrive-type saturation: from a warm glow to a thick distortion. | 0: gain<br>1: tone<br>2: mix<br>3: level | 8 | 42 | 277 | 1 |

## Filter

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `ancho` | Makes a mono guitar wide in stereo and tilts the tone between bass and treble. | 0: width<br>1: tilt | 8 | 26 | 185 | 636 |
| `autowah` | Automatic wah: the harder you play, the higher the filter goes. | 0: sensitivity<br>1: resonance<br>2: mix | 8 | 43 | 295 | 1 |
| `filtro` | A resonant low-pass filter that goes up and down by itself, with an LFO. | 0: rate<br>1: resonance<br>2: mix<br>3: depth | 8 | 60 | 394 | 1 |

## Looper

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `looper` | A 0.67 s micro-looper with overdub, ½×, 2× and reverse. | 0: level<br>1: rate<br>2: direction<br>3: feedback | 8 | 85 | 549 | 32,769 |

## Chains

A chain joins two programs into one, in series (→) or in parallel (‖), with no change to the RTL (ADR 0013, Spanish). The chains are in `presets/cadenas.toml`; `sofifi cadena` processes them. 18 fit today and 6 wait for the SDRAM: they only need memory.

| Chain | Programs | Cycles | Memory | Registers | LFOs | Status |
|---|---|---|---|---|---|---|
| Armonía en la placa | `armonizador` → `plate` | 1,270 | 41,539 | 14 | 3 | fits |
| Bruma que gira | `bruma` → `chorus` | 950 | 42,654 | 12 | 4 | fits |
| Campanas | `ringmod` → `shimmer` | 1,239 | 41,539 | 18 | 3 | fits |
| Cinta desgastada | `cinta` → `lofi` | 1,085 | 41,600 | 18 | 3 | fits |
| Cuerdas en ola | `tremolo` → `ensemble` | 1,288 | 38,540 | 16 | 4 | fits |
| Doble resonancia | `doblador` → `resonador` | 879 | 1,028 | 24 | 2 | fits |
| Eco oscuro en flor | `bbd` → `bloom` | 1,053 | 38,194 | 20 | 2 | fits |
| Eco y muelle | `delay` → `spring` | 1,149 | 35,599 | 14 | 1 | fits |
| Eco y resonancia | `delay` ‖ `resonador` | 870 | 33,749 | 27 | 1 | fits |
| Flor al revés | `reverse` → `bloom` | 930 | 39,908 | 17 | 1 | fits |
| Fuzz en la nube | `saturacion` → `cloud` | 1,248 | 42,814 | 16 | 4 | fits |
| Loop filtrado | `looper` → `filtro` | 983 | 32,769 | 22 | 0 | fits |
| Octavas en flor | `octava` ‖ `bloom` | 953 | 27,620 | 18 | 2 | fits |
| Placa que tiembla | `tremolo` → `plate` | 1,109 | 37,439 | 14 | 2 | fits |
| Shimmer con vibrato | `vibrato` → `shimmer` | 1,243 | 41,664 | 18 | 4 | fits |
| Silencio y agujero negro | `puerta` → `blackhole` | 1,099 | 40,882 | 20 | 2 | fits |
| Sustain en la placa | `compresor` → `plate` | 1,214 | 37,439 | 17 | 2 | fits |
| Órgano infinito | `octava` → `infinite` | 1,246 | 41,539 | 13 | 4 | fits |
| Bruma en flor | `bruma` → `bloom` | 1,181 | 65,073 | 19 | 1 | waits for the SDRAM |
| Cinta en la flor | `cinta` → `bloom` | 1,129 | 65,120 | 20 | 3 | waits for the SDRAM |
| Eco al revés congelado | `reverse` → `freeze` | 1,271 | 53,827 | 13 | 3 | waits for the SDRAM |
| Eco en la nube | `delay` → `plate` | 1,113 | 71,188 | 15 | 3 | waits for the SDRAM |
| Lluvia sobre la placa | `lluvia` → `plate` | 1,148 | 72,824 | 12 | 2 | waits for the SDRAM |
| Ping-pong infinito | `pingpong` → `infinite` | 1,223 | 78,313 | 13 | 3 | waits for the SDRAM |
