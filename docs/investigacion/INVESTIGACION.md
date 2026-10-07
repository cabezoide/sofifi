# Pedal ambient en FPGA (Sipeed Tang Primer 25K): investigación y propuesta

*Fecha: 2026-10-07.*

**Marcas de confianza:**
- **[V]**: verificado en una fuente primaria.
- **[?]**: incierto; conviene verificarlo.
- **[INF]**: inferencia técnica, no confirmada por el fabricante.

---

## 0. Resumen ejecutivo

1. **Nadie ha publicado un pedal ambient en Tang/Gowin.** No encontramos ninguna reverb ni efecto ambient de guitarra open source para Tang Primer 20K/25K. Sería un proyecto pionero.
2. **Los mejores pedales no publican su DSP**, pero todos se apoyan en una literatura conocida:
   - reverbs de Griesinger/Lexicon y el plate de Dattorro;
   - FDN de Jot;
   - el allpass loop de Keith Barr (FV-1);
   - pitch shifting por doble línea con crossfade;
   - granular y micro-loops;
   - cinta modelada con delay fraccional y saturación.

   Todo eso se reduce a **líneas de retardo + multiplicar-acumular + filtros de 1 polo**, que es justo lo que una FPGA hace bien.
3. **La Tang Primer 25K da para mucho.** Tiene 23 040 LUT4, 28 bloques DSP (multiplicador de 27×18 más otro de 12×12 en cada uno) y 1 008 Kbit de BSRAM. Con el **módulo SDRAM** de 32–64 MB caben looper, granular y delays de minutos. A 98,304 MHz hay **2 048 ciclos por muestra** a 48 kHz, es decir más de 50 000 MAC por muestra en teoría.
4. **Arquitectura recomendada:** varios **núcleos DSP microcodificados "FV-1 en esteroides"** más un motor granular/pitch dedicado y una CPU RISC-V pequeña para la interfaz. Así los efectos son *programas*: se pueden añadir sin resintetizar, y además se puede aprovechar el enorme catálogo de programas del FV-1.
5. **Golden models con licencia permisiva** que se pueden portar sin problemas: Clouds/Rings/Elements de Mutable (MIT), CloudSeed (MIT), dattorro-verb (MIT), Faust `jpverb`, `greyhole` y `zita_rev1` (MIT/STK), Airwindows (MIT), DaisySP (MIT) y los programas del FV-1 (Spin Open Reverb License).

---

## 1. Pedales de referencia y qué hace cada uno "por dentro"

| # | Pedal | Qué lo hace especial | Concepto DSP a emular |
|---|---|---|---|
| 1 | **Strymon BigSky / BigSky MX** | Estándar de la industria | Cloud, Bloom (cadena larga de difusores + feedback), Shimmer, Chorale (formantes), Swell, Nonlinear y doble motor. SHARC en el clásico; ARM a 800 MHz con 24 bit/96 kHz en el MX [V] |
| 2 | **Meris Mercury7 / MercuryX** | Sonido Lexicon 224 de *Blade Runner* | **Pitch Vector dentro del tanque** (−8va, ±detune, +5ª, +8va), auto-swell, Ultraplate/Cathedra. MercuryX trabaja a 48 kHz [V] |
| 3 | **Hologram Microcosm** | Referencia del granular | Micro-loops a varias velocidades, nubes de grains, glitch y multi-delay con pitch, looper de 60 s, Hold |
| 4 | **Chase Bliss MOOD MkII** | Experimental | **Reloj de muestreo variable** (pitch/tiempo/fidelidad), micro-looper siempre grabando, canales con realimentación cruzada |
| 5 | **Eventide Blackhole / Shimmer / H90** | Clásicos del H8000 | **Realimentación alrededor de toda la reverb**, Gravity inversa, Freeze frente a Infinite. Shimmer con **dos pitch A/B desafinados alrededor de 1 200 c** dentro del bucle [V] |
| 6 | **Strymon Volante / TimeLine** | Cinta y tambor | 4 cabezas, wow/flutter ("Mechanics"), desgaste, saturación y low-cut en el bucle |
| 7 | **Walrus Slöer / Fathom** | Ambient estéreo | Modos Dark (−8va), Rise (swell), Dream (latch), **Rain (taps audibles con poca difusión)**, Light (shimmer), control de sample rate |
| 8 | **Strymon Cloudburst / NightSky** | Síntesis reverberante | Ensemble con análisis en 48 bandas y parciales sintéticos; secuenciador de tamaño y pitch |
| 9 | **OBNE Dark Star** | Pad lo-fi | Dos pitch de ±2 oct con realimentación global y *crush* (reducción de SR con aliasing) |
| 10 | **Red Panda Particle / Tensor** | Granular y time-warp | Tamaño y densidad de grano, pitch ±1 oct cuantizado, reverse, tape-stop, stretch 4:1 |
| 11 | **Chase Bliss Lossy / Blooper / Habit / Onward** | Degradación y loops | Artefactos de códec (MDCT/STFT [INF]), packet loss/repeat, freeze espectral |
| 12 | **EHX Oceans 12 / Canyon / Cathedral** | Mucho por poco dinero | Auto-infinito según la ejecución, reverb con **resonadores** sintonizados, octava acumulativa |
| 13 | **Empress Reverb / Zoia**, **Count to 5**, **DBA**, **Gamechanger LIGHT** | Nichos | 48 kHz/32 bit; remuestreo de buffers; fuzz en repeticiones; muelle óptico (analógico) |

**Plataforma de referencia DIY: Spin FV-1.** Ejecuta 128 instrucciones por muestra, tiene 32K palabras de RAM de delay (≈1 s a 32 kHz) y ADC/DAC de 24 bit [V]. Está detrás de muchísimos pedales boutique. Si eso alcanza para reverbs de calidad comercial, una FPGA con 16× más instrucciones y 1 000× más memoria va muy sobrada.

### 1.1 Catálogo de algoritmos (lo que hay que implementar)

**Reverbs**
- **Plate de Dattorro (1997):**
  - Estructura: predelay → LPF de "bandwidth" → 4 allpass de difusión → tanque en figura de ocho, con 2 ramas, allpass **modulados**, damping LPF y decay.
  - Salida estéreo con 7 taps por canal.
  - Paper: https://ccrma.stanford.edu/~dattorro/EffectDesignPart1.pdf
- **Lexicon/Griesinger:**
  - Difusión de entrada → tanque recirculante con **modulación aleatoria** de los delays, que mata el sonido metálico.
  - Es el ADN de Cloud, Mercury7 y Cathedra.
- **FDN de Jot:**
  - N líneas (8 o 16) con longitudes primas entre sí y una matriz Hadamard/Householder.
  - Un filtro de absorción por línea, con g = 10^(−3·m/(T60·fs)).
  - Da halls enormes y suaves; Supermassive es de esta familia.
- **Allpass loop de Keith Barr:**
  - Un anillo [AP → AP → delay → LPF → ×krt] con varias inyecciones y taps.
  - Es la reverb del FV-1 y de los Alesis.
- **CloudSeed:** varias líneas paralelas, cada una con delay modulado, cadena de difusores y filtros. Ideal para "Cloud".
- **Spring:** cadena larga de allpass de dispersión (*chirp*) más un delay con feedback.
- **Nonlinear/gate/reverse falso:** taps con una envolvente de ganancia.

**Shimmer:** un pitch shifter de +12 (o +7/+19) **dentro de la realimentación**. Hay tres variantes:
- shifter en el bucle post-reverb, al estilo Eventide, con 2 voces desafinadas que generan batido;
- shifter intra-tanque, al estilo Mercury7;
- shimmer espectral, como el BigSky MX [INF], que es caro.

**Bloom.** Hay dos interpretaciones:
- *Estructural* (Strymon): muchos difusores en serie y feedback, de modo que la envolvente crece sola.
- *Por envolvente*: un seguidor de la entrada controla el send o el decay.

**Pitch shifting**
1. **Doble tap con crossfade** (familia H910 y FV-1): barato y perfecto para shimmer.
2. **Granular OLA**, para Particle y Microcosm.
3. **Remuestreo**, es decir leer el buffer a otra velocidad, como hacen MOOD, Count to 5 y el tape-stop.
4. **Phase vocoder/STFT**: es polifónico, pero caro.

**Granular / micro-loop / glitch**
- Buffer circular siempre grabando.
- Planificador de grains con densidad, tamaño de 10 a 500 ms, spray, pitch cuantizado y probabilidad de reverse.
- Ventana Hann.
- Glitch: stutter, reordenación de bloques y dropouts.

**Freeze / Infinite**
- **Freeze:** ganancia del tanque = 1 con la entrada cortada.
- **Infinite:** ganancia del tanque = 1 con la entrada abierta, que acumula capas.
- En ambos casos hacen falta un **limitador suave en el bucle** y modulación interna para que el sonido no quede estático.

**Cinta (Volante/Magneto)**
- Delay fraccional modulado por:
  - wow: 0,3–2 Hz;
  - flutter: 5–20 Hz;
  - deriva aleatoria.
- En el bucle: `tanh` + HPF/LPF.
- Además: hiss, dropouts y varias cabezas.

**Lo-fi**
- Reducción de bits.
- Sample & hold **sin** antialias, que produce aliasing.
- Códec simulado (Lossy): MDCT/STFT con descarte de bins, *packet loss/repeat* y *phase jitter* [INF].

**Swell:** un detector de ataque rearma la ganancia a 0 y aplica una rampa de 50 ms a varios segundos, antes o después de la reverb.

**Coros, formantes y resonadores:** banco de biquads bandpass (vocales, como Chorale) o resonadores modales (Rings, Oceans 12 Resonant).

**Literatura esencial**
- Dattorro, *Effect Design* Parte 1 y 2 (la 2 trata delays modulados e interpolación).
- Griesinger (1989).
- Jot y Chaigne (1991).
- Moorer (1979).
- J. O. Smith, *PASP*.
- Blog de Valhalla DSP. Imprescindibles las notas de diseño de Shimmer y el post sobre difusión y artefactos metálicos.
- Knowledge base de Spin Semiconductor (Keith Barr).

---

## 2. Recursos open source

### 2.1 Para portar a HDL: licencia permisiva

| Recurso | Licencia | Qué aporta |
|---|---|---|
| Mutable Instruments `eurorack` (Clouds, Rings, Elements): https://github.com/pichenettes/eurorack | MIT (código STM32) | `fx_engine` + `reverb.h`: reverb tipo Griesinger en un buffer circular de 16 bit. **Se traduce casi 1:1 a BRAM + MAC.** También granular, WSOLA, resonadores. *Beads no está publicado.* |
| CloudSeed / CloudSeedCore (Valdemar Erlingsson) | MIT | Reverb "Cloud" con líneas paralelas; muy paralelizable |
| el-visio/dattorro-verb | MIT | Plate de Dattorro pequeño en C; ideal para pasar a punto fijo |
| Faust `reverbs.lib` | `jpverb` y `greyhole`: MIT; `zita_rev1` y `dattorro_rev`: STK (estilo MIT) | Reverbs de altísima calidad; Faust genera C para el modelo de referencia |
| Airwindows (Galactic, kCathedral, kPlate, ToTape, MatrixVerb…) | MIT | Fuentes cortas y con mucho carácter |
| DaisySP | MIT | Delay, SVF, pitchshifter, chorus… |
| bkshepherd/DaisySeedProjects | MIT | **Catálogo completo** de módulos ambient para pedal: cloudseed, dattorro, granular, tape, spectral, pitch… |
| GuitarML (DaisyEffects, FunBox) | MIT | Pedales completos con PCB KiCad |
| Programas FV-1 (spinsemi, wir35/spin-programs) + asfv1 / disfv1 | Spin Open Reverb License / MIT | Cientos de reverbs y efectos probados en hardware |
| Freeverb | Dominio público | La más fácil, aunque suena metálica |
| Signalsmith Stretch | MIT | Pitch/stretch polifónico (STFT) para una v2 |

**Solo estudiar, no copiar.** Llevar estos a HDL contagia su licencia:
- Surge XT (GPL-3), que incluye Nimbus, es decir Clouds.
- ValleyAudio Plateau (GPL-3).
- ChowTape (GPL-3).
- DaisySP-LGPL, que incluye ReverbSc de Costello.
- Tiliqua y eurorack-pmod: CERN-OHL-S, licencia recíproca.
- Cores de ZipCPU (GPL/LGPL).

### 2.2 FPGA / HDL de referencia
- **apfaudio/tiliqua** (Amaranth, ECP5): delays y **difusores en PSRAM externa con arbitraje**, pitch shift, STFT. Es lo más parecido a lo que queremos. Se puede estudiar; la licencia es CERN-OHL-S.
- **Muzhou-exe/FPGA-Based-Guitar-Digital-Multi-effect-pedal** (MIT): Basys3, I2S a 48 kHz/24 bit, Schroeder, delay en BRAM y tap tempo.
- **klumw/tang_nano_9k_dsp** (Apache-2.0): plantilla I2S RX/TX en Gowin.
- **ppy2/gowin-dsd-pcm-bridge** (MIT): I2S a 192 kHz **sobre la propia Tang Primer 25K**.
- **ZiyangYE/LicheeTang25k_SDRAM**: controlador para el módulo SDRAM de la 25K (≈260 MB/s secuencial).
- **nand2mario/sdram-tang-nano-20k** (Apache-2.0): controlador SDRAM probado.
- **alexforencich/verilog-axis** (MIT): FIFOs y arbitraje.
- **Cores I2S:** escribir uno propio son ~60 líneas y evita depender de cores GPL.

### 2.3 Front-end analógico
- **pedalSHIELD MEGA** (ElectroSmash): buffer y preamplificador de entrada, filtros antialias y reconstrucción. Es una buena plantilla.
- **PedalPCB Terrarium:** buffer con TL072. Lección aprendida: poner un **RC de ~22 kHz a la salida** (3k3 + 2n2) para el ruido del códec.
- **Belton brick y PT2399** (Electric Druid, ElectroSmash, Coda): para entender los "lo-fi" analógicos. No hacen falta aquí.

---

## 3. La placa: Sipeed Tang Primer 25K

| Recurso | Valor |
|---|---|
| FPGA | GW5A-LV25MG121 (Arora V, 22 nm) [V] |
| LUT4 / FF | 23 040 / 23 040 |
| BSRAM | **1 008 Kbit = 56 bloques de 18 Kbit** (1K×18, 512×36, SDP, DP…) |
| SSRAM (LUTRAM) | 180 Kbit (depende de la versión del chip [?]; no contar con ella) |
| DSP | **28 bloques**, cada uno con 27×18 + 12×12, pre-sumador y ALU de 48 bit con cascada |
| PLL | 6 (VCO de 700–1 400 MHz) |
| ADC interno | 1 ADC sigma-delta de 10 bit, 8 canales, 0–1 V. Sirve para potenciómetros; falta confirmar qué pines llegan al Dock [?] |
| Reloj | Cristal de 50 MHz |
| Memoria externa | **No trae.** El módulo **TANG_SDRAM** va en el conector 40P (2×32 MB, 16 bit, 143 MHz) |
| E/S en el Dock | 3 PMOD (24 E/S) + 40P (lo ocupa la SDRAM) + USB-C con depurador |
| Precio aprox. | Core + Dock ≈ 29 USD; SDRAM ≈ 10 USD [precios de 2024] |

**Toolchain**
- **Gowin EDA Education:** gratuita y compatible con la GW5A-25 desde la v1.9.9Beta-4 [V].
- **Yosys + nextpnr-himbaechel + apicula:** funcionan en la Primer 25K en 2026. BSRAM, DSP y PLLA están soportados (apicula 0.34, 2026-10-02), aunque la madurez es media. Hay un issue abierto con la PLLA (#427).
- **Recomendación:** usar Gowin EDA como referencia y el flujo libre en CI.
- **LiteX** tiene target oficial `sipeed_tang_primer_25k` (VexRiscv + SDRAM).

### 3.1 Presupuesto de memoria (48 kHz)

| Memoria | Capacidad útil | Uso |
|---|---|---|
| BSRAM (56×1K×18) | ≈57 000 muestras ≈ **1,19 s mono** a 18 bit; en la práctica unos 0,5–0,8 s libres | Difusores, allpass, plate de Dattorro (≈35k muestras), memoria de microcódigo, CPU |
| SDRAM de 32 MB (muestras de 32 bit) | ≈175 s mono; con 64 MB, ≈175 s estéreo | Looper, granular, delays largos, tanques FDN grandes |
| Ancho de banda de la SDRAM | ≈340 accesos aleatorios de 32 bit por muestra; ≈1 350 en ráfaga | Suficiente para 16–32 taps + 16 grains + looper estéreo |

### 3.2 Presupuesto de cómputo
- Con reloj de sistema de **98,304 MHz** (24,576 MHz × 4), cada muestra a 48 kHz dura exactamente **2 048 ciclos**.
- Un solo DSP multiplexado en el tiempo hace ≈2 000 MAC por muestra, más que todo el FV-1 (128 instrucciones). Con 28 DSP el techo teórico es de ≈57 000 MAC por muestra.
- **El cuello de botella real son los puertos de BSRAM y la lógica de control, no los multiplicadores.**

---

## 4. Propuesta de arquitectura

```
 Guitarra ─► Front-end analógico ─► ADC ┐                          ┌─► DAC ─► Buffer salida L/R ─► Amp
 (1 MΩ, 9→18 V, ganancia)  (PCM3060/CS4272)                           │
                                         ▼                          │
                         ┌───────────────── FPGA GW5A-25 ───────────┴──────────────┐
                         │  I2S maestro (MCLK/BCLK/LRCK desde PLL, un solo dominio) │
                         │                                                         │
                         │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
                         │  │ Núcleo A │─►│ Núcleo B │─►│ Núcleo C │─►│ Núcleo D │ │  ◄─ matriz de ruteo
                         │  │ dinámica │  │ pitch /  │  │  delay / │  │  reverb  │ │     serie/paralelo
                         │  │ swell,   │  │ granular │  │  cinta   │  │ + freeze │ │     + feedback cruzado
                         │  │ lo-fi    │  │ (motor   │  │          │  │          │ │
                         │  └──────────┘  │ dedicado)│  └──────────┘  └──────────┘ │
                         │       │        └──────────┘       │              │      │
                         │       └──────── BSRAM (líneas cortas) ───────────┘      │
                         │                       │                                 │
                         │        Árbitro SDRAM (prefetch 1 muestra) ─► SDRAM 32–64 MB
                         │                                                         │
                         │  RISC-V (VexRiscv/PicoRV32): presets, UI, MIDI, carga de │
                         │  microcódigo desde flash, LFOs lentos, suavizado        │
                         └──────┬──────────┬───────────┬──────────┬────────────────┘
                              OLED     Pots (ADC     Footswitch  MIDI in / Exp. pedal
                                       SPI MCP3208)   ×3 + relé
```

### 4.1 Idea clave: núcleos DSP microcodificados compatibles con FV-1 (y ampliados)

En lugar de escribir cada efecto en Verilog, se escribe **un procesador de efectos pequeño** y se replica:
- **ISA:** un superconjunto de la del FV-1: `RDAX`, `WRAX`, `RDA`, `WRA`, `MULX`, `LOG`, `EXP`, `SOF`, `RDFX`, `WRAP`, `CHO` (interpolación con LFO)… Así se pueden **ensamblar programas `.spn` existentes** con `asfv1` y usar **SpinCAD Designer** como editor visual.
- **Ampliaciones:**
  - 1 024–2 048 instrucciones por muestra en vez de 128;
  - acumulador de 48 bit con datos de 24 bit y coeficientes de 18 bit (encaja en el 27×18);
  - interpolación **cúbica (Hermite)** para delays modulados;
  - más LFOs, incluido ruido filtrado;
  - `tanh` por tabla;
  - acceso a SDRAM para líneas largas.
- **Lecturas de SDRAM sin latencia:** las direcciones de un programa son deterministas, así que el árbitro puede **precargar las lecturas de la muestra n+1** mientras se calcula la n.
- **Ventaja:** cada efecto nuevo es *software* que la CPU carga en caliente, y no hay que resintetizar.

**Motor granular/pitch dedicado** (hardware fijo):
- 16 grains con ventana Hann en tabla.
- Lectura fraccional desde SDRAM, con pitch por paso de fase y reverse.
- Sirve para granular, micro-loops, shimmer de calidad (las dos voces se suman en la realimentación de la reverb), octavador, tape-stop y looper con velocidad variable.

### 4.2 Estimación de recursos [INF: estimación, hay que confirmarla sintetizando]

| Bloque | LUT4 | DSP | BSRAM (bloques de 18K) |
|---|---|---|---|
| RISC-V (VexRiscv min) + bus + periféricos (SPI, I2C, UART MIDI, GPIO) | ~3 000 | 0–4 | 8 (16 KB) |
| 4 núcleos DSP microcodificados (MAC, interpolación cúbica, LOG/EXP, LFOs) | ~8 000 | 8–12 | 8 (microcódigo de 1K×36 ×4) + 4 (registros) |
| Motor granular/pitch de 16 voces | ~3 000 | 4–6 | 2 (ventanas) |
| Controlador SDRAM + árbitro + prefetch | ~1 800 | 0 | 2 (FIFOs) |
| I2S, relojes, suavizado de parámetros, envolventes, medidores | ~1 000 | 1–2 | 0 |
| **Líneas de retardo en BSRAM** | — | — | **~30** (~0,6 s) |
| **Total** | **~17 000 / 23 040 (≈74 %)** | **~13–24 / 28** | **~54 / 56** |

Queda margen para un **núcleo FFT** (por ejemplo radix-2 de 1 024 puntos con 2–4 DSP) en una v2. Habilitaría freeze espectral, un shimmer polifónico y emulación tipo *Lossy*. Si falta BSRAM, se pueden mover tanques de reverb a SDRAM o bajar los difusores a 16 bit.

### 4.3 Lista de efectos ("todo lo que quepa")

**Dinámica y textura (núcleo A)**
- Noise gate.
- Compresor.
- **Swell** con ataque de 50 ms a 5 s, como Rise o el auto-swell del Mercury7.
- Seguidor de envolvente, que sirve como fuente de modulación global.
- **Lo-fi:** reducción de bits, sample & hold con aliasing (Crush del Dark Star) y saturación.

**Pitch y granular (motor dedicado + núcleo B)**
- Octavador: −1, +1 y +2.
- Dual pitch de ±2 oct con realimentación global (tipo Dark Star).
- **Granular** al estilo Microcosm/Particle: densidad, tamaño, spray, pitch cuantizado (8vas, 5ªs, escala) y probabilidad de reverse.
- **Micro-loops** Mosaic/Tunnel: varias cabezas a ½×, 1× y 2×.
- Glitch: stutter, reordenación de bloques y dropouts.
- **Hold/freeze granular.**

**Delay (núcleo C, SDRAM)**
- **Cinta** al estilo Volante: 4 cabezas, wow/flutter/deriva, saturación `tanh` en el bucle, HPF/LPF, hiss y desgaste.
- BBD oscuro.
- Digital limpio y ping-pong.
- **Reverse delay** con doble buffer y crossfade.
- **Multitap "Rain"**: taps rítmicos que se difuminan con allpass.
- Tap tempo y subdivisiones.
- Delays de hasta decenas de segundos.

**Reverb (núcleo D)**
1. **Plate**: Dattorro con modulación (Ultraplate).
2. **Hall**: FDN de 8 líneas Householder con T60 por bandas (Lexicon/Cathedra).
3. **Cloud**: tipo CloudSeed, con difusores largos y modulación aleatoria.
4. **Bloom**: cadena larga de difusores con feedback, más bloom por envolvente opcional.
5. **Shimmer**:
   - shifter en el bucle con +12, +7/+19 o −12;
   - 2 voces desafinadas a ±5–10 cents al estilo Eventide;
   - modo intra-tanque al estilo Mercury7.
6. **Blackhole**: feedback alrededor de toda la reverb, Gravity inversa y tamaño gigante.
7. **Swell / Nonlinear / Reverse / Gate**.
8. **Spring**: chirp con allpass de dispersión.
9. **Chorale**: banco de 3–5 biquads de formante (vocales) sobre la cola.
10. **Resonant**: banco de resonadores modales sintonizado a una tonalidad (Rings/Oceans 12).

**Global**
- **Freeze** (tanque = 1, entrada cortada) e **Infinite** (tanque = 1, entrada abierta), con limitador suave en el bucle.
- **Looper** estéreo de 60 s o más, con overdub, reverse y velocidad ½×/2× (MOOD/Blooper).
- Ruteo serie o paralelo y **feedback cruzado entre motores** (MOOD).
- *Spillover* de colas al cambiar de preset.
- Tilt EQ y ancho estéreo.
- **"Clock" variable** al estilo MOOD: remuestrear el buffer para acoplar pitch, tiempo y fidelidad.

### 4.4 Claves para que suene *hermoso* (no solo que funcione)
- **Precisión:**
  - datos de 24 bit, acumuladores de 48 bit y coeficientes de 18 bit;
  - líneas de retardo de al menos 18 bit en BSRAM, 24 o 32 bit en SDRAM;
  - un poco de dither o ruido de −120 dB en los bucles largos para evitar *limit cycles*.
- **Modulación:**
  - usar **ruido filtrado lento (random walk) + seno**, no solo seno;
  - interpolación **cúbica**, o allpass para modulación lenta. La lineal opaca y hace zumbar.
- **Longitudes:** de delay mutuamente primas, para evitar resonancias metálicas.
- **Damping:** dentro del bucle, para que las colas se oscurezcan como en una sala real.
- **Suavizado de parámetros** con un filtro de 1 polo de ~20 ms. Sin él aparecen *zipper noise* y clics al girar los potenciómetros.
- **Freeze e Infinite:** necesitan un limitador suave (`tanh` o *soft knee*) en el bucle para que nunca exploten.
- **Shimmer:** poner un HPF y un LPF en el bucle del shifter. Sin ellos, el sonido se vuelve "chillón".
- **Front-end analógico:**
  - entrada de 1 MΩ con TL072/OPA1678, idealmente con **bomba de carga de 9 → 18 V** para tener headroom;
  - **relé de bypass** (true bypass o buffered) con *trails*;
  - RC de ~22 kHz a la salida.
- **Sample rate:** 48 kHz es el estándar de Eventide, MercuryX y Empress. 96 kHz no aporta nada en reverbs y reduce a la mitad el presupuesto.

---

## 5. Hardware recomendado (BOM orientativo)

| Componente | Opción |
|---|---|
| FPGA | Tang Primer 25K + Dock |
| Memoria | Módulo Sipeed TANG_SDRAM (en el 40P). **No** es compatible con el MiSTer SDRAM v3 |
| Audio, fase 1 (prototipo) | **Digilent Pmod I2S2** (CS5343 + CS4344, 24 bit, se enchufa en un PMOD), o módulos PCM1808 + PCM5102A |
| Audio, fase final | Placa propia con **PCM3060** (99/104 dB) o **CS4272** (114 dB) + oscilador de 24,576 MHz |
| Reloj de audio | 24,576 MHz en la placa de audio como entrada de reloj de la FPGA → PLL ×4 = 98,304 MHz (2 048 ciclos por muestra exactos). Alternativa con el cristal de 50 MHz: MCLK = 12,5 MHz → fs = 48,828 kHz |
| Potenciómetros | MCP3208 (SPI, 12 bit, 8 canales) en un PMOD. Se puede usar el ADC interno si los pines están accesibles |
| Interfaz | OLED SSD1306/SH1106 128×64 + encoder con pulsador |
| Pie | 3 footswitches (bypass, tap/freeze, preset/looper) + relé de bypass |
| Extras | Entrada de pedal de expresión (TRS), MIDI IN (optoacoplador 6N138), salida estéreo |
| Pines | 3 PMOD: (1) audio I2S, (2) SPI ADC + OLED, (3) footswitches, LEDs, MIDI y relé |

---

## 6. Hoja de ruta

1. **Fase 0, modelo de referencia.**
   - Python o C con punto fijo *bit-exact*.
   - Portar Dattorro (el-visio), la reverb de Clouds, CloudSeed y un shimmer de doble tap.
   - Procesar WAVs de guitarra y comparar a oído contra los plugins de referencia.
2. **Fase 1, "hola audio".**
   - I2S con Pmod I2S2, passthrough y medición de latencia y ruido.
   - Controlador SDRAM (ZiyangYE) + delay de 10 s.
3. **Fase 2, núcleo DSP microcodificado.**
   - ISA tipo FV-1 + ensamblador en Python (o adaptar `asfv1`).
   - Testbench con Verilator/cocotb que procese WAV y compare contra el modelo de la fase 0.
   - Correr programas `.spn` existentes como prueba de fuego.
4. **Fase 3, efectos núcleo.** Plate, Hall, Cloud, Shimmer, cinta y Freeze.
5. **Fase 4, motor granular/pitch.** Granular, micro-loops, octavas y looper.
6. **Fase 5, interfaz y producto.**
   - RISC-V con presets, OLED, MIDI y expresión.
   - PCB de audio + front-end + caja 1590BB/125B.
7. **Fase 6 (v2).** Núcleo FFT para freeze espectral, shimmer polifónico y emulación Lossy.

---

## 7. Fuentes principales

**Literatura**
- Dattorro: https://ccrma.stanford.edu/~dattorro/EffectDesignPart1.pdf y https://ccrma.stanford.edu/~dattorro/EffectDesignPart2.pdf
- Valhalla DSP:
  - https://valhalladsp.com/2011/01/21/reverbs-diffusion-allpass-delays-and-metallic-artifacts/
  - https://www.valhalladsp.com/shimmer/ValhallaShimmerNotes.pdf
- Griesinger (1989): https://freeverb3-vst.sourceforge.io/doc/10.1.1.72.5367.pdf
- J. O. Smith, PASP: https://ccrma.stanford.edu/~jos/pasp/
- Spin FV-1, knowledge base: https://www.spinsemi.com/knowledge_base/effects.html
- Análisis de programas FV-1: https://forum.pedalpcb.com/threads/high-level-analysis-of-some-common-fv-1-reverb-programs.28802/

**Fabricantes**
- Eventide, H9 Algorithm Guide: https://downloads.eventideaudio.com/Product+Manuals/H9AlgorithmGuide+V12.pdf
- Strymon, Bloom: https://www.strymon.net/?p=6103
- Meris, MercuryX: https://www.meris.us/product/mercuryx/
- Lossy (Goodhertz): https://manuals.goodhertz.com/3.13/lossy/

**Código**
- https://github.com/pichenettes/eurorack
- https://github.com/ValdemarOrn/CloudSeed
- https://github.com/el-visio/dattorro-verb
- https://github.com/grame-cncm/faustlibraries
- https://github.com/airwindows/airwindows
- https://github.com/bkshepherd/DaisySeedProjects
- https://github.com/ndf-zz/asfv1
- https://github.com/HolyCityAudio/SpinCAD-Designer
- https://github.com/apfaudio/tiliqua

**Hardware**
- Sipeed, Primer 25K: https://wiki.sipeed.com/hardware/en/tang/tang-primer-25k/primer-25k.html
- Gowin, datasheet DS1103: https://cdn.gowinsemi.com.cn/DS1103E.pdf
- Apicula, ejemplos GW5A: https://github.com/YosysHQ/apicula/tree/master/examples/gw5a
- SDRAM de la 25K: https://github.com/ZiyangYE/LicheeTang25k_SDRAM
- LiteX: https://github.com/litex-hub/litex-boards
- Digilent Pmod I2S2: https://digilent.com/shop/pmod-i2s2-stereo-audio-input-and-output

**Pendiente de verificar**
- Pines del ADC interno accesibles en el Dock.
- Fmax real de DSP y BSRAM.
- Precios actuales.
- Coeficientes exactos de Dattorro (tomarlos del PDF).
- Qué pedales comerciales usan FV-1. No está confirmado para ninguno de la lista: Dark Star, Slöer y Lore son solo sospechas.

---

## 8. Plan con el hardware actual: Tang Primer 25K + Dock + microSD de 64 GB, **sin SDRAM**

### 8.1 ¿Puede la microSD sustituir a la SDRAM? **No como memoria de delay. Sí como almacenamiento.**

| | SDRAM | microSD |
|---|---|---|
| Ancho de banda | ~260 MB/s | Modo SPI ~2–3 MB/s; SD de 4 bit a 25–50 MHz da 12–25 MB/s |
| Latencia | ~100 ns | Lectura de **ms**. Escritura con **picos de hasta 250 ms** (la especificación SDHC lo permite por la recolección de basura interna) |
| Desgaste | Ninguno | Escrituras continuas = desgaste de la flash |

Una reverb o un delay con realimentación necesita leer y escribir cada muestra con latencia determinista. Con la SD, haría falta un FIFO de más de 250 ms por stream, lo que se come toda la BSRAM. **Usos correctos de la microSD:**
- **Presets y programas de efectos** (microcódigo), cargados en caliente por la CPU.
- **Tablas**: ventanas, wavetables, IRs cortas o drones/samples para reproducir.
- **Grabar la salida a WAV**, para escuchar y depurar los algoritmos en el PC. Es muy útil.
- **(Experimental, fase tardía)** un looper largo en streaming secuencial: escribir y leer bloques grandes con pre-borrado (ACMD23) y FIFOs de unos 170 ms. Puede funcionar con una tarjeta buena (A1/A2, U3), pero sin garantías.

### 8.2 Presupuesto de BSRAM (todo el audio vive aquí)

**Reserva de bloques de 18 Kbit:**
- CPU mínima (FemtoRV32 o PicoRV32, 8 KB): 4 bloques.
- Microcódigo: 4 bloques.
- Buffer de sector SD y FIFOs: 2 bloques.
- Tablas (seno, Hann, `tanh`, log/exp): 2 bloques.
- **Quedan unos 44 bloques = 45 056 palabras de delay.**

**Duración de esas 45 056 palabras según el formato:**

| Frecuencia de muestreo interna | 18 bit (calidad completa) | 9 bit μ-law (modo 2K×9, lo-fi) |
|---|---|---|
| 48,8 kHz | 0,92 s | 1,85 s |
| 32 kHz (como el FV-1) | 1,41 s | 2,82 s |
| 24 kHz | 1,88 s | 3,75 s |

**Trucos para estirarla:**
- Correr la **reverb a 32 kHz** con diezmado e interpolación half-band. En ambient la cola se amortigua por encima de 10–12 kHz de todos modos, y es lo que hace el FV-1.
- Guardar **delays largos en 9 bit μ-law**. El ruido queda enmascarado y suena "a cinta".
- **La memoria se reparte por preset, como en el FV-1.** Cada programa dispone de *toda* la RAM de delay, así que el preset "Shimmer gigante" usa los 0,9–1,4 s para su tanque y el preset "Granular" la usa como buffer de grains.
- Opcional: la SSRAM (180 Kbit, si el chip la tiene [?]) para allpass cortos.

**Ejemplos de reparto:**
- **Plate de Dattorro a 32 kHz** ≈ 24 200 palabras (54 %). Deja unas 21 000 para predelay, el shifter de shimmer (~2 400) y un eco.
- **Hall FDN de 8 líneas** ≈ 15–25k palabras.
- **Delay de cinta lo-fi**: hasta ~3,7 s a 24 kHz en 9 bit.
- **Micro-looper o granular**: ~1,4–2,8 s. Es un "micro"cosmos de verdad.

### 8.3 Reloj sin cristal de audio
- El cristal de 50 MHz no da 48 kHz exactos, pero hay una solución muy limpia:
  - **reloj de sistema de 100 MHz** (PLL ×2);
  - **MCLK = 12,5 MHz** (÷8) = 256·fs, que da **fs = 48,828 kHz**;
  - **2 048 ciclos de reloj por muestra, exactos.**
- El PCM1808, el PCM5102A y el CS5343/CS4344 funcionan sin problema a esa frecuencia. Para un pedal standalone, el 1,7 % de desvío respecto a 48 kHz es irrelevante.

### 8.4 Arquitectura simplificada (cabe sobrada en la 25K)
- **Un núcleo DSP tipo FV-1 ampliado:**
  - 2 048 instrucciones por muestra (16× el FV-1) a una instrucción por ciclo;
  - acumulador de 48 bit, datos de 24 bit y coeficientes de 18 bit;
  - `RDA`/`WRA` con interpolación cúbica, 4–8 LFOs (seno y ruido filtrado), `LOG`/`EXP`/`tanh`;
  - opcionalmente, ejecutar dos programas intercalados con dos particiones de memoria, para encadenar efectos.
- **Shimmer y octavas** con pitch shifter de doble tap: no necesita hardware extra porque cabe en microcódigo, igual que en el FV-1.
- **Granular de 4–8 voces** como bloque pequeño de hardware, o en microcódigo. Se puede dejar para una fase posterior.
- **CPU pequeña**: lectura de potenciómetros, footswitches, OLED, presets desde la SD y carga del microcódigo.
- **Estimación** [INF]: ~8–11k LUT4 (≈40–50 %), 4–8 DSP y ~56 bloques de BSRAM. Queda margen para un segundo núcleo si se quita memoria a los delays.

### 8.5 Lo que **falta comprar** (barato) para hacer sonar algo
1. **Códec de audio I2S.** Es imprescindible: la placa no tiene ni ADC ni DAC de audio. Opciones:
   - módulos **PCM1808 (ADC) + PCM5102A (DAC)**, ~5–10 USD los dos, cableados a un PMOD;
   - o el **Digilent Pmod I2S2**, que se enchufa directo.
2. **Buffer de entrada para la guitarra.** El ADC espera señal de línea y la impedancia baja carga las pastillas.
   - Para empezar ya: poner **cualquier pedal con buffer** (un afinador, un Boss) delante del ADC.
   - Después, un buffer de 1 MΩ con TL072 u OPA1678.
3. **Controles:** un MCP3208 (SPI) y potenciómetros de 10k. El ADC interno sirve si sus pines están accesibles [?].
4. **Muy recomendado más adelante:** el módulo SDRAM de Sipeed (~10 USD) en el conector 40P. Habilita looper, granular largo y delays de minutos **sin rediseñar nada**, porque el núcleo ya habla con una "memoria de delay" abstracta.

### 8.6 Hoja de ruta ajustada
1. Modelo de referencia en Python/C a fs = 48 828 Hz y punto fijo: Dattorro a 32 kHz, shimmer, cinta lo-fi y freeze.
2. I2S passthrough (PCM1808/PCM5102A) + escritura a WAV en la microSD para medir.
3. Núcleo FV-1 ampliado + ensamblador, validado con programas `.spn` existentes.
4. Presets: Plate, Hall, Cloud, Shimmer, Blackhole/Freeze, cinta lo-fi, reverse y micro-looper.
5. Interfaz: potenciómetros, footswitches y OLED; presets en SD.
6. Cuando haya SDRAM: looper, granular largo y delays largos.
