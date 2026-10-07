# Fase 06 — Biblioteca de programas ambient

> Planificada: no está en el control hasta cerrarse.

## Objetivo

Ampliar la biblioteca más allá de plate, shimmer y freeze, con los algoritmos de la investigación: hall FDN, cloud, cinta, reverse, lo-fi y swell. Cada uno con su prueba acústica y su huella.

## Origen

Investigación §1.1 (catálogo de algoritmos) y §4.3 (lista de efectos).

## Requisito previo (de la Fase 05)

El núcleo segmentado gasta unos 13 ciclos por instrucción: el shimmer usa 1 601 de 2 048 (MED-11). Los programas de esta fase no caben así. Primer PR de la fase: **leer la instrucción siguiente mientras se ejecuta la actual** y solapar la escritura del ACC con esa lectura, con el margen de reloj medido en la placa por encima del 20 % (ADR 0011, MED-14).

**Estado (2026-10-07):** hecho en el primer PR de la fase, con una diferencia.

- Lectura adelantada: sí. Margen en la placa: **al menos un 20 %** (120 MHz, 4 de 4; MED-14).
- Para llegar al margen hubo que segmentar la memoria de retardo y el banco de registros (fails.md, F-15). Eso gasta parte de lo que ahorra la lectura adelantada: el shimmer baja de 1 601 a 1 514 ciclos (MED-11), unos 14 ciclos por instrucción.
- La escritura del ACC **no** se solapa todavía: cada instrucción espera a su resultado. Caben unas 145 instrucciones por muestra, más que las 128 del FV-1. Si un programa de esta fase no cabe, el siguiente paso es no esperar cuando la instrucción siguiente no depende del resultado (`docs/arquitectura_fpga.md`).

## Diagnóstico

- **Se reutiliza:** núcleo, ensamblador y el patrón de pruebas de `model/tests/programas_test.py`.
- **Falta:** los programas y, posiblemente, una directiva `include` para no duplicar bloques comunes (enmienda 5 de la Fase 01).

## El hallazgo que decide el diseño

Con 43 008 palabras, cada preset dispone de toda la memoria (ADR 0004). Los efectos no se reparten la RAM: **se diseñan uno a uno para llenarla**. El cloud usa líneas largas, la cinta usa casi 0,9 s de delay, y así con los demás. La memoria es la restricción y no el cómputo, porque ninguno pasa de unos 300 ciclos de 2 048.

## Diseño

| Programa | Qué es |
|---|---|
| `hall.sasm` | FDN de 8 líneas con matriz Householder, T60 por pot y damping |
| `cloud.sasm` | Difusores largos en cascada con modulación aleatoria (RND), al estilo CloudSeed |
| `cinta.sasm` | Delay de hasta 0,85 s con wow/flutter (SIN + RND), saturación `clip` en el bucle y filtros |
| `reverse.sasm` | Reverse delay con doble buffer y ventanas complementarias (RAMP) |
| `lofi.sasm` | Reducción de bits y de sample rate con aliasing, por S&H en registro |
| `swell.sasm` | Detector de ataque con envolvente (`maxx`/`rdfx`) y rampa de volumen antes de la reverb |

Además, la directiva `include` en el ensamblador.

## Plan de PRs

1. `include` en el ensamblador + hall + cloud.
2. Cinta + reverse.
3. Lo-fi + swell + demos regeneradas.

**Estado del PR 1 del plan (2026-10-07):** hecho, con estas diferencias.

- **`include`:** `include ruta` inserta otro fichero, con la ruta relativa a la carpeta del programa. El ensamblador sigue puro: recibe una función que lee el fichero. Plate, shimmer y freeze comparten seis bloques de `programas/comun/` y sus huellas no cambian.
- **Coste en el RTL (no estaba en el plan):** `model/sofifi/domain/coste.py` da los ciclos de cada instrucción en el RTL, medidos en simulación. Sin él, «cabe en el núcleo» comprobaba 1 ciclo por instrucción y no servía.
- **Hall:** FDN de 8 líneas (55-103 ms) con Householder, 1 578 ciclos y 34 522 palabras. T60 de 0,6 s (pot0 = 0,2), 2,1 s (pot0 = 0,8) y 8,1 s (pot0 = 1, sin damping). Todas las líneas usan el mismo kdecay: la ISA no tiene `exp` para dar a cada línea su ganancia.
- **Cloud:** seis difusores largos (13-56 ms) y un tanque en ocho, 1 356 ciclos y 42 814 palabras. El LFO RND sigue a su objetivo en unos 1,3 ms: con una excursión grande, el tono salta. Por eso los difusores usan una excursión de 4 muestras y el tanque, un LFO senoidal.
- **Prueba del cloud:** mide la modulación como pérdida de invariancia. Con pot3 = 0, un impulso retrasado da la misma cola, bit a bit; con pot3 = 1, no.
- **El cloud no cabe en `hil_nucleo`** (38 bloques de retardo). Los programas nuevos están probados en simulación, no en la placa.

**Estado del PR 2 del plan (2026-10-07):** hecho, con estas diferencias.

- **Cinta:** eco de 0,18 a 0,85 s, 658 ciclos y 41 600 palabras. La ISA no tiene un puntero de lectura variable. El tiempo sale de un LFO senoidal parado en un cuarto de vuelta: el retardo del `CHO` sigue a `lfo0_depth`. Al girar pot0, el tono del eco se desliza, como en una cinta.
- **Wow y flutter con dos LFO senoidales**, no con SIN + RND. El LFO RND salta de tono (ver el cloud) y en una cinta se oye como un defecto.
- **Reverse:** granos de 0,17 s, 431 ciclos y 16 388 palabras. El grano dura W/2 y la ventana W del LFO RAMP no pasa de 16 384 muestras. Para granos más largos hay que ampliar W en `ConfigLfo` (ADR 0009).
- **La compuerta no ve el eco de la cinta:** compara 1 000 muestras y el primer eco llega a las 8 782. La aceptación usa 12 000 muestras con pot0 = 0.
- Las huellas de cinta y reverse duran 0,6 s y 0,4 s: en 0,1 s solo suena la señal seca.

**Estado del PR 3 del plan (2026-10-07):** hecho, con estas diferencias.

- **Lo-fi:** muestreo de 48,8 kHz a ~1 kHz y 24, 12, 10, 8 o 7 bit, 620 ciclos. La ISA no tiene AND. El cuantizador escala la muestra por 2^-(23-b), la redondea con `WRAX` y la multiplica por casi 2 con `SOF` (23-b) veces. Por debajo de 7 bit haría falta un coeficiente menor que 2^-16.
- **Swell:** detector de ataque con dos envolventes y ganancia² antes del plate, 1 467 ciclos. Usa `rdfx` y `absa`, no `maxx`. La subida va de ~50 ms a ~1,3 s.
- **El tanque del plate** pasa a `comun/dattorro_tanque.sasm`: lo comparten plate y swell.
- La mezcla deja pasar un −0,1 % de señal seca con pot2 = 1 (`comun/mezcla.sasm`, D = 0,999). La prueba del lo-fi mete la señal por la derecha y mide la izquierda.
- Las demos están en PCM de 16 bit (15,2 MB). La compuerta `secrets` ya no limita su total, solo 4 MiB por demo (ADR 0001, actualización).

**Ampliación (2026-10-07): catálogo de familias.** La persona propietaria pide todos los efectos posibles del estado del arte. Son unos 35-40 algoritmos distintos (investigación §4.3 y hoja de ruta de la Fase 03); los cientos de variantes salen de presets. Se hace en lotes de unos 5 programas por PR, y después un banco de presets.

- **Lote 1, modulación:** chorus (3 voces), flanger, phaser (4 etapas), trémolo con autopan y vibrato. Trémolo y phaser usan un LFO triangular por software (`comun/lfo_triangulo.sasm`): los LFO del núcleo no se pueden leer.
- `docs/programas.md` se genera con `sofifi catalogo` desde la cabecera de cada programa (`; familia:`, `; resumen:`, `; potN =`).

## Criterios de aceptación

- Cada programa cabe en el núcleo.
- Cada programa tiene una prueba acústica que mide su propiedad característica: decay, modulación, inversión temporal o envolvente.
- Huellas y demos regeneradas.

## Ampliaciones de la Fase 03

Puntos de la hoja de ruta (`docs/investigacion/ESTADO_DEL_ARTE_2026.md`, hoja de ruta). Ninguno cambia la ISA.

| Punto | Programa o herramienta | Coste estimado [INF] |
|---|---|---|
| 2 | Modulación aleatoria filtrada (LFSR) en el plate | 3-4 instrucciones por línea |
| 3 | Matriz de Givens con LFO en el freeze: modula sin perder energía | +10-20 instrucciones |
| 4 | Detección de ataque con swell, ducking y auto-freeze | < 50 instrucciones |
| 5 | FDN incolora de 4-8 líneas y difusor de velvet noise | 100-220 instrucciones |
| 6 | Ajuste DDSP en el PC con cuantización simulada | 0 en el pedal |
| 7 | Shimmer con criterio energético | 20-60 instrucciones |
| 8 | Cinta: wow/flutter, saturación y «stretch» por pasos armónicos | 40-70 instrucciones |
| 9 | Ensemble de 3 voces | 25-30 instrucciones |
| 10 | Traductor de SpinASM a SOFIFI | 0 en el pedal |

La matriz de Givens se verifica primero en el modelo bit-exact: la cuantización a 18 bit puede romper su ortogonalidad (ADR 0008).

## Lo que NO entra

Granular y looper (Fase 07).
