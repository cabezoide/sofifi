<!-- GENERADO por `sofifi catalogo` desde programas/*.sasm. No se edita a mano:
     model/tests/catalogo_test.py lo compara con su generador. -->

# Programas del núcleo

30 programas. Cada uno es un fichero de texto en `programas/`.
Los ciclos son la cota del RTL, de 2 048 por muestra
(`model/sofifi/domain/coste.py`). La memoria es de 43 008 palabras.

## Reverb

| Programa | Qué hace | Mandos | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|
| `blackhole` | Sala gigante con un decay de decenas de segundos. | 0: decay<br>1: damping<br>2: mezcla | 140 | 1 615 | 40 882 |
| `bloom` | La reverb crece despacio después de cada nota, como una flor que se abre. | 0: decay<br>1: damping<br>2: mezcla<br>3: apertura | 84 | 979 | 23 520 |
| `cloud` | Difusores largos con modulación aleatoria: el ataque se disuelve. | 0: decay<br>1: damping<br>2: mezcla<br>3: modulación | 96 | 1 385 | 42 814 |
| `freeze` | Plate que congela la cola con el pulsador. | 0: decay<br>1: damping<br>2: mezcla | 103 | 1 378 | 37 439 |
| `gated` | Reverb que se corta de golpe tras cada ataque, como en los años 80. | 0: decay<br>1: damping<br>2: mezcla<br>3: duración | 133 | 1 657 | 37 439 |
| `hall` | Red de 8 retardos con matriz de Householder: sala grande. | 0: decay<br>1: damping<br>2: mezcla | 137 | 1 585 | 34 522 |
| `infinite` | Plate que no decae: cada nota se suma a una capa que no se apaga. | 0: vaciado<br>1: damping<br>2: mezcla | 95 | 1 300 | 37 439 |
| `plate` | Plate de Dattorro con el tanque modulado. | 0: decay<br>1: damping<br>2: mezcla | 86 | 1 202 | 37 439 |
| `reverb_inversa` | Reverb al revés: tras cada ataque, la cola crece y se corta de golpe. | 0: decay<br>1: damping<br>2: mezcla<br>3: duración | 133 | 1 657 | 37 439 |
| `shimmer` | Plate con un +12 en la realimentación: cada vuelta sube una octava. | 0: decay<br>1: damping<br>2: mezcla<br>3: cantidad de shimmer | 108 | 1 553 | 41 539 |
| `shimmer_quinta` | Shimmer de quinta: cada vuelta sube 7 semitonos, como un acorde que se abre. | 0: decay<br>1: damping<br>2: mezcla<br>3: cantidad de shimmer | 108 | 1 553 | 41 539 |
| `spring` | Reverb de muelle: el sonido gotea, con los agudos antes que los graves. | 0: decay<br>1: damping<br>2: mezcla | 95 | 1 273 | 1 850 |

## Delay

| Programa | Qué hace | Mandos | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|
| `bbd` | Eco analógico oscuro: cada repetición pierde agudos y se satura. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: modulación | 44 | 563 | 14 674 |
| `cinta` | Eco de cinta de 0,18 a 0,85 s con wow, flutter y saturación. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: wow y flutter | 50 | 665 | 41 600 |
| `delay` | Eco digital limpio de 20 a 690 ms, con tono en la realimentación. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: tono | 38 | 455 | 33 749 |
| `ducking` | Eco que se aparta mientras se toca y aparece en los silencios. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: ducking | 51 | 586 | 33 749 |
| `lluvia` | Seis ecos irregulares que se deshacen en allpass: una lluvia de notas. | 0: difusión<br>1: realimentación<br>2: mezcla | 46 | 593 | 35 385 |
| `pingpong` | Eco estéreo que salta de un lado a otro. | 0: tiempo<br>1: realimentación<br>2: mezcla | 38 | 497 | 40 874 |
| `reverse` | Eco invertido en granos de 0,17 s. | 0: tono<br>1: realimentación<br>2: mezcla | 34 | 470 | 16 388 |

## Modulación

| Programa | Qué hace | Mandos | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|
| `chorus` | Tres voces con retardos que se mueven. | 0: velocidad<br>1: profundidad<br>2: mezcla | 42 | 578 | 1 101 |
| `flanger` | Retardo muy corto y móvil con realimentación: peines que barren. | 0: velocidad<br>1: profundidad<br>2: mezcla<br>3: realimentación | 31 | 384 | 247 |
| `phaser` | Cuatro allpass con coeficiente móvil: muescas que barren. | 0: velocidad<br>1: profundidad<br>2: mezcla<br>3: realimentación | 79 | 802 | 1 |
| `tremolo` | El volumen sube y baja; con pot2, de un lado a otro. | 0: velocidad<br>1: profundidad<br>2: panorama | 43 | 442 | 1 |
| `vibrato` | El tono sube y baja. | 0: velocidad<br>1: profundidad<br>2: mezcla | 27 | 344 | 125 |

## Pitch

| Programa | Qué hace | Mandos | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|
| `armonizador` | Una voz a −12, −7, −5, +5, +7 o +12 semitonos, con realimentación. | 0: intervalo<br>1: realimentación<br>2: mezcla | 55 | 632 | 4 100 |
| `doblador` | Dos voces desafinadas unos cents, una a cada lado: ensancha el sonido. | 0: desafinación<br>2: mezcla | 32 | 540 | 1 028 |
| `escalera` | Eco en el que cada repetición sube o baja un intervalo: una escalera. | 0: intervalo<br>1: realimentación<br>2: mezcla<br>3: tiempo | 67 | 799 | 39 313 |
| `octava` | Octavador: una octava abajo y una arriba, cada una con su nivel. | 0: octava baja<br>1: octava alta<br>2: seco | 25 | 470 | 4 100 |

## Dinámica

| Programa | Qué hace | Mandos | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|
| `swell` | Cada nota empieza en silencio y sube, antes de un plate. | 0: decay<br>1: damping<br>2: mezcla<br>3: subida | 116 | 1 490 | 37 439 |

## Textura

| Programa | Qué hace | Mandos | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|
| `lofi` | Menos muestras por segundo y menos bits, con aliasing. | 0: muestreo<br>1: bits<br>2: mezcla<br>3: tono | 81 | 800 | 1 |
