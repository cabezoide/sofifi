<!-- GENERADO por `sofifi catalogo` desde programas/*.sasm. No se edita a mano:
     model/tests/catalogo_test.py lo compara con su generador. -->

# Programas del núcleo

14 programas. Cada uno es un fichero de texto en `programas/`.
Los ciclos son la cota del RTL, de 2 048 por muestra
(`model/sofifi/domain/coste.py`). La memoria es de 43 008 palabras.

## Reverb

| Programa | Qué hace | Mandos | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|
| `cloud` | Difusores largos con modulación aleatoria: el ataque se disuelve. | 0: decay<br>1: damping<br>2: mezcla<br>3: modulación | 96 | 1 385 | 42 814 |
| `freeze` | Plate que congela la cola con el pulsador. | 0: decay<br>1: damping<br>2: mezcla | 103 | 1 378 | 37 439 |
| `hall` | Red de 8 retardos con matriz de Householder: sala grande. | 0: decay<br>1: damping<br>2: mezcla | 137 | 1 585 | 34 522 |
| `plate` | Plate de Dattorro con el tanque modulado. | 0: decay<br>1: damping<br>2: mezcla | 86 | 1 202 | 37 439 |
| `shimmer` | Plate con un +12 en la realimentación: cada vuelta sube una octava. | 0: decay<br>1: damping<br>2: mezcla<br>3: cantidad de shimmer | 108 | 1 553 | 41 539 |

## Delay

| Programa | Qué hace | Mandos | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|
| `cinta` | Eco de cinta de 0,18 a 0,85 s con wow, flutter y saturación. | 0: tiempo<br>1: realimentación<br>2: mezcla<br>3: wow y flutter | 50 | 665 | 41 600 |
| `reverse` | Eco invertido en granos de 0,17 s. | 0: tono<br>1: realimentación<br>2: mezcla | 34 | 470 | 16 388 |

## Modulación

| Programa | Qué hace | Mandos | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|
| `chorus` | Tres voces con retardos que se mueven. | 0: velocidad<br>1: profundidad<br>2: mezcla | 42 | 578 | 1 101 |
| `flanger` | Retardo muy corto y móvil con realimentación: peines que barren. | 0: velocidad<br>1: profundidad<br>2: mezcla<br>3: realimentación | 31 | 384 | 247 |
| `phaser` | Cuatro allpass con coeficiente móvil: muescas que barren. | 0: velocidad<br>1: profundidad<br>2: mezcla<br>3: realimentación | 79 | 802 | 1 |
| `tremolo` | El volumen sube y baja; con pot2, de un lado a otro. | 0: velocidad<br>1: profundidad<br>2: panorama | 43 | 442 | 1 |
| `vibrato` | El tono sube y baja. | 0: velocidad<br>1: profundidad<br>2: mezcla | 27 | 344 | 125 |

## Dinámica

| Programa | Qué hace | Mandos | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|
| `swell` | Cada nota empieza en silencio y sube, antes de un plate. | 0: decay<br>1: damping<br>2: mezcla<br>3: subida | 116 | 1 490 | 37 439 |

## Textura

| Programa | Qué hace | Mandos | Instrucciones | Ciclos | Memoria |
|---|---|---|---|---|---|
| `lofi` | Menos muestras por segundo y menos bits, con aliasing. | 0: muestreo<br>1: bits<br>2: mezcla<br>3: tono | 81 | 800 | 1 |
