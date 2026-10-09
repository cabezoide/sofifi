<!-- GENERADO por `sofifi catalogo` desde programas/*.sasm. No se edita a mano:
     model/tests/catalogo_test.py lo compara con su generador. -->

# Programas del núcleo

86 programas y 688 presets. Cada programa es un fichero de texto en `programas/`; los presets están en `presets/banco.toml`.
Los ciclos son la cota del RTL, de 2 048 por muestra (`model/sofifi/domain/coste.py`). La memoria es de 43 008 palabras.

## Reverb

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `baldosa` | Reverb sucia de dos ecos cruzados, oscura y granulada, como un baño de azulejos. | 0: tiempo<br>1: decay<br>2: mezcla<br>3: modulación<br>4: tono<br>5: muestreo | 8 | 152 | 1 145 | 8 258 |
| `blackhole` | Sala gigante con un decay de decenas de segundos. | 0: decay<br>1: damping<br>2: mezcla | 8 | 140 | 883 | 40 882 |
| `bloom` | La reverb crece despacio después de cada nota, como una flor que se abre. | 0: decay<br>1: damping<br>2: mezcla<br>3: apertura | 8 | 84 | 637 | 23 520 |
| `chorale` | La cola del plate canta una vocal, de «a» a «i». | 0: decay<br>1: damping<br>2: mezcla<br>3: vocal | 8 | 160 | 1 192 | 37 439 |
| `cloud` | Difusores largos con modulación aleatoria: el ataque se disuelve. | 0: decay<br>1: damping<br>2: mezcla<br>3: modulación | 8 | 96 | 907 | 42 814 |
| `dinamica` | Plate cuya cola cambia con la fuerza con que se toca. | 0: decay<br>1: damping<br>2: mezcla<br>3: profundidad<br>4: umbral<br>5: velocidad | 8 | 141 | 1 188 | 37 439 |
| `ensemble` | Un coro de tres voces antes del plate: la cola suena como una sección de cuerdas. | 0: decay<br>1: damping<br>2: mezcla<br>3: ensemble | 8 | 99 | 953 | 38 540 |
| `freeze` | Plate que congela la cola con el pulsador. | 0: decay<br>1: damping<br>2: mezcla | 8 | 103 | 940 | 37 439 |
| `freeze_givens` | Freeze que se mueve sin perder energía: la cola congelada gira entre las ramas. | 0: decay<br>1: damping<br>2: mezcla<br>3: giro | 8 | 136 | 1 138 | 37 439 |
| `gated` | Reverb que se corta de golpe tras cada ataque, como en los años 80. | 0: decay<br>1: damping<br>2: mezcla<br>3: duración | 8 | 133 | 1 098 | 37 439 |
| `hall` | Red de 8 retardos con matriz de Householder: sala grande. | 0: decay<br>1: damping<br>2: mezcla | 8 | 137 | 863 | 34 522 |
| `infinite` | Plate que no decae: cada nota se suma a una capa que no se apaga. | 0: vaciado<br>1: damping<br>2: mezcla | 8 | 95 | 872 | 37 439 |
| `marea` | La cola del plate sube y baja en olas, de un lado a otro; la señal seca no cambia. | 0: decay<br>1: damping<br>2: mezcla<br>3: velocidad | 8 | 137 | 1 126 | 37 439 |
| `plate` | Plate de Dattorro con el tanque modulado. | 0: decay<br>1: damping<br>2: mezcla | 8 | 86 | 790 | 37 439 |
| `plate_vivo` | Plate cuya modulación deriva al azar: la cola nunca se repite igual. | 0: decay<br>1: damping<br>2: mezcla<br>3: vida | 8 | 127 | 1 054 | 37 439 |
| `resonador` | Cuatro cuerdas afinadas en mi mayor que vibran por simpatía con lo que se toca. | 0: sustain<br>1: excitación<br>2: mezcla<br>3: afinación | 8 | 89 | 525 | 1 |
| `reverb_inversa` | Reverb al revés: tras cada ataque, la cola crece y se corta de golpe. | 0: decay<br>1: damping<br>2: mezcla<br>3: duración | 8 | 133 | 1 098 | 37 439 |
| `semilla` | Reverb nube con primeras reflexiones que salen de una semilla: cada semilla da otra sala. | 0: decay<br>1: damping<br>2: mezcla<br>3: semilla<br>4: densidad<br>5: modulación | 8 | 196 | 1 513 | 42 934 |
| `shimmer` | Plate con un +12 en la realimentación: cada vuelta sube una octava. | 0: decay<br>1: damping<br>2: mezcla<br>3: cantidad de shimmer | 8 | 108 | 1 037 | 41 539 |
| `shimmer_energia` | Shimmer que se regula solo: cuanta más octava acumula, menos añade. | 0: decay<br>1: damping<br>2: mezcla<br>3: cantidad de shimmer | 8 | 117 | 1 095 | 41 539 |
| `shimmer_escondido` | Shimmer escondido: la octava se calla mientras tocas y aparece en la cola. | 0: decay<br>1: damping<br>2: mezcla<br>3: cantidad de shimmer<br>4: ducking<br>5: tono | 8 | 139 | 1 239 | 41 539 |
| `shimmer_grave` | Shimmer hacia abajo: cada vuelta baja una octava y la cola se vuelve un órgano grave. | 0: decay<br>1: damping<br>2: mezcla<br>3: cantidad de shimmer | 8 | 108 | 1 037 | 41 539 |
| `shimmer_quinta` | Shimmer de quinta: cada vuelta sube 7 semitonos, como un acorde que se abre. | 0: decay<br>1: damping<br>2: mezcla<br>3: cantidad de shimmer | 8 | 108 | 1 037 | 41 539 |
| `shoegaze` | Plate que se satura después de la cola: un muro de ruido cálido detrás de la guitarra. | 0: decay<br>1: damping<br>2: mezcla<br>3: saturación | 8 | 142 | 1 106 | 37 439 |
| `sostenido` | Freeze automático: cada acorde nuevo se captura y queda sonando como un pad. | 0: capas<br>1: damping<br>2: mezcla<br>3: captura | 8 | 141 | 1 190 | 37 439 |
| `spring` | Reverb de muelle: el sonido gotea, con los agudos antes que los graves. | 0: decay<br>1: damping<br>2: mezcla | 8 | 95 | 832 | 1 850 |

## Delay

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `aureo` | Catorce ecos en la serie de Fibonacci, alternados entre izquierda y derecha, que se espesan en una reverb chasqueante. | 0: inclinación<br>1: realimentación<br>2: mezcla<br>3: tono<br>4: ancho<br>5: difusión | 8 | 141 | 1 096 | 42 259 |
| `bbd` | Eco analógico oscuro: cada repetición pierde agudos y se satura. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: modulación | 8 | 44 | 408 | 14 674 |
| `bruma` | Eco de cuatro cabezas que se difumina en cada vuelta hasta volverse reverb. | 0: difusión<br>1: realimentación<br>2: mezcla<br>3: cabezas | 8 | 53 | 536 | 41 553 |
| `cinta` | Eco de cinta de 0,18 a 0,85 s con wow, flutter y saturación. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: wow y flutter | 8 | 50 | 484 | 41 600 |
| `compas` | Eco con tap tempo y cinco figuras: negra, corchea con puntillo, corchea, tresillo y semicorchea. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: subdivisión<br>4: segunda toma<br>5: tono | 8 | 135 | 885 | 32 769 |
| `dados` | Cuatro ecos con tiempos y octavas al azar; sw tira los dados otra vez. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: probabilidad<br>4: tono<br>5: ancho | 8 | 239 | 1 620 | 38 260 |
| `delay` | Eco digital limpio de 20 a 690 ms, con tono en la realimentación. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: tono | 8 | 38 | 309 | 33 749 |
| `deriva` | Eco que pierde el rumbo: el tiempo salta al azar y llega con glide. | 0: tiempo<br>1: profundidad<br>2: mezcla<br>3: velocidad<br>4: glide<br>5: realimentación | 8 | 128 | 969 | 33 796 |
| `dos_ecos` | Dos ecos a ritmo, uno limpio y otro de cinta, que se cruzan y acaban en una nube difusa. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: proporción<br>4: equilibrio<br>5: difusión | 8 | 142 | 1 131 | 41 258 |
| `ducking` | Eco que se aparta mientras se toca y aparece en los silencios. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: ducking | 8 | 51 | 394 | 33 749 |
| `eco_casero` | Eco de chip casero: limpio con tiempos cortos; oscuro, granuloso y con bombeo al alargarlo. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: suciedad<br>4: modulación<br>5: tono | 8 | 124 | 1 002 | 41 492 |
| `enjambre` | Un enjambre de ocho ecos cortos: se junta en reverb o se abre en ecos sueltos. | 0: dispersión<br>1: realimentación<br>2: mezcla<br>3: difusión<br>4: tono<br>5: deriva | 8 | 199 | 1 377 | 42 820 |
| `estelar` | Eco con un phaser dentro del lazo: cada repetición barre más y la cola gira. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: profundidad<br>4: velocidad<br>5: resonancia | 8 | 123 | 830 | 33 749 |
| `frenada` | Eco de cinta con freno: al pisar, la cinta se para y el eco cae hasta el silencio. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: frenada<br>4: arranque<br>5: wow y flutter | 8 | 156 | 1 199 | 32 876 |
| `lata` | Eco de lata de aceite: corto, turbio y líquido, con un vibrato atado al tiempo. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: profundidad<br>4: tono<br>5: aceite | 8 | 90 | 768 | 18 931 |
| `lluvia` | Seis ecos irregulares que se deshacen en allpass: una lluvia de notas. | 0: difusión<br>1: realimentación<br>2: mezcla | 8 | 46 | 364 | 35 385 |
| `oscilador` | Eco que oscila solo con un techo de nivel; el tiempo afina el tono. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: suavizado<br>4: tono<br>5: nivel | 8 | 86 | 614 | 24 678 |
| `pingpong` | Eco estéreo que salta de un lado a otro. | 0: tiempo<br>1: realimentación<br>2: mezcla | 8 | 38 | 353 | 40 874 |
| `probabilidad` | Ocho ecos que suenan o callan por sorteo: reverb cambiante o patrón que no se repite. | 0: tiempo<br>1: probabilidad<br>2: mezcla<br>3: realimentación<br>4: tono<br>5: suavizado | 8 | 220 | 1 450 | 34 456 |
| `reverse` | Eco invertido en granos de 0,17 s. | 0: tono<br>1: realimentación<br>2: mezcla | 8 | 34 | 301 | 16 388 |
| `tambor` | Eco de tambor magnético de cuatro cabezas: un ritmo que sale de las cabezas encendidas. | 0: velocidad<br>1: realimentación<br>2: mezcla<br>3: cabezas<br>4: edad<br>5: tono | 8 | 173 | 1 328 | 37 656 |

## Modulación

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `armonico` | Los graves y los agudos laten en contrafase; con pot2, un eco detrás. | 0: velocidad<br>1: profundidad<br>2: eco<br>3: frecuencia<br>4: forma<br>5: ancho | 8 | 125 | 847 | 17 101 |
| `chorus` | Tres voces con retardos que se mueven. | 0: velocidad<br>1: profundidad<br>2: mezcla | 8 | 42 | 416 | 1 101 |
| `desplazador` | Eco que desplaza su frecuencia en cada vuelta: la cola sube o baja en espiral. | 0: desplazamiento<br>1: tiempo<br>2: mezcla<br>3: realimentación<br>4: tono<br>5: ancho | 8 | 110 | 864 | 33 767 |
| `dimension` | Un chorus que abre el estéreo y da cuerpo sin que el tono ondule. | 0: modo<br>1: velocidad<br>2: mezcla<br>3: profundidad<br>4: cruce<br>5: tono | 8 | 94 | 795 | 505 |
| `flanger` | Retardo muy corto y móvil con realimentación: peines que barren. | 0: velocidad<br>1: profundidad<br>2: mezcla<br>3: realimentación | 8 | 31 | 266 | 247 |
| `orilla` | Chorus aleatorio y lento con una puerta de paso bajo que se cierra con cada nota. | 0: velocidad<br>1: profundidad<br>2: mezcla<br>3: suavizado<br>4: puerta<br>5: sensibilidad | 8 | 147 | 1 078 | 736 |
| `phaser` | Cuatro allpass con coeficiente móvil: muescas que barren. | 0: velocidad<br>1: profundidad<br>2: mezcla<br>3: realimentación | 8 | 80 | 521 | 1 |
| `slicer` | Corta el sonido en pulsos rítmicos, como una puerta que abre y cierra. | 0: velocidad<br>1: profundidad<br>2: ciclo<br>3: suavizado | 8 | 37 | 262 | 1 |
| `tremolo` | El volumen sube y baja; con pot2, de un lado a otro. | 0: velocidad<br>1: profundidad<br>2: panorama | 8 | 43 | 325 | 1 |
| `vibe` | Vibe de lámpara: cuatro fases desiguales con un barrido que sube rápido y baja lento. | 0: velocidad<br>1: profundidad<br>2: mezcla<br>3: realimentación<br>4: forma<br>5: tono | 8 | 125 | 830 | 1 |
| `vibrato` | El tono sube y baja. | 0: velocidad<br>1: profundidad<br>2: mezcla | 8 | 27 | 240 | 125 |

## Pitch

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `acople` | Una nota sostenida hace crecer encima un armónico saturado, como un acople. | 0: tiempo<br>1: intervalo<br>2: mezcla<br>3: subida<br>4: tono<br>5: nivel | 8 | 138 | 1 038 | 3 550 |
| `arcoiris` | Dos voces transpuestas en un bucle que regenera y llega a autooscilar. | 0: intervalo<br>1: segunda voz<br>2: mezcla<br>3: tiempo<br>4: realimentación<br>5: tono | 8 | 76 | 693 | 12 345 |
| `armonizador` | Una voz a −12, −7, −5, +5, +7 o +12 semitonos, con realimentación. | 0: intervalo<br>1: realimentación<br>2: mezcla | 8 | 55 | 450 | 4 100 |
| `arpegio` | Cada nota se abre en un arpegio transpuesto (1-3-5-8) que cae en una reverb. | 0: velocidad<br>1: notas<br>2: mezcla<br>3: modo<br>4: eco<br>5: decay | 8 | 163 | 1 259 | 42 851 |
| `doblador` | Dos voces desafinadas unos cents, una a cada lado: ensancha el sonido. | 0: desafinación<br>2: mezcla | 8 | 32 | 346 | 1 028 |
| `escalera` | Eco en el que cada repetición sube o baja un intervalo: una escalera. | 0: intervalo<br>1: realimentación<br>2: mezcla<br>3: tiempo | 8 | 67 | 582 | 39 313 |
| `espiral` | Reverb cuya cola sube o baja de tono en espiral, con un intervalo a cada lado. | 0: intervalo<br>1: segunda voz<br>2: mezcla<br>3: tiempo<br>4: realimentación<br>5: decay | 8 | 171 | 1 455 | 42 878 |
| `octava` | Octavador: una octava abajo y una arriba, cada una con su nivel. | 0: octava baja<br>1: octava alta<br>2: seco | 8 | 25 | 296 | 4 100 |

## Dinámica

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `arco` | Sustain de arco: la nota entra suave, se queda a nivel fijo y puede pasar a su octava. | 0: sustain<br>1: subida<br>2: mezcla<br>3: octava alta<br>4: tono<br>5: umbral | 8 | 122 | 897 | 2 052 |
| `compresor` | Compresor: baja lo fuerte y deja lo suave; sostiene las notas. | 0: umbral<br>1: compresión<br>2: mezcla<br>3: ganancia | 8 | 57 | 394 | 1 |
| `puerta` | Puerta de ruido: calla el zumbido entre notas y deja pasar lo que se toca. | 0: umbral<br>1: cierre | 8 | 29 | 222 | 1 |
| `swell` | Cada nota empieza en silencio y sube, antes de un plate. | 0: decay<br>1: damping<br>2: mezcla<br>3: subida | 8 | 116 | 983 | 37 439 |
| `swell_ritmico` | Cada nota sube con la curva y el tiempo que eliges, también al pulso del pie, en un plate que ondula. | 0: subida<br>1: forma<br>2: mezcla<br>3: decay<br>4: deriva<br>5: sensibilidad | 8 | 216 | 1 611 | 37 439 |
| `violin` | Cada nota entra sin púa, como con un arco, y el vibrato llega después. | 0: subida<br>1: tiempo<br>2: mezcla<br>3: profundidad<br>4: velocidad<br>5: tono | 8 | 118 | 845 | 85 |

## Textura

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `granular` | Nube granular de 4 voces con ventana Hann, pitch en octavas y freeze. | 0: duración<br>1: difusión<br>2: intervalo<br>3: mezcla | 8 | 188 | 1 209 | 32 769 |
| `lofi` | Menos muestras por segundo y menos bits, con aliasing. | 0: muestreo<br>1: bits<br>2: mezcla<br>3: tono | 8 | 81 | 577 | 1 |
| `ringmod` | Modulador en anillo: multiplica la guitarra por un seno; suena metálico. | 0: frecuencia<br>2: mezcla | 8 | 33 | 236 | 1 |
| `saturacion` | Saturación tipo overdrive: de un brillo cálido a una distorsión espesa. | 0: ganancia<br>1: tono<br>2: mezcla<br>3: nivel | 8 | 42 | 277 | 1 |
| `viento` | Ráfagas de ruido filtrado que silban al azar y soplan más fuerte cuando se toca. | 0: velocidad<br>1: resonancia<br>2: mezcla<br>3: sensibilidad<br>4: frecuencia<br>5: nivel | 8 | 140 | 913 | 3 728 |

## Filtro

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `ancho` | Ensancha el estéreo de una guitarra mono y ajusta el tono graves-agudos. | 0: ancho<br>1: tilt | 8 | 26 | 185 | 636 |
| `autowah` | Wah automático: cuanto más fuerte se toca, más sube el filtro. | 0: sensibilidad<br>1: resonancia<br>2: mezcla | 8 | 43 | 295 | 1 |
| `filtro` | Filtro paso bajo resonante que sube y baja solo, con un LFO. | 0: velocidad<br>1: resonancia<br>2: mezcla<br>3: profundidad | 8 | 61 | 402 | 1 |

## Looper

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `erosion` | Bucle de cinta que se desgasta en cada vuelta: pierde agudos y nivel y gana wow, grano y saturación. | 0: erosión<br>1: damping<br>2: mezcla<br>3: modulación<br>4: nivel<br>5: duración | 8 | 161 | 1 043 | 32 769 |
| `looper` | Micro-looper de 0,67 s con overdub, ½×, 2× y reverse. | 0: nivel<br>1: velocidad<br>2: sentido<br>3: realimentación | 8 | 87 | 576 | 32 769 |
| `mosaico` | Bucle sonido sobre sonido de 0,67 s que suena a la vez a ½×, 1× y 2×. | 0: octava baja<br>1: nivel<br>2: mezcla<br>3: octava alta<br>4: realimentación<br>5: difusión | 8 | 144 | 1 064 | 34 662 |
| `relevo` | Freeze de dos capas: cada pisada congela un acorde nuevo y lo funde sobre el anterior, con bend y vibrato. | 0: tiempo<br>1: afinación<br>2: mezcla<br>3: vibrato<br>4: tono<br>5: nivel | 8 | 197 | 1 438 | 34 140 |
| `resbalon` | Una cabeza libre resbala sobre lo que acabas de tocar, de −2× a 2×, sin grabar. | 0: velocidad<br>1: realimentación<br>2: mezcla<br>3: duración<br>4: tono<br>5: tiempo | 8 | 119 | 865 | 32 769 |
| `tartamudeo` | Cada ataque fuerte captura un trozo corto y lo repite, cada vez más bajo. | 0: umbral<br>1: duración<br>2: mezcla<br>3: repeticiones<br>4: velocidad<br>5: tono | 8 | 188 | 1 240 | 32 769 |

## Cadenas

Una cadena une dos programas en uno, en serie (→) o en paralelo (‖), sin cambiar el RTL (ADR 0013). Están en `presets/cadenas.toml`; `sofifi cadena` las procesa. 18 caben hoy y 6 esperan la SDRAM: solo les falta memoria.

| Cadena | Programas | Ciclos | Memoria | Registros | LFOs | Estado |
|---|---|---|---|---|---|---|
| Armonía en la placa | `armonizador` → `plate` | 1 270 | 41 539 | 14 | 3 | cabe |
| Bruma que gira | `bruma` → `chorus` | 950 | 42 654 | 12 | 4 | cabe |
| Campanas | `ringmod` → `shimmer` | 1 239 | 41 539 | 18 | 3 | cabe |
| Cinta desgastada | `cinta` → `lofi` | 1 085 | 41 600 | 18 | 3 | cabe |
| Cuerdas en ola | `tremolo` → `ensemble` | 1 288 | 38 540 | 16 | 4 | cabe |
| Doble resonancia | `doblador` → `resonador` | 879 | 1 028 | 24 | 2 | cabe |
| Eco oscuro en flor | `bbd` → `bloom` | 1 053 | 38 194 | 20 | 2 | cabe |
| Eco y muelle | `delay` → `spring` | 1 149 | 35 599 | 14 | 1 | cabe |
| Eco y resonancia | `delay` ‖ `resonador` | 870 | 33 749 | 27 | 1 | cabe |
| Flor al revés | `reverse` → `bloom` | 930 | 39 908 | 17 | 1 | cabe |
| Fuzz en la nube | `saturacion` → `cloud` | 1 248 | 42 814 | 16 | 4 | cabe |
| Loop filtrado | `looper` → `filtro` | 1 018 | 32 769 | 23 | 0 | cabe |
| Octavas en flor | `octava` ‖ `bloom` | 953 | 27 620 | 18 | 2 | cabe |
| Placa que tiembla | `tremolo` → `plate` | 1 109 | 37 439 | 14 | 2 | cabe |
| Shimmer con vibrato | `vibrato` → `shimmer` | 1 243 | 41 664 | 18 | 4 | cabe |
| Silencio y agujero negro | `puerta` → `blackhole` | 1 099 | 40 882 | 20 | 2 | cabe |
| Sustain en la placa | `compresor` → `plate` | 1 214 | 37 439 | 17 | 2 | cabe |
| Órgano infinito | `octava` → `infinite` | 1 246 | 41 539 | 13 | 4 | cabe |
| Bruma en flor | `bruma` → `bloom` | 1 181 | 65 073 | 19 | 1 | espera la SDRAM |
| Cinta en la flor | `cinta` → `bloom` | 1 129 | 65 120 | 20 | 3 | espera la SDRAM |
| Eco al revés congelado | `reverse` → `freeze` | 1 271 | 53 827 | 13 | 3 | espera la SDRAM |
| Eco en la nube | `delay` → `plate` | 1 113 | 71 188 | 15 | 3 | espera la SDRAM |
| Lluvia sobre la placa | `lluvia` → `plate` | 1 148 | 72 824 | 12 | 2 | espera la SDRAM |
| Ping-pong infinito | `pingpong` → `infinite` | 1 223 | 78 313 | 13 | 3 | espera la SDRAM |
