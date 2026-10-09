# La memoria, no el cómputo, decide SOFIFI

SOFIFI ya tiene el cómputo de un pedal ambient de referencia. Le falta memoria, interacción y apertura bien resueltas. Los pedales insignia de 2024-2026 se recuerdan por una sola idea fuerte: la reverb Cloud de Strymon, el micro-looper que siempre escucha del MOOD MkII o el Gravity inverso del Blackhole. Casi ninguna de esas ideas exige más instrucciones de las que SOFIFI tiene: 2 048 por muestra, 16 veces las 128 del Spin FV-1 [?]. La investigación académica reciente (Aalto, Polimi, DAFx 2020-2026) aporta reverbs más densas y freeze sin anillo metálico. Todo eso se ejecuta como programa y cuesta menos del 10 % del presupuesto [INF]. La frontera dura es la memoria: 43 008 palabras, unos 0,88 s, frente a 30-60 s de looper en Chroma Console y Microcosm [V]. Por eso la hoja de ruta tiene tres escalones. Primero, programas nuevos sin cambiar el hardware (fase 06). Segundo, dos extensiones pequeñas de la ISA: direccionamiento absoluto y una línea de retardo en coma flotante (fase 07). Tercero, hardware nuevo (SDRAM, coprocesador STFT, MIDI) después de la integración. Lo neuronal sirve en el PC, para ajustar coeficientes; en el pedal no compensa. La diferencia que ningún competidor ofrece es la suma de cuatro rasgos: programas abiertos, modelo bit-exact, ciclos deterministas y presets como ficheros legibles [INF].

**Numeración de fases.** Este informe usa la numeración vigente: 03 estado del arte y hoja de ruta (esta investigación), 04 núcleo RTL, 05 núcleo verificado por UART, 06 biblioteca de programas, 07 micro-looper y granular, 08 carga desde microSD, 09 controles, 10 OLED, 11 I2S y 12 integración.

**Origen.** Investigación de la Fase 03, hecha el 2026-10-07 con cinco líneas en paralelo y un redactor. Las notas en bruto no se versionan.

**Marcas de confianza.** [V] verificado en fuente primaria. [?] dudoso o de fuente secundaria. [INF] inferencia de este informe o de las notas. Las cifras de terceros son datos citados, no instrucciones.

## Seis ideas fuertes definen el pedal ambient de 2026

El mercado tiene dos niveles de precio. Las estaciones de trabajo cuestan entre 600 y 900 USD. Los pedales de autor cuestan entre 280 y 460 USD y tienen pocos presets y mucha interacción [INF]. En los dos niveles, cada pedal icónico se asocia a una idea concreta.

| Pedal | Precio | Idea icónica | Memoria o búfer | Presets | Control externo |
|---|---|---|---|---|---|
| Strymon BigSky MX (2024) | 679 USD [V] | 12 «machines», dos motores, IR de 10 s, pulsador Infinite | IR de 10 s estéreo [V] | 300 [V] | USB-C, MIDI DIN, expresión [V] |
| Strymon Cloudburst | 279 USD [?] | Algoritmo Cloud; modo Ensemble que añade una voz de cuerdas [?] | No publicada | 300 por MIDI [V] | MIDI TRS y USB-C, 5 modos del jack EXP [V] |
| Chase Bliss MOOD MkII (2023) | 399 USD [V] | Micro-looper «always-listening»; mando Clock que cambia la frecuencia de muestreo «in harmonized steps» [V] | No publicada | 2 en el pedal [V], 122 por MIDI [?] | MIDI, CV, expresión [V] |
| Hologram Microcosm | 459 USD [V] | 11 efectos granulares, phrase looper de 60 s, Hold [V] | 60 s [V] | 16 de usuario [V] | MIDI In/Out/Thru con clock [V] |
| Hologram Chroma Console | 399 USD [V] | 4 módulos reordenables, CAPTURE de 30 s, grabación de gestos [V] | 30 s [V] | 80 [V] | MIDI DIN y USB-C [V] |
| Eventide Blackhole (pedal) | 279 USD [V] | Dos freeze; Gravity pasa de reverb normal a inversa [V] | No publicada | 5, ampliables a 127 [V] | EXP configurable como MIDI [V] |
| Meris Polymoon | 299 USD [V] | Multitap supermodulado con 6 LFO [V] | 1 200 ms [V] | 5 [V] | MIDI por TRS con caja aparte [V] |
| Walrus Lüm (2025-2026) | 279,99 USD [?] | Taps granulares que leen el tanque de la reverb; crossfade entre presets [?] | No publicada | 3 [?] | E/S mono; MIDI sin especificar [?] |
| MXR Textures M310 (julio 2026) | 269,99-279 USD [?] | Granular con modos Delay, Auto Freeze y Layers [?] | No publicada | 8 de fábrica [?] | Expresión y tap externo [?] |

Fuentes: [Strymon BigSky MX](https://www.strymon.net/product/bigsky-mx/), [Strymon Cloudburst](https://www.strymon.net/product/cloudburst/), [Chase Bliss MOOD MkII](https://www.chasebliss.com/mood-mkii), [Hologram Microcosm](https://www.hologramelectronics.com/products/microcosm), [Hologram Chroma Console](https://www.hologramelectronics.com/products/chroma-console), [SOS Blackhole](https://www.soundonsound.com/reviews/eventide-blackhole-pedal), [Meris Polymoon](https://meris.us/product/polymoon/), [Synth Anatomy Lüm](https://synthanatomy.com/2026/07/walrus-audio-lum-a-limited-edition-fusion-granular-textural-reverb-pedal.html), [Guitarbomb MXR Textures](https://guitarbomb.com/blog/mxr-textures-granular-synth-engine/).

Las plataformas conocidas usan ARM (Strymon, Eventide) o DSP SHARC en coma flotante de 32 bit (Meris) ([SOS Enzo X](https://www.soundonsound.com/reviews/meris-enzo-x)). Ninguna fuente consultada cita una FPGA en un pedal ambient comercial [INF]. El BigSky MX usa un ARM tri-core a 800 MHz con conversión de 24 bit / 96 kHz [V] ([Strymon](https://www.strymon.net/product/bigsky-mx/)).

Las listas de «best ambient» repiten los mismos rasgos ([Guitar.com](https://guitar.com/guides/buyers-guide/best-ambient-pedals/)):

- **freeze** (congelar la cola y tocar encima) o sustain infinito;
- **shimmer** (reverb con desplazamiento de tono en el lazo);
- granular o micro-looper;
- **lo-fi**: reducción de muestreo, cinta o artefactos de códec;
- E/S estéreo;
- colas largas y moduladas.

El control de muestreo o «stretch» se repite en MOOD MkII [V], Slöer [?], Lüm [?] y Afterneath V3 [?]. El morphing (paso continuo entre dos estados de parámetros) aparece en el crossfade del Lüm [?] y en los gestos del Chroma Console [V].

Las críticas también se repiten. Los usuarios dicen que el granular del Microcosm «kicks in too late» [?] ([ModWiggler](https://www.modwiggler.com/forum/viewtopic.php?t=282983)). Las funciones secundarias del NightSky no están rotuladas y obligan a consultar el manual [?] ([MusicTech](https://musictech.com/reviews/studio-recording-gear/strymon-nightsky-review/)). El Habit no tiene salida estéreo y usa un MIDI no estándar [?] ([Engadget](https://www.engadget.com/chase-bliss-habit-review-guitar-effects-pedal-delay-looper-130017678-134517316.html)). La única plataforma programable del segmento, el ZOIA, tiene fama de no ser «user friendly» [?] ([TalkBass](https://www.talkbass.com/threads/lets-talk-weirdo-pedals-red-panda-chase-bliss-meris-montreal-assembly-bananana-pladask.1440821/)). Ningún fabricante publica cifras de latencia [INF].

La conclusión para SOFIFI es directa. El paquete mínimo competitivo de 2026 incluye estéreo, freeze en pulsador, shimmer, un mando de stretch, modulación de cola, presets por MIDI y expresión [INF]. SOFIFI ya tiene plate, shimmer y freeze. Le faltan el stretch, el granular, las rampas, el morphing y el MIDI [INF]. El looper de frase de 30-60 s no cabe en 0,88 s. Hay que declararlo fuera de alcance hasta tener SDRAM [INF].

## Para superar a los Eventide hay que ganar en sonido, no en número

*Añadido el 2026-10-08, tras cerrar la Fase 07 (versión 0.7).* La persona propietaria fija un objetivo: superar a los Eventide de gama alta. Esta sección compara cifras y dice qué falta.

| Pedal | Efectos o algoritmos | Presets | Precio nuevo |
|---|---|---|---|
| **SOFIFI 0.7** | 45 programas en 8 familias | 360 | unos 125 USD de BOM, sin caja (`BOM.md`) |
| Eventide H9 Gen 2 | 74 algoritmos, con las bibliotecas del H90 y del H9 Max [?] | más de 1 000 [?] | 599 USD [?] |
| Eventide H90 | 62 a 64 algoritmos [?] | 99 en el pedal y unos 500 por la app [?] | 899 USD; la edición Dark, hasta 999 [?] |
| Eventide Space | 12 algoritmos [?] | 100 [?] | 399 a 499 USD [?] |
| Eventide Blackhole | 1 algoritmo [V] | 5, ampliables a 127 por MIDI [V] | 239 a 299 USD [?] |
| Strymon BigSky MX | 12 reverbs, dos a la vez [V] | 300 [V] | 679 USD [V] |
| Boss RV-500 | 12 modos con 21 tipos de reverb [?] | 297 [?] | sin consultar |
| Hologram Microcosm | 11 efectos × 4 variaciones = 44 [V] | 16 de usuario [V] | 459 USD [V] |

En número, SOFIFI ya supera a los pedales de reverb dedicados y queda por debajo del H90 y del H9 Gen 2 [INF]. El número engaña por tres razones [INF]:

1. Los 45 programas incluyen efectos que no son ambient, como el compresor, la puerta o el autowah.
2. Los 360 presets son otras posiciones de los mandos de los mismos programas.
3. Un algoritmo de Eventide tiene años de ajuste por oído detrás; un programa `.sasm` tiene una prueba acústica y una huella.

**Qué quiere decir «superar».** Se proponen ocho criterios medibles [INF]:

| Criterio | H9 Gen 2 / H90 | SOFIFI hoy | Qué hace falta |
|---|---|---|---|
| Suena con guitarra | sí | no | códec I2S, mandos y OLED (Fases 09 a 11) |
| Algoritmos | 74 [?] | 45 | 30 programas más; caben como ficheros, sin RTL (ADR 0006) |
| Presets | más de 1 000 [?] | 360 | más presets por programa, y presets de usuario en la microSD (Fase 08) |
| Dos efectos a la vez | el H90 encadena dos algoritmos por preset [?] | uno | repartir los 2 048 ciclos entre dos programas, o un segundo núcleo |
| Memoria | segundos de retardo [?] | 0,88 s (0,67 s para loops) | SDRAM (`BOM.md`, línea 12) |
| Calidad percibida | referencia del mercado | sin medir | prueba ciega ABX contra grabaciones de referencia |
| Precio | 599 a 999 USD [?] | unos 125 USD de BOM | ya gana |
| Abierto y comprobable | no | sí, bit a bit (ADR 0003) | ya gana |

**Lo más difícil son dos efectos a la vez y la calidad** [INF]:

- El hall usa 1 585 de 2 048 ciclos y el granular, 1 896. Dos efectos así no caben en un núcleo.
- Un segundo núcleo ocuparía casi otra mitad del chip: hoy `nucleo_placa` usa 11 097 de 23 040 LUT4 (`docs/ratchets.yaml`, RAT-11). Antes hay que reducir la espera de unos 14 ciclos por instrucción (`docs/arquitectura_fpga.md`, «Próximo cambio previsto»).
  - Actualización 2026-10-08: no cabe (ADR 0013) y la persona propietaria decidió seguir sin él. El núcleo segmentado (ADR 0014) gasta 1,6 veces menos ciclos; ahora limita más la memoria.
- La calidad no se demuestra con una huella. Hace falta una prueba de escucha con personas y un criterio de aceptación escrito antes de escuchar.

**Actualización 2026-10-08: dos efectos a la vez.** Se midió el coste de más núcleos [V] (ADR 0013). Con 2 núcleos, yosys da 13 112 LUT4 antes de colocar y nextpnr no encuentra una colocación legal; con 3, 19 046 LUT4. Dos efectos a la vez se hacen con cadenas: el compositor une dos programas en uno. Hoy hay 24 cadenas en `presets/cadenas.toml`: 18 caben y 6 esperan la SDRAM, porque solo les falta memoria.

**Lo que ya gana** [INF]: el precio, que es de cinco a siete veces menor que el de un H90, y la apertura. Ningún Eventide deja leer su algoritmo ni comprobarlo bit a bit.

Fuentes de los precios y las cifras de Eventide (agregadores y tiendas, por eso van con [?]): [Equipboard H90](https://equipboard.com/items/eventide-h90-harmonizer-multi-effects-pedal), [Guitar Chalk](https://www.guitarchalk.com/best-multi-effects-pedals-under-1000/), [Equipboard H9 Gen 2](https://equipboard.com/items/eventide-h9-harmonizer-gen-2), [SOS H9 Gen 2](https://www.soundonsound.com/news/eventide-launch-h9-harmonizer-gen-2), [Thomann H90](https://thomannmusic.com/eventide_h90_harmonizer.htm), [Equipboard Space](https://equipboard.com/items/eventide-space-reverb-pedal), [Equipboard Blackhole](https://equipboard.com/items/eventide-blackhole-pedal), [SOS Space](https://www.soundonsound.com/node/4904933), [zZounds RV-500](https://www.zzounds.com/pagearea--61/item--BOSRV500), [SOS Microcosm](https://www.soundonsound.com/reviews/hologram-electronics-microcosm).

### Actualización 2026-10-08: lote ambient (51 programas)

La persona propietaria pidió más efectos ambient. Se compararon los modos de tres pedales de referencia con el catálogo. La tabla dice qué idea faltaba y qué programa la cubre ahora.

| Idea en el mercado | Dónde aparece | Programa nuevo |
|---|---|---|
| Eco de varias cabezas con difusión, entre delay y reverb | Magneto del BigSky MX: de una a seis cabezas y un mando de difusión [?] | `bruma` |
| Pad de cuerdas sobre la reverb | modo Ensemble del Cloudburst y del Cloud del BigSky MX [?] | `ensemble` |
| Drone que se sostiene solo | Tunnel del Microcosm: drones con micro-loops cíclicos [?]; hoja de ruta, punto 4 | `sostenido` |
| Reverb con trémolo o con distorsión | algoritmos de reverb con trémolo y reverb distorsionada de los multiefectos [INF] | `marea`, `shoegaze` |
| Shimmer de −12 | lista de efectos de la investigación (`INVESTIGACION.md` §4.3) | `shimmer_grave` |

Los seis caben en el núcleo sin cambiar la ISA ni el RTL: el más caro, `shoegaze`, usa 1 772 de 2 048 ciclos. Con ellos hay 51 programas y 408 presets [V] (`docs/programas.md`). Al H9 Gen 2 le quedan 23 algoritmos de ventaja [?].

Quedan fuera, porque necesitan algo que el núcleo aún no tiene [INF]:

- Polyphony y Prism Shift del H90: pitch polifónico, que pide un STFT (hoja de ruta, punto 25) [?].
- Strum, Seq y Arp del Microcosm: secuencias de notas recientes, que piden más memoria (SDRAM, punto 24) [?].
- Choir del BigSky MX: voces con tono y timbre al azar; el `chorale` es su base, pero un coro de varias voces no cabe hoy en los ciclos [INF].

Fuentes: [Strymon BigSky MX, guía rápida](https://www.strymon.net/manuals/BigSkyMX_QuickStart_RevB.pdf), [Synth Anatomy Microcosm](https://synthanatomy.com/2020/02/microcosm-new-super-creative-granular-looper-pedal-from-hologram.html), [MusicRadar H90](https://musicradar.com/news/eventide-h90-harmonizer-effects-pedal), [SOS H90](https://www.soundonsound.com/news/eventide-reveal-h90-harmonizer-pedal).

## La investigación DSP mejora la calidad sin hardware nuevo

La línea académica dominante de 2020-2026 no cambia la topología de la reverb. Optimiza la **FDN** (red de retardos con realimentación, del inglés *feedback delay network*) fuera de línea y la densifica con poco coste. Ese trabajo ocurre en el PC; el pedal solo ejecuta coeficientes [INF].

Cuatro resultados encajan en el núcleo como programas:

- **FDN incolora de 4 líneas.** Dal Santo y colaboradores optimizan una FDN de solo 4 líneas para maximizar la planitud espectral. En la prueba subjetiva, la cola pierde el timbre metálico [V] ([arXiv:2402.11216](https://www.arxiv.org/abs/2402.11216)).
- **Velvet noise.** Es ruido disperso con pulsos de ±1 y hasta un 95 % de ceros [V]. El VN-FDN supera la densidad de ecos de una FDN convencional con la mitad de líneas. Además, ahorra más del 50 % de las operaciones [V] ([DAFx-2020](https://dafx.de/paper-archive/details/5QRu1GCO7Aix-Qn4LMJdrw)).
- **Matriz de realimentación variable en el tiempo.** Modular la matriz, y no las longitudes, mejora la calidad percibida de los modos que decaen [V] ([Schlecht y Habets, JASA 2015](https://cris.fau.de/publications/212195437)). Griesinger describe el mismo principio en el Lexicon 224: elementos aleatorios que limitan los modos metálicos [V] ([Muzines](https://www.muzines.co.uk/articles/illusions-of-space/2902)).
- **Shimmer con FDN no lineal.** El artículo de DAFx-2026 estudia cinco formas de meter no linealidades en el lazo. Todas respetan la conservación de energía y la estabilidad [V] ([DAFx-26](https://dafx.de/paper-archive/details/tLDBzbMbZN8aoERSiwvSpg)). Las notas no pudieron leer las cinco técnicas [?].

El tercer punto resuelve un problema medido en el proyecto. En la fase 01, la interpolación Hermite del tanque modulado apagaba el freeze unos 0,6 dB cada 0,6 s. El proyecto lo corrigió llevando la profundidad de modulación a 0 durante el freeze (`docs/fases/estado_fases.csv`). Una rotación de Givens (giro de un par de líneas por un ángulo θ) con θ procedente de un LFO lento mantiene la matriz ortogonal. Así, el freeze modula sin perder energía [INF]. La cuantización a 18 bit puede romper esa ortogonalidad. Por eso hay que verificar la rotación en el modelo bit-exact (ADR 0003, ADR 0008) [INF].

La tabla resume el coste estimado en el núcleo. Todas las cifras son [INF] de las notas, con 1 instrucción ≈ 1 MAC o 1 acceso a la línea. `CHO` cuesta 4 ciclos según el ADR 0009.

| Técnica | Instrucciones por muestra | Palabras de memoria | FFT | Prioridad |
|---|---|---|---|---|
| FDN incolora optimizada, N = 4-8 | 40-120 | 4 000-12 000 | No | Alta |
| Difusor de velvet noise | 60-100 | ≈ 2 400 compartidas | No | Alta |
| Matriz variable (Givens + LFO) | +10-20 | ≈ 0 | No | Alta |
| Shimmer con criterio energético | 20-60 | 2 000-4 000 | No [?] | Alta |
| Freeze granular, 4-8 granos | 40-60 | 10 000-24 000 | No | Alta |
| Wow/flutter y saturación de cinta | ≈ 40 | según el retardo | No | Alta |
| Onset con swell, ducking y auto-freeze | < 50 | ≈ 0 | No | Alta |
| Ensemble de 3 voces | 25-30 | ≈ 1 500 | No | Media |
| WSOLA repartido entre muestras | 30-60 | 4 000-8 000 | No | Media |
| Banco de 24 bandas (blur, vocoder) | ≈ 220 | ≈ 0 | No | Media |
| Muelle con all-pass dispersivos | 150-300 | < 2 000 | No | Media |
| Vocoder de fase (PGHI) o freeze espectral | ≈ 400 amortizadas | ≈ 8 000 | Sí | Baja hoy |

El pitch shifter actual de dos tomas tiene una latencia media de unos 10-40 ms y produce «gorjeo» en notas sostenidas [INF]. **WSOLA** (solapamiento y suma con búsqueda de la forma de onda más parecida) reduce ese gorjeo sin FFT. Cuesta unas 30-60 instrucciones si el núcleo reparte la búsqueda de correlación entre muestras [INF]. El vocoder de fase con PGHI admite estiramientos extremos sin los artefactos típicos [V] ([arXiv:2202.07382](https://arxiv.org/pdf/2202.07382)). Pero exige FFT, direccionamiento bit-inverso y CORDIC. Eso es un cambio de ISA, no un programa [INF].

Para el lo-fi, los modelos de cinta de complejidad constante encajan bien [V] ([Zavalishin y Parker, DAFx-2018](https://www.dafx.de/paper-archive/details/HeLd0OAtZr6hPw_63LViZg)). El ADAA (antialiasing por antiderivada) necesita una división [V] ([Aalto](https://aaltodoc.aalto.fi/items/a46ae786-3014-4c49-a409-957b4c330bcd)). El núcleo no tiene división. La alternativa es una polinómica de grado bajo o una tabla de recíprocos [INF].

**La restricción que más aprieta es la memoria.** Un plate, un freeze granular y un delay de cinta con tiempos generosos no caben a la vez en 43 008 palabras [INF]. Cada bloque de BSRAM guarda 1 024 palabras, unos 21 ms a 48 828 Hz [INF].

## Lo neuronal ajusta coeficientes en el PC y no corre en el pedal

El **DDSP** (procesado de señal diferenciable) es la línea neuronal más útil para SOFIFI. Sirve fuera de línea. FLAMO ajusta por descenso de gradiente una FDN contra una respuesta al impulso objetivo [V] ([arXiv:2409.08723](https://arxiv.org/abs/2409.08723)). DiffAPF hace diferenciables los filtros todo-polo variables en el tiempo y lo demuestra con un phaser [V] ([arXiv:2404.07970](https://arxiv.org/abs/2404.07970)). DeepAFx-ST predice parámetros de efectos a partir de una grabación de referencia [V] ([arXiv:2207.08759](https://arxiv.org/abs/2207.08759)). El resultado son coeficientes clásicos. El coste en el pedal es cero [INF].

Ninguna herramienta DDSP modela la cuantización en punto fijo ni el acumulador de 48 bit [INF]. SOFIFI tiene que añadir dos piezas: cuantización simulada durante el ajuste y una verificación posterior con el modelo bit-exact [INF]. Las longitudes de retardo son enteras y no tienen gradiente. Lo práctico es fijarlas por criterio clásico y optimizar solo ganancias y filtros [INF].

En el pedal, los modelos neuronales no compensan:

| Modelo | MAC por muestra | ¿Cabe en un núcleo? |
|---|---|---|
| LSTM-8 o S4D/LRU de ≈ 800 parámetros | ≤ 750 [V] ([arXiv:2405.04124](https://arxiv.org/abs/2405.04124)) | Sí, con bucles matriz-vector y tablas de tanh/sigmoide [INF] |
| LSTM-32, el equilibrio de Juvela | ≈ 4 350 [INF] ([arXiv:2403.08559](https://arxiv.org/abs/2403.08559)) | No; necesita unos 2 núcleos o un acelerador [INF] |
| LSTM-40 de Proteus | ≈ 6 700 [INF] ([GitHub Proteus](https://github.com/GuitarML/Proteus)) | No [INF] |
| RAVE «raspberry» | 10⁸-10⁹ MAC/s [INF] ([arXiv:2111.05011](https://arxiv.org/abs/2111.05011)) | No; supera el chip completo [INF] |

Un acelerador neuronal dedicado **choca con el ADR 0006** («los efectos son programas, no módulos RTL»). Además, quita DSP y BSRAM a las líneas de retardo [INF]. Para el carácter de un drive, un modelo grey-box (EQ, waveshaper aprendido y EQ) ajustado offline cuesta decenas de MAC y se expresa como programa [INF]. Las notas no encontraron ningún paper de amplificador neuronal en FPGA [V, búsqueda sin resultado positivo].

## El sector pide capas visibles, MIDI estándar y presets abiertos

El formato dominante es un mando por parámetro y una segunda capa oculta. En el MOOD MkII, el usuario entra en esa capa manteniendo los dos pulsadores [?] ([manual MOOD MkII](https://www.chasebliss.com/s/MOOD-MKII_Manual_Pedal_Chase-Bliss.pdf)). El Cloudburst tiene seis controles directos y 300 presets por MIDI [V] ([Strymon](https://www.strymon.net/product/cloudburst/)). SOFIFI tiene 6 potenciómetros y 2 pulsadores: el mismo formato [INF]. La OLED puede mostrar la función activa de cada mando. Eso ataca la queja del NightSky sin añadir menús [INF]. La OLED también resuelve el desajuste entre preset y mando. Chase Bliss lo resuelve con faders motorizados [?] ([Effects Database](https://www.effectsdatabase.com/model/chasebliss/automatone/preamp/mk2)). SOFIFI solo necesita mostrar el valor guardado y recogerlo cuando el mando lo cruza (*pickup*) [INF].

Los pulsadores tienen un comportamiento esperado. Freeze o infinito, **trails** (la cola sigue sonando al desactivar el efecto) y tap tempo son lo normal [INF]. El Cloudburst deja usar el jack EXP como pulsador externo de Freeze o Infinite [V] ([Strymon](https://www.strymon.net/product/cloudburst/)). Las notas proponen este reparto [INF]:

| Acción | Función |
|---|---|
| Pulsador A | Bypass con trails |
| Pulsador B, pulsación corta | Freeze enclavado |
| Pulsador B, mantenido | Freeze momentáneo |
| A y B mantenidos | Segunda capa de mandos |
| Pulsación doble o MIDI | Preset siguiente o anterior |

En conectividad, la gama de 250-450 USD espera MIDI por TRS o USB-C, PC, CC y clock. También espera expresión, estéreo, **kill-dry** (salida solo húmeda para bucles en paralelo) y firmware actualizable [INF]. El caos de los cables TRS tipo A y tipo B está documentado [V] ([Morningstar](https://www.morningstar.io/post/all-you-need-to-know-about-trs-midi-connections)). SOFIFI debe usar el tipo A, que es el estándar de la MIDI Association, y rotularlo [INF]. El MIDI serie a 31 250 baudios es una UART más en la FPGA [INF]. El puente USB-UART de la placa **no** es USB-MIDI de clase. Ese modo exige un microcontrolador puente [INF].

Los presets son otro hueco. Ningún fabricante revisado publica su formato de fichero [INF]. La comunidad ZOIA comparte en patchstorage, con más de 100 páginas de listados [?] ([patchstorage](https://patchstorage.com/platform/zoia/page/18/)). Existen editores de terceros para el Microcosm, prueba de una demanda sin cubrir [?] ([Sonic Freaks](https://www.sonicfreaks.com/shop/microcosm-editor/)). SOFIFI puede guardar cada preset como texto versionado en la microSD. El preset debe guardar todo: mandos, segunda capa, rampas, asignación de expresión y programa [INF].

Dos plataformas abiertas muestran los límites del enfoque. El Hothouse exige compilar C++, gen~ o Pure Data [V] ([Synthtopia](https://www.synthtopia.com/content/2024/09/10/build-a-custom-diy-effects-pedal-with-the-daisy-seed-hothouse-case/)). Los usuarios del MOD Dwarf llaman «unacceptable» a su ruido de entrada. También describen crujidos con la CPU al 100 % [V] ([foro MOD](https://forum.mod.audio/t/my-thoughts-on-the-mod-dwarf-pros-and-cons-and-wishes/10422)). SOFIFI ejecuta un número fijo de ciclos por programa. No puede saturar la CPU en directo [INF].

La calidad de audio tiene una referencia de gama alta: 24 bit / 96 kHz y 116 dB de relación señal/ruido (Cloudburst) [V] ([Strymon](https://www.strymon.net/product/cloudburst/)). El PCM1808 ronda los 99 dB según su ficha, cifra no verificada [?]. SOFIFI debe medir y publicar su cifra real, no copiar la de la ficha (P2, P3) [INF]. Su latencia total debería quedar por debajo de 1 ms, dominada por los filtros del códec [INF]. También hay que medirla.

## La FPGA tiene cómputo de sobra y memoria escasa

SOFIFI hace unos 100 M MAC/s. Un Cortex-M7 a 480 MHz hace del orden de 0,5-1 G MAC/s, compartidos con el control [INF]. En efectos de líneas de retardo, los dos están en la misma liga [INF]. La diferencia real es la memoria. La Daisy Seed tiene 64 MB de SDRAM, «para buffers de audio de hasta 10 minutos» [V] ([ficha Daisy Seed](https://www.electrokit.com/upload/product/41020/41020659/Daisy_Seed_datasheet_v1.0.5.pdf)). Las reverbs clásicas de Lexicon usaban unos 1-2 s de memoria [?] ([freeverb3](https://freeverb3-vst.sourceforge.io/doc/Lexicon/lexicon_480l.pdf)). Por eso los 0,88 s bastan para reverb. No bastan para looper, granular largo ni delays de varios segundos [INF].

El FV-1 sigue vivo por su ecosistema. En septiembre de 2026 salió un emulador abierto para PC, bajo licencia MPL [V] ([Hackaday](https://hackaday.com/2026/09/12/spin-fv-1-emulator-simplifies-sound-pedal-development/)). Hay ensambladores en Python (`asfv1`) y un editor gráfico (SpinCAD) [V] ([PedalPCB wiki](https://wiki.pedalpcb.com/wiki/Spin_FV-1)). Las notas no encontraron ningún «FV-1 en FPGA» publicado [V, búsqueda sin resultado]. Un traductor desde SpinASM daría a SOFIFI una biblioteca desde el primer día [INF]. Según el ADR 0009, los programas sin `CHO` se ensamblan casi tal cual. Los que usan `CHO` hay que reescribirlos.

### La cadena de herramientas funciona, pero no para todas las primitivas

Una nota afirma que el README de apicula no lista el GW5A [V] ([apicula](https://github.com/YosysHQ/apicula)). La evidencia del proyecto manda sobre esa nota. El proyecto ya sintetizó, colocó, enrutó y programó el GW5A-25 con yosys, nextpnr-himbaechel y apicula. También recibió salida UART de la placa: un mensaje cada 1,0001 s, con 207 LUT4 y 366,84 MHz (medido el 2026-10-07, MED-03 a MED-05). **La cadena funciona para las primitivas usadas hasta hoy: LUT, ALU, DFF e IOB.** Aún no está verificada para los bloques DSP 27×18, la BSRAM de doble puerto ni el PLL. El núcleo RTL de la fase 04 depende de las tres. Por eso la Fase 03 incluye una prueba mínima por primitiva en la placa [INF].

### Tres saltos de hardware, ordenados por lo que habilitan

**SDRAM.** El módulo TANG_SDRAM de Sipeed tiene 2 chips de 32 MB a 16 bit y 143 MHz [V] ([Sipeed wiki](https://wiki.sipeed.com/hardware/en/tang/tang-PMOD/FPGA_PMOD)). Eso da unos 11 minutos de audio mono [INF]. Admite unos 200-350 accesos aleatorios por muestra y chip [INF]. Basta para looper, granular de 16-32 granos y delays multitap. No basta para mover una reverb densa. Las reverbs deben seguir en BSRAM [INF]. El controlador cuesta unas 1 000-2 000 LUT [INF]. La ISA necesita lecturas anticipadas con resultado en la muestra siguiente [INF]. El módulo usa un conector de 40 pines; hay que revisar si convive con la microSD y el códec [INF]. La memoria del proyecto dice que la placa disponible no tiene SDRAM.

**Coprocesador STFT.** Una FFT radix-2 de 1 024 puntos en modo ráfaga necesita unas 40 mariposas por muestra, con FFT e IFFT [INF]. Estimación: 4-6 DSP, 6-10 BSRAM y 1 500-3 000 LUT [INF]. Habilita shimmer limpio por vocoder de fase, freeze espectral y blur espectral [INF]. Su coste real es BSRAM: 8 bloques son unos 0,17 s de retardo [INF]. Las notas citan 0,12 s para 8 bloques; con 1 024 palabras por bloque, la cifra correcta es 0,17 s [INF].

**Línea de retardo en coma flotante de 12 bit.** Sigue el escalado de ganancia del Lexicon 224 [?] ([vintagedigital](https://www.vintagedigital.com.au/?p=143805)). Multiplica la memoria por 1,5, de 0,88 s a unos 1,32 s [INF]. Cuesta unas 100-300 LUT por codificador o decodificador y no usa DSP [INF]. Mantiene el acceso aleatorio y la interpolación Hermite [INF]. El μ-law de 8 bit da ×2,25 con ruido audible en colas largas. El ADPCM de 4 bit es incompatible con lecturas moduladas [INF].

Un segundo núcleo aporta poco cómputo, porque ya sobra. Su valor es otro: dos programas en paralelo y transición sin cortes entre presets [INF]. Cuesta las LUT del núcleo y 6 BSRAM de microcódigo, unos 0,13 s de retardo [INF]. Un VLIW de 2-3 rutas (MAC, acceso a memoria y LFO en paralelo) daría más trabajo por ciclo sin duplicar el microcódigo [INF].

### Recomendaciones que chocan con un ADR

| Recomendación | ADR afectado | Naturaleza del conflicto |
|---|---|---|
| Acelerador neuronal (LSTM-32 o más) | ADR 0006 | Es un módulo RTL de efecto. Se desaconseja. |
| Coprocesador STFT | ADR 0006 (parcial) | Es RTL nuevo, pero genérico. Los programas lo invocan. Exige una actualización del ADR 0006 y del ADR 0009. |
| Línea en coma flotante o μ-law | ADR 0008 | Cambia la aritmética del contrato. El modelo bit-exact la implementa primero (ADR 0003). |
| SDRAM como línea de retardo | ADR 0004 | El ADR prevé su revisión al instalar el módulo. La microSD sigue sin retardar. |
| Looper en streaming a microSD | ADR 0004 | Choca de frente. Se descarta. |
| `RDAA` / `WRAA` (direccionamiento absoluto) | ADR 0009 | Ya planificado en la fase 07, con actualización del ADR. |

## Lo que haría a SOFIFI única

| Diferenciador | Evidencia | Marca |
|---|---|---|
| Único pedal ambient en FPGA | Ninguna fuente cita una FPGA en un pedal ambient comercial | [INF] |
| Programas abiertos con modelo bit-exact en Python | Hothouse exige compilar [V]; ZOIA tiene fama de difícil [?] | [INF] |
| Cero crujidos por CPU: ciclos fijos por programa | Queja documentada del MOD Dwarf [V] | [INF] |
| Presets como ficheros de texto con todo el estado | Ningún fabricante publica su formato | [INF] |
| Latencia de una muestra en la ruta húmeda y < 1 ms total | Queja de latencia del Microcosm [?]; falta medirla | [INF] |
| Freeze que modula sin perder energía (matriz Givens) | Matrices variables mejoran los modos [V]; fallo medido en la fase 01 | [INF] |
| Segunda capa visible en una OLED trilingüe (es · en · zh-CN) | Queja de funciones sin rotular [?]; ningún pedal tiene UI localizada | [INF] |
| Compatibilidad con el ecosistema FV-1 | Emulador abierto de 2026 [V]; no hay sucesor del FV-1 | [INF] |

## Hoja de ruta priorizada

El orden sigue impacto entre coste. Las cifras de coste son [INF] salvo indicación.

| # | Función o cambio | Qué aporta | Coste estimado | Cambio en la ISA o el hardware | Hardware que exige | Fase |
|---|---|---|---|---|---|---|
| 1 | Prueba mínima por primitiva: DSP 27×18, BSRAM de doble puerto, PLL | Quita el riesgo de la cadena antes del núcleo | Pocas LUT; 1 DSP, 1 BSRAM, 1 PLL por prueba | Ninguno; prueba en la placa | Ninguno | 03 |
| 2 | Modulación aleatoria filtrada (LFSR) en el plate, al estilo Spin/Wander | Mayor impacto audible por coste; rompe modos metálicos | 3-4 instr. por línea modulada; 0 memoria | Ninguno | Ninguno | 06 |
| 3 | Matriz Givens con LFO en el freeze | Freeze modulado sin pérdida de energía | +10-20 instr.; 0 memoria | Ninguno si el LFO da seno y coseno; si no, dos LFO en cuadratura | Ninguno | 06 |
| 4 | Onset con swell, ducking y auto-freeze | Interacción «que escucha», como el MOOD | < 50 instr.; ≈ 0 memoria | Ninguno | Ninguno | 06 |
| 5 | FDN incolora de 4-8 líneas y difusor de velvet noise | Cola más densa y menos coloreada | 100-220 instr.; 6 400-14 400 palabras | Ninguno; cada pulso es una `RDA` con coeficiente ±1 | Ninguno | 06 |
| 6 | Ajuste DDSP offline con cuantización simulada | Coeficientes óptimos y estables a 18 bit | 0 en el pedal; herramienta en el PC | Ninguno | Ninguno | 06 |
| 7 | Shimmer con criterio energético | +12 st que no diverge ni se apaga | 20-60 instr.; 2 000-4 000 palabras | Ninguno [?] | Ninguno | 06 |
| 8 | Cinta: wow/flutter, saturación y stretch con pasos armónicos | Lo-fi y «Clock» tipo MOOD | ≈ 40-70 instr.; según el retardo | Ninguno; `CHO` con rampa | Ninguno | 06 |
| 9 | Ensemble de 3 voces | Coro denso tipo Cloudburst | 25-30 instr.; ≈ 1 500 palabras | Ninguno | Ninguno | 06 |
| 10 | Traductor SpinASM → SOFIFI | Biblioteca FV-1 desde el primer día | 0 en el pedal; herramienta en el PC | Ninguno; reescribe `CHO` | Ninguno | 06 |
| 11 | `RDAA` / `WRAA` y escritura congelada | Base del looper, granular y reverse | Pocas LUT; 1 ciclo por acceso | Sí: actualización del ADR 0009 | Ninguno | 07 |
| 12 | Freeze granular de 4-8 granos y granular sobre el tanque | Granular tipo Microcosm y Lüm | 40-60 instr.; 10 000-24 000 palabras | Usa el n.º 11 | Ninguno | 07 |
| 13 | Gravity: reverb inversa | Rasgo icónico del Blackhole | 30-60 instr.; 10 000-20 000 palabras | Usa el n.º 11 | Ninguno | 07 |
| 14 | Línea de retardo en coma flotante de 12 bit | ×1,5 de memoria (≈ 1,32 s) | 200-500 LUT; 0 DSP | Sí: flag de acceso; actualización del ADR 0008 | Ninguno | 07 |
| 15 | WSOLA repartido entre muestras | Pitch con menos gorjeo | 30-60 instr.; 4 000-8 000 palabras | Ninguno o un registro índice | Ninguno | 07 |
| 16 | Presets de texto versionados con todo el estado | Compartir presets sin editor propietario | 0 en el núcleo; espacio en la microSD | Ninguno | Ninguno | 08 |
| 17 | Segunda capa por A+B, rampas, morphing por expresión, pickup | Profundidad sin menús | ≈ 30 instr. de suavizado; lógica de control | Ninguno; parámetros por registro y `MULX` | Jack de expresión (otro) | 09 |
| 18 | Trails al bypass y kill-dry global | Lo esperado en la gama | ≈ 0 instr. | Ninguno | Ninguno | 09 |
| 19 | MIDI TRS tipo A: PC, CC y clock; tap tempo | Control y sincronía estándar | 100-300 LUT (UART de 31 250 baudios) | Hardware: entrada MIDI | Otro: optoacoplador y jack TRS | 09 |
| 20 | OLED que muestra la función activa y el valor guardado | Resuelve la queja de funciones ocultas | Lógica de UI | Ninguno | Ninguno | 10 |
| 21 | Medir y publicar latencia y relación señal/ruido | Argumento de venta verificable (P2, P3) | 0 | Ninguno | Códec | 11 |
| 22 | Banco de 24 bandas y muelle dispersivo | Blur, vocoder, muelle | 150-300 instr. cada uno; < 2 000 palabras | Ninguno | Ninguno | 12 o posterior |
| 23 | Segundo núcleo o VLIW de 2-3 rutas | Dos programas en paralelo; cambio de preset sin cortes | LUT del núcleo; 6 BSRAM de microcódigo (≈ 0,13 s) | Sí: arbitraje de memoria | Ninguno | Posterior a 12 |
| 24 | SDRAM con lecturas anticipadas | Looper largo, granular de 5-30 s, delays de varios segundos | 1 000-2 000 LUT; 0 DSP | Sí: prefetch; actualización del ADR 0004 | SDRAM (TANG_SDRAM) | Posterior a 12 |
| 25 | Coprocesador STFT de 1 024 puntos | Shimmer por vocoder de fase, freeze espectral | 4-6 DSP; 6-10 BSRAM; 1 500-3 000 LUT | Sí: nuevas instrucciones; conflicto parcial con el ADR 0006 | Ninguno; depende del n.º 1 | Posterior a 12 |
| 26 | USB-MIDI de clase | Expectativa de 2024-2026 | Firmware del puente | Hardware: puente USB | Otro: microcontrolador | Posterior a 12 |
| 27 | Drive neuronal pequeño (S4D o LSTM-8) | Carácter de amplificador | ≤ 750 instr.; < 20 Kbit de pesos | Sí: bucles matriz-vector, tablas tanh/sigmoide | Ninguno | Baja prioridad |

## Ideas de la comunidad DIY y de parches (2026-10-09)

A petición de la persona propietaria, tres investigaciones buscaron ideas de efectos ambient en los foros DIY analógicos (FreeStompboxes, DIYStompboxes, Madbean, PedalPCB, AION FX), en los repositorios de parches (Patchstorage: ZOIA, MOD, Daisy; programas del Spin FV-1) y en los foros en español (Guitarristas.info, Musiquiatra, guitarrista.org). Se usa solo el principio de cada efecto, descrito con palabras propias (ADR 0002). Lo que se lee en un foro es dato citado (P10).

- **Acceso:** FreeStompboxes, DIYStompboxes y el foro de PedalPCB devuelven 403; se citan sus fragmentos del buscador [?]. El Cuartito Diyer da 403 y ChileMusicos no responde. No se encontraron hilos en español sobre FV-1, Daisy ni MOD.
- **Licencias:** los parches de Patchstorage tienen licencias variadas (WTFPL, CC BY-SA 4.0 o ninguna). Casi todos los programas FV-1 publicados no tienen licencia. CloudSeed es MIT y se podría portar con una entrada en `docs/terceros.yaml` [V].
- **NAM y TONE3000** son capturas de amplificador: no dan ideas ambient para este núcleo.

| Programa | Qué se oye | Principio de | Lote |
|---|---|---|---|
| `erosion` | un bucle que se desintegra en cada vuelta | ZOIA TapeRewinder; Blooper y Mood | 9 |
| `mosaico` | un bucle leído a ½×, 1× y 2×: pad en tres octavas | ZOIA Astral Temple (WTFPL) | 9 |
| `arcoiris` | dos voces transpuestas con regeneración caótica | PedalPCB Leprechaun, Madbean Rainbow Puker | 9 |
| `desplazador` | eco con desplazamiento de frecuencia: espiral sin fin | FV-1 del Buchla 285 (modularsynthesis.com) | 9 |
| `tambor` | eco de tambor de 4 cabezas con combinaciones | PedalPCB Hydra | 9 |
| `armonico` | trémolo armónico: graves y agudos en contrafase | PedalPCB Pendulum; FV-1 Starfield+ | 9 |
| `violin` | ataque lento y un vibrato que entra tarde | Guitarristas.info (hilos «violín» y «slow attack») | 10 |
| `acople` | la nota sostenida se vuelve un acople armónico | Guitarristas.info (pedales atmosféricos) | 10 |
| `arco` | sustain tipo eBow, con control automático de ganancia | Guitarristas.info (sustain infinito) | 10 |
| `oscilador` | delay que autooscila con el nivel limitado | Guitarristas.info (compresor al final) | 10 |
| `shimmer_escondido` | shimmer que solo entra en la cola | Guitarristas.info y Musiquiatra (shimmer) | 10 |
| `dinamica` | el decay y el brillo siguen la fuerza al tocar | MOD Dyna Shimmer; ZOIA DirtyVerb | 10 |
| `enjambre` | nube de ecos cortos que se junta o se dispersa | PedalPCB Deflector | 11 |
| `probabilidad` | 8 ecos que suenan o no según una probabilidad | ZOIA Echolalia (WTFPL) | 11 |
| `dados` | 4 ecos con tiempos y octavas al azar | ZOIA Rain Delay (WTFPL) | 11 |
| `aureo` | tomas de eco en serie de Fibonacci | ZOIA Golden | 11 |
| `estelar` | eco con un phaser en la realimentación | FV-1 Starfield (Madbean) | 11 |
| `lata` | eco de lata de aceite: vibrato atado al tiempo | FV-1 Oil can delay | 11 |
| `deriva` | el tiempo de eco salta a destinos al azar con glide | FV-1 Pitch Step Glider | 12 |
| `dimension` | chorus espacial sin vibrato audible | AION Blueshift | 12 |
| `vibe` | vibe de lámpara con fases escalonadas | AION Straylight; PedalPCB ElectroVibe | 12 |
| `orilla` | chorus aleatorio con puerta de paso bajo | PedalPCB Low Tide | 12 |
| `baldosa` | reverb sucia de eco cruzado, estilo PT2399 | FreeStompboxes (Wishing Well, Spare Room, TBR) | 12 |
| `eco_casero` | eco que se ensucia cuanto más largo es | guitarrista.org y Guitarristas.info (PT2399) | 12 |
| `relevo` | freeze que pasa de un acorde al siguiente con fundido | Guitarristas.info (sustain infinito) | 13 |
| `frenada` | con el pulsador, la cinta se para y el tono cae | ZOIA Tape Pad V2 (WTFPL) | 13 |
| `resbalon` | cabeza de velocidad libre sobre el pasado inmediato | Mood (modo Slip) | 13 |
| `tartamudeo` | cada ataque fuerte repite un trozo | Mood (modo Envelope) | 13 |
| `dos_ecos` | dos ecos a negra y negra con puntillo | Guitarristas.info y guitarrista.org (post-rock) | 13 |
| `viento` | ráfagas de ruido filtrado que soplan al tocar | Guitarristas.info (simular instrumentos) | 13 |
| `espiral` | reverb con pitch en la regeneración, L y R distintos | ZOIA Downward spiral, Abyss | 14 |
| `arpegio` | ecos que tocan un arpegio y caen en una reverb | ZOIA Arpverb; FV-1 Arpeggio | 14 |
| `semilla` | nube con multitap que sale de una semilla | CloudSeed (MIT) | 14 |
| `swell_ritmico` | swell al ritmo del tap tempo | ZOIA Swell verb (CC BY-SA 4.0) | 14 |
| `compas` | eco con tap tempo y subdivisiones | BYOC Echo Royal | 14 |

Ya existen y no se repiten: Space Echo (cadena `cinta` → `spring`), shimmer de coro (`chorale`), freeze momentáneo (`freeze`), reverse reverb, reverb antes de saturación (`shoegaze`). Se descartan por FFT: Venus y Saturn. La receta «sinte» de Guitarristas.info (puerta, phaser, delay y reverb) es una cadena candidata.

## Conclusión

El hallazgo central invierte la intuición. SOFIFI no necesita más potencia para competir con Strymon o Chase Bliss; ya tiene 16 veces el cómputo del FV-1 [?]. Necesita gastar ese cómputo en calidad que antes era cara. Las matrices variables, el velvet noise y los coeficientes ajustados por DDSP cuestan menos de 250 instrucciones juntas. Las tres atacan el defecto clásico de las reverbs digitales baratas: el anillo metálico [INF]. La fase 06 puede entregar casi toda esa calidad sin tocar la ISA.

La segunda conclusión es estratégica. El hueco del mercado no es sonoro, sino de confianza y apertura [INF]. Ningún pedal ambient combina programas abiertos, presets legibles, ciclos deterministas y una latencia publicada [INF]. Esos cuatro rasgos nacen de decisiones que el proyecto ya tomó (ADR 0003, 0005, 0006). El riesgo inmediato no está en el diseño, sino en la cadena de herramientas. Las primitivas DSP, BSRAM de doble puerto y PLL siguen sin verificar, y la fase 04 depende de ellas. La Fase 03 las prueba antes.
