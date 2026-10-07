<!-- GENERADO por `sofifi catalogo` desde programas/*.sasm. No se edita a mano:
     model/tests/catalogo_test.py lo compara con su generador. -->

# Programas del núcleo

43 programas y 344 presets. Cada programa es un fichero de texto en `programas/`; los presets están en `presets/banco.toml`.
Los ciclos son la cota del RTL, de 2 048 por muestra (`model/sofifi/domain/coste.py`). La memoria es de 43 008 palabras.

## Reverb

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `blackhole` | Sala gigante con un decay de decenas de segundos. | 0: decay<br>1: damping<br>2: mezcla | 8 | 140 | 1 615 | 40 882 |
| `bloom` | La reverb crece despacio después de cada nota, como una flor que se abre. | 0: decay<br>1: damping<br>2: mezcla<br>3: apertura | 8 | 84 | 979 | 23 520 |
| `chorale` | La cola del plate canta una vocal, de «a» a «i». | 0: decay<br>1: damping<br>2: mezcla<br>3: vocal | 8 | 160 | 1 942 | 37 439 |
| `cloud` | Difusores largos con modulación aleatoria: el ataque se disuelve. | 0: decay<br>1: damping<br>2: mezcla<br>3: modulación | 8 | 96 | 1 385 | 42 814 |
| `freeze` | Plate que congela la cola con el pulsador. | 0: decay<br>1: damping<br>2: mezcla | 8 | 103 | 1 378 | 37 439 |
| `freeze_givens` | Freeze que se mueve sin perder energía: la cola congelada gira entre las ramas. | 0: decay<br>1: damping<br>2: mezcla<br>3: giro | 8 | 136 | 1 708 | 37 439 |
| `gated` | Reverb que se corta de golpe tras cada ataque, como en los años 80. | 0: decay<br>1: damping<br>2: mezcla<br>3: duración | 8 | 133 | 1 657 | 37 439 |
| `hall` | Red de 8 retardos con matriz de Householder: sala grande. | 0: decay<br>1: damping<br>2: mezcla | 8 | 137 | 1 585 | 34 522 |
| `infinite` | Plate que no decae: cada nota se suma a una capa que no se apaga. | 0: vaciado<br>1: damping<br>2: mezcla | 8 | 95 | 1 300 | 37 439 |
| `plate` | Plate de Dattorro con el tanque modulado. | 0: decay<br>1: damping<br>2: mezcla | 8 | 86 | 1 202 | 37 439 |
| `plate_vivo` | Plate cuya modulación deriva al azar: la cola nunca se repite igual. | 0: decay<br>1: damping<br>2: mezcla<br>3: vida | 8 | 127 | 1 599 | 37 439 |
| `resonador` | Cuatro cuerdas afinadas en mi mayor que vibran por simpatía con lo que se toca. | 0: sustain<br>1: excitación<br>2: mezcla<br>3: afinación | 8 | 89 | 924 | 1 |
| `reverb_inversa` | Reverb al revés: tras cada ataque, la cola crece y se corta de golpe. | 0: decay<br>1: damping<br>2: mezcla<br>3: duración | 8 | 133 | 1 657 | 37 439 |
| `shimmer` | Plate con un +12 en la realimentación: cada vuelta sube una octava. | 0: decay<br>1: damping<br>2: mezcla<br>3: cantidad de shimmer | 8 | 108 | 1 553 | 41 539 |
| `shimmer_energia` | Shimmer que se regula solo: cuanta más octava acumula, menos añade. | 0: decay<br>1: damping<br>2: mezcla<br>3: cantidad de shimmer | 8 | 117 | 1 643 | 41 539 |
| `shimmer_quinta` | Shimmer de quinta: cada vuelta sube 7 semitonos, como un acorde que se abre. | 0: decay<br>1: damping<br>2: mezcla<br>3: cantidad de shimmer | 8 | 108 | 1 553 | 41 539 |
| `spring` | Reverb de muelle: el sonido gotea, con los agudos antes que los graves. | 0: decay<br>1: damping<br>2: mezcla | 8 | 95 | 1 273 | 1 850 |

## Delay

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `bbd` | Eco analógico oscuro: cada repetición pierde agudos y se satura. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: modulación | 8 | 44 | 563 | 14 674 |
| `cinta` | Eco de cinta de 0,18 a 0,85 s con wow, flutter y saturación. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: wow y flutter | 8 | 50 | 665 | 41 600 |
| `delay` | Eco digital limpio de 20 a 690 ms, con tono en la realimentación. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: tono | 8 | 38 | 455 | 33 749 |
| `ducking` | Eco que se aparta mientras se toca y aparece en los silencios. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: ducking | 8 | 51 | 586 | 33 749 |
| `lluvia` | Seis ecos irregulares que se deshacen en allpass: una lluvia de notas. | 0: difusión<br>1: realimentación<br>2: mezcla | 8 | 46 | 593 | 35 385 |
| `pingpong` | Eco estéreo que salta de un lado a otro. | 0: tiempo<br>1: realimentación<br>2: mezcla | 8 | 38 | 497 | 40 874 |
| `reverse` | Eco invertido en granos de 0,17 s. | 0: tono<br>1: realimentación<br>2: mezcla | 8 | 34 | 470 | 16 388 |

## Modulación

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `chorus` | Tres voces con retardos que se mueven. | 0: velocidad<br>1: profundidad<br>2: mezcla | 8 | 42 | 578 | 1 101 |
| `flanger` | Retardo muy corto y móvil con realimentación: peines que barren. | 0: velocidad<br>1: profundidad<br>2: mezcla<br>3: realimentación | 8 | 31 | 384 | 247 |
| `phaser` | Cuatro allpass con coeficiente móvil: muescas que barren. | 0: velocidad<br>1: profundidad<br>2: mezcla<br>3: realimentación | 8 | 79 | 802 | 1 |
| `slicer` | Corta el sonido en pulsos rítmicos, como una puerta que abre y cierra. | 0: velocidad<br>1: profundidad<br>2: ciclo<br>3: suavizado | 8 | 37 | 390 | 1 |
| `tremolo` | El volumen sube y baja; con pot2, de un lado a otro. | 0: velocidad<br>1: profundidad<br>2: panorama | 8 | 43 | 442 | 1 |
| `vibrato` | El tono sube y baja. | 0: velocidad<br>1: profundidad<br>2: mezcla | 8 | 27 | 344 | 125 |

## Pitch

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `armonizador` | Una voz a −12, −7, −5, +5, +7 o +12 semitonos, con realimentación. | 0: intervalo<br>1: realimentación<br>2: mezcla | 8 | 55 | 632 | 4 100 |
| `doblador` | Dos voces desafinadas unos cents, una a cada lado: ensancha el sonido. | 0: desafinación<br>2: mezcla | 8 | 32 | 540 | 1 028 |
| `escalera` | Eco en el que cada repetición sube o baja un intervalo: una escalera. | 0: intervalo<br>1: realimentación<br>2: mezcla<br>3: tiempo | 8 | 67 | 799 | 39 313 |
| `octava` | Octavador: una octava abajo y una arriba, cada una con su nivel. | 0: octava baja<br>1: octava alta<br>2: seco | 8 | 25 | 470 | 4 100 |

## Dinámica

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `compresor` | Compresor: baja lo fuerte y deja lo suave; sostiene las notas. | 0: umbral<br>1: compresión<br>2: mezcla<br>3: ganancia | 8 | 57 | 596 | 1 |
| `puerta` | Puerta de ruido: calla el zumbido entre notas y deja pasar lo que se toca. | 0: umbral<br>1: cierre | 8 | 29 | 317 | 1 |
| `swell` | Cada nota empieza en silencio y sube, antes de un plate. | 0: decay<br>1: damping<br>2: mezcla<br>3: subida | 8 | 116 | 1 490 | 37 439 |

## Textura

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `lofi` | Menos muestras por segundo y menos bits, con aliasing. | 0: muestreo<br>1: bits<br>2: mezcla<br>3: tono | 8 | 81 | 800 | 1 |
| `ringmod` | Modulador en anillo: multiplica la guitarra por un seno; suena metálico. | 0: frecuencia<br>2: mezcla | 8 | 33 | 362 | 1 |
| `saturacion` | Saturación tipo overdrive: de un brillo cálido a una distorsión espesa. | 0: ganancia<br>1: tono<br>2: mezcla<br>3: nivel | 8 | 42 | 462 | 1 |

## Filtro

| Programa | Qué hace | Mandos | Presets | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|---|
| `ancho` | Ensancha el estéreo de una guitarra mono y ajusta el tono graves-agudos. | 0: ancho<br>1: tilt | 8 | 26 | 304 | 636 |
| `autowah` | Wah automático: cuanto más fuerte se toca, más sube el filtro. | 0: sensibilidad<br>1: resonancia<br>2: mezcla | 8 | 43 | 464 | 1 |
| `filtro` | Filtro paso bajo resonante que sube y baja solo, con un LFO. | 0: velocidad<br>1: resonancia<br>2: mezcla<br>3: profundidad | 8 | 60 | 608 | 1 |
