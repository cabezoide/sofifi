<!-- i18n: fuente=docs/programas.md sha=f4f3a0032e92 estado=al_dia -->
<!-- GENERADO por `sofifi catalogo` desde programas/*.sasm. No se edita a mano:
     model/tests/catalogo_test.py lo compara con su generador. -->

# Core programs

86 programs and 688 presets. Each program is a text file in `programas/`; the presets are in `presets/banco.toml`. Program and preset names are in Spanish.
The cycles are the RTL upper limit, of 2,048 per sample (`model/sofifi/domain/coste.py`). The memory has 43,008 words.

## Reverb

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `baldosa` | Dirty reverb of two crossed echoes, dark and grainy, like a tiled bathroom. | 0: time<br>1: decay<br>2: mix<br>3: modulation<br>4: tone<br>5: sample rate | 8 | 152 | 1,145 | 8,258 |
| `blackhole` | A giant hall with a decay of tens of seconds. | 0: decay<br>1: damping<br>2: mix | 8 | 140 | 883 | 40,882 |
| `bloom` | The reverb grows slowly after each note, like a flower that opens. | 0: decay<br>1: damping<br>2: mix<br>3: bloom time | 8 | 84 | 637 | 23,520 |
| `chorale` | The plate tail sings a vowel, from "a" to "i". | 0: decay<br>1: damping<br>2: mix<br>3: vowel | 8 | 160 | 1,192 | 37,439 |
| `cloud` | Long diffusers with random modulation: the attack dissolves. | 0: decay<br>1: damping<br>2: mix<br>3: modulation | 8 | 96 | 907 | 42,814 |
| `dinamica` | A plate whose tail changes with how hard you play. | 0: decay<br>1: damping<br>2: mix<br>3: depth<br>4: threshold<br>5: rate | 8 | 141 | 1,188 | 37,439 |
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
| `semilla` | Cloud reverb with early reflections from a seed: each seed gives a different room. | 0: decay<br>1: damping<br>2: mix<br>3: seed<br>4: density<br>5: modulation | 8 | 196 | 1,513 | 42,934 |
| `shimmer` | A plate with +12 in the feedback: each turn goes up one octave. | 0: decay<br>1: damping<br>2: mix<br>3: shimmer amount | 8 | 108 | 1,037 | 41,539 |
| `shimmer_energia` | A shimmer that controls itself: the more octave it collects, the less it adds. | 0: decay<br>1: damping<br>2: mix<br>3: shimmer amount | 8 | 117 | 1,095 | 41,539 |
| `shimmer_escondido` | Hidden shimmer: the octave stays quiet while you play and comes up in the tail. | 0: decay<br>1: damping<br>2: mix<br>3: shimmer amount<br>4: ducking<br>5: tone | 8 | 139 | 1,239 | 41,539 |
| `shimmer_grave` | Downward shimmer: each turn goes down one octave and the tail becomes a deep organ. | 0: decay<br>1: damping<br>2: mix<br>3: shimmer amount | 8 | 108 | 1,037 | 41,539 |
| `shimmer_quinta` | Fifth shimmer: each turn goes up 7 semitones, like a chord that opens. | 0: decay<br>1: damping<br>2: mix<br>3: shimmer amount | 8 | 108 | 1,037 | 41,539 |
| `shoegaze` | A plate that saturates after the tail: a wall of warm noise behind the guitar. | 0: decay<br>1: damping<br>2: mix<br>3: saturation | 8 | 142 | 1,106 | 37,439 |
| `sostenido` | Automatic freeze: each new chord is captured and keeps sounding as a pad. | 0: layers<br>1: damping<br>2: mix<br>3: capture | 8 | 141 | 1,190 | 37,439 |
| `spring` | Spring reverb: the sound drips, with the treble before the bass. | 0: decay<br>1: damping<br>2: mix | 8 | 95 | 832 | 1,850 |

## Delay

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `aureo` | Fourteen echoes on the Fibonacci series, alternating left and right, that thicken into a clicking reverb. | 0: slope<br>1: feedback<br>2: mix<br>3: tone<br>4: width<br>5: diffusion | 8 | 141 | 1,096 | 42,259 |
| `bbd` | Dark analog echo: each repeat loses treble and saturates. | 0: time<br>1: feedback<br>2: mix<br>3: modulation | 8 | 44 | 408 | 14,674 |
| `bruma` | A four-head echo that blurs on each turn until it becomes a reverb. | 0: diffusion<br>1: feedback<br>2: mix<br>3: heads | 8 | 53 | 536 | 41,553 |
| `cinta` | Tape echo from 0.18 to 0.85 s with wow, flutter and saturation. | 0: time<br>1: feedback<br>2: mix<br>3: wow and flutter | 8 | 50 | 484 | 41,600 |
| `compas` | Echo with tap tempo and five note values: quarter, dotted eighth, eighth, triplet and sixteenth. | 0: time<br>1: feedback<br>2: mix<br>3: subdivision<br>4: second tap<br>5: tone | 8 | 135 | 885 | 32,769 |
| `dados` | Four echoes with random times and octaves; sw rolls the dice again. | 0: time<br>1: feedback<br>2: mix<br>3: probability<br>4: tone<br>5: width | 8 | 239 | 1,620 | 38,260 |
| `delay` | Clean digital echo from 20 to 690 ms, with tone in the feedback. | 0: time<br>1: feedback<br>2: mix<br>3: tone | 8 | 38 | 309 | 33,749 |
| `deriva` | An echo that drifts: the time jumps at random and glides to the new value. | 0: time<br>1: depth<br>2: mix<br>3: rate<br>4: glide<br>5: feedback | 8 | 128 | 969 | 33,796 |
| `dos_ecos` | Two echoes in rhythm, one clean and one tape, that cross and end in a diffuse cloud. | 0: time<br>1: feedback<br>2: mix<br>3: ratio<br>4: balance<br>5: diffusion | 8 | 142 | 1,131 | 41,258 |
| `ducking` | An echo that moves back while you play and comes back in the silences. | 0: time<br>1: feedback<br>2: mix<br>3: ducking | 8 | 51 | 394 | 33,749 |
| `eco_casero` | Home-built chip echo: clean at short times; dark, grainy and pumping when you make it longer. | 0: time<br>1: feedback<br>2: mix<br>3: dirt<br>4: modulation<br>5: tone | 8 | 124 | 1,002 | 41,492 |
| `enjambre` | A swarm of eight short echoes: it closes into a reverb or opens into single echoes. | 0: spread<br>1: feedback<br>2: mix<br>3: diffusion<br>4: tone<br>5: drift | 8 | 199 | 1,377 | 42,820 |
| `estelar` | Echo with a phaser inside the loop: each repeat sweeps more and the tail swirls. | 0: time<br>1: feedback<br>2: mix<br>3: depth<br>4: rate<br>5: resonance | 8 | 123 | 830 | 33,749 |
| `frenada` | Tape echo with a brake: press the switch and the tape stops, the echo falls to silence. | 0: time<br>1: feedback<br>2: mix<br>3: brake time<br>4: spin-up time<br>5: wow and flutter | 8 | 156 | 1,199 | 32,876 |
| `lata` | Oil can echo: short, murky and liquid, with a vibrato tied to the time. | 0: time<br>1: feedback<br>2: mix<br>3: depth<br>4: tone<br>5: oil | 8 | 90 | 768 | 18,931 |
| `lluvia` | Six irregular echoes that dissolve in allpass filters: a rain of notes. | 0: diffusion<br>1: feedback<br>2: mix | 8 | 46 | 364 | 35,385 |
| `oscilador` | Echo that oscillates by itself under a level ceiling; the time tunes the pitch. | 0: time<br>1: feedback<br>2: mix<br>3: smoothing<br>4: tone<br>5: level | 8 | 86 | 614 | 24,678 |
| `pingpong` | A stereo echo that jumps from one side to the other. | 0: time<br>1: feedback<br>2: mix | 8 | 38 | 353 | 40,874 |
| `probabilidad` | Eight echoes that play or stay silent by chance: a changing reverb or a pattern that never repeats. | 0: time<br>1: probability<br>2: mix<br>3: feedback<br>4: tone<br>5: smoothing | 8 | 220 | 1,450 | 34,456 |
| `reverse` | Reversed echo in grains of 0.17 s. | 0: tone<br>1: feedback<br>2: mix | 8 | 34 | 301 | 16,388 |
| `tambor` | A four-head magnetic drum echo: a rhythm that comes from the heads that are on. | 0: rate<br>1: feedback<br>2: mix<br>3: heads<br>4: age<br>5: tone | 8 | 173 | 1,328 | 37,656 |

## Modulation

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `armonico` | The lows and the highs pulse in opposite phase; with pot2, an echo after them. | 0: rate<br>1: depth<br>2: echo<br>3: frequency<br>4: shape<br>5: width | 8 | 125 | 847 | 17,101 |
| `chorus` | Three voices with moving delays. | 0: rate<br>1: depth<br>2: mix | 8 | 42 | 416 | 1,101 |
| `desplazador` | Echo that shifts its frequency on each pass: the tail goes up or down in a spiral. | 0: frequency shift<br>1: time<br>2: mix<br>3: feedback<br>4: tone<br>5: width | 8 | 110 | 864 | 33,767 |
| `dimension` | A chorus that makes the stereo wide and adds body, but the pitch does not wobble. | 0: mode<br>1: rate<br>2: mix<br>3: depth<br>4: crossfeed<br>5: tone | 8 | 94 | 795 | 505 |
| `flanger` | A very short moving delay with feedback: sweeping combs. | 0: rate<br>1: depth<br>2: mix<br>3: feedback | 8 | 31 | 266 | 247 |
| `orilla` | Slow random chorus with a low-pass gate that closes with each note. | 0: rate<br>1: depth<br>2: mix<br>3: smoothing<br>4: low-pass gate<br>5: sensitivity | 8 | 147 | 1,078 | 736 |
| `phaser` | Four allpass filters with a moving coefficient: sweeping notches. | 0: rate<br>1: depth<br>2: mix<br>3: feedback | 8 | 80 | 521 | 1 |
| `slicer` | It cuts the sound into rhythmic pulses, like a gate that opens and closes. | 0: rate<br>1: depth<br>2: duty cycle<br>3: smoothing | 8 | 37 | 262 | 1 |
| `tremolo` | The volume goes up and down; with pot2, from one side to the other. | 0: rate<br>1: depth<br>2: pan | 8 | 43 | 325 | 1 |
| `vibe` | Lamp vibe: four unequal phase stages with a sweep that rises fast and falls slowly. | 0: rate<br>1: depth<br>2: mix<br>3: feedback<br>4: shape<br>5: tone | 8 | 125 | 830 | 1 |
| `vibrato` | The pitch goes up and down. | 0: rate<br>1: depth<br>2: mix | 8 | 27 | 240 | 125 |

## Pitch

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `acople` | A held note slowly grows a saturated harmonic above it, like amp feedback. | 0: time<br>1: interval<br>2: mix<br>3: rise time<br>4: tone<br>5: level | 8 | 138 | 1,038 | 3,550 |
| `arcoiris` | Two pitch-shifted voices in a loop that regenerates and can self-oscillate. | 0: interval<br>1: second voice<br>2: mix<br>3: time<br>4: feedback<br>5: tone | 8 | 76 | 693 | 12,345 |
| `armonizador` | One voice at −12, −7, −5, +5, +7 or +12 semitones, with feedback. | 0: interval<br>1: feedback<br>2: mix | 8 | 55 | 450 | 4,100 |
| `arpegio` | Each note opens into a transposed arpeggio (1-3-5-8) that falls into a reverb. | 0: rate<br>1: notes<br>2: mix<br>3: mode<br>4: echo<br>5: decay | 8 | 163 | 1,259 | 42,851 |
| `doblador` | Two voices detuned by a few cents, one on each side: it widens the sound. | 0: detune<br>2: mix | 8 | 32 | 346 | 1,028 |
| `escalera` | An echo in which each repeat goes up or down an interval: a staircase. | 0: interval<br>1: feedback<br>2: mix<br>3: time | 8 | 67 | 582 | 39,313 |
| `espiral` | A reverb whose tail spirals up or down in pitch, with one interval on each side. | 0: interval<br>1: second voice<br>2: mix<br>3: time<br>4: feedback<br>5: decay | 8 | 171 | 1,455 | 42,878 |
| `octava` | Octaver: one octave down and one up, each with its own level. | 0: lower octave<br>1: upper octave<br>2: dry | 8 | 25 | 296 | 4,100 |

## Dynamics

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `arco` | Bow sustain: the note fades in, stays at a constant level and can move to its octave. | 0: sustain<br>1: rise time<br>2: mix<br>3: upper octave<br>4: tone<br>5: threshold | 8 | 122 | 897 | 2,052 |
| `compresor` | Compressor: it lowers the loud parts, keeps the soft ones and sustains the notes. | 0: threshold<br>1: compression<br>2: mix<br>3: gain | 8 | 57 | 394 | 1 |
| `puerta` | Noise gate: it silences the hum between notes and lets the playing through. | 0: threshold<br>1: release | 8 | 29 | 222 | 1 |
| `swell` | Each note starts in silence and rises, before a plate. | 0: decay<br>1: damping<br>2: mix<br>3: rise time | 8 | 116 | 983 | 37,439 |
| `swell_ritmico` | Each note rises with the curve and time you set, also to the beat of your foot, in a plate that sways. | 0: rise time<br>1: shape<br>2: mix<br>3: decay<br>4: drift<br>5: sensitivity | 8 | 216 | 1,611 | 37,439 |
| `violin` | Each note starts with no pick attack, as with a bow, and the vibrato comes later. | 0: rise time<br>1: time<br>2: mix<br>3: depth<br>4: rate<br>5: tone | 8 | 118 | 845 | 85 |

## Texture

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `granular` | A 4-voice granular cloud with a Hann window, octave pitch and freeze. | 0: length<br>1: diffusion<br>2: interval<br>3: mix | 8 | 188 | 1,209 | 32,769 |
| `lofi` | Fewer samples per second and fewer bits, with aliasing. | 0: sample rate<br>1: bits<br>2: mix<br>3: tone | 8 | 81 | 577 | 1 |
| `ringmod` | Ring modulator: it multiplies the guitar by a sine; it sounds metallic. | 0: frequency<br>2: mix | 8 | 33 | 236 | 1 |
| `saturacion` | Overdrive-type saturation: from a warm glow to a thick distortion. | 0: gain<br>1: tone<br>2: mix<br>3: level | 8 | 42 | 277 | 1 |
| `viento` | Gusts of filtered noise that whistle at random and blow harder when you play. | 0: rate<br>1: resonance<br>2: mix<br>3: sensitivity<br>4: frequency<br>5: level | 8 | 140 | 913 | 3,728 |

## Filter

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `ancho` | Makes a mono guitar wide in stereo and tilts the tone between bass and treble. | 0: width<br>1: tilt | 8 | 26 | 185 | 636 |
| `autowah` | Automatic wah: the harder you play, the higher the filter goes. | 0: sensitivity<br>1: resonance<br>2: mix | 8 | 43 | 295 | 1 |
| `filtro` | A resonant low-pass filter that goes up and down by itself, with an LFO. | 0: rate<br>1: resonance<br>2: mix<br>3: depth | 8 | 61 | 402 | 1 |

## Looper

| Program | What it does | Knobs | Presets | Instructions | Cycles | Memory |
|---|---|---|---|---|---|---|
| `erosion` | A tape loop that wears out on each pass: it loses treble and level and gains wow, grain and saturation. | 0: erosion<br>1: damping<br>2: mix<br>3: modulation<br>4: level<br>5: length | 8 | 161 | 1,043 | 32,769 |
| `looper` | A 0.67 s micro-looper with overdub, ½×, 2× and reverse. | 0: level<br>1: rate<br>2: direction<br>3: feedback | 8 | 87 | 576 | 32,769 |
| `mosaico` | A 0.67 s sound-on-sound loop that plays at ½×, 1× and 2× at the same time. | 0: lower octave<br>1: level<br>2: mix<br>3: upper octave<br>4: feedback<br>5: diffusion | 8 | 144 | 1,064 | 34,662 |
| `relevo` | A two-layer freeze: each press freezes a new chord and fades it in over the old one, with bend and vibrato. | 0: time<br>1: tuning<br>2: mix<br>3: vibrato<br>4: tone<br>5: level | 8 | 197 | 1,438 | 34,140 |
| `resbalon` | A free read head slips over what you just played, from −2× to 2×, with no recording. | 0: rate<br>1: feedback<br>2: mix<br>3: length<br>4: tone<br>5: time | 8 | 119 | 865 | 32,769 |
| `tartamudeo` | Each hard attack captures a short slice and repeats it, softer each time. | 0: threshold<br>1: length<br>2: mix<br>3: repeats<br>4: rate<br>5: tone | 8 | 188 | 1,240 | 32,769 |

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
| Loop filtrado | `looper` → `filtro` | 1,018 | 32,769 | 23 | 0 | fits |
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
