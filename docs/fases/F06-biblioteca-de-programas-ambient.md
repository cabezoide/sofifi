# Fase 06 — Biblioteca de programas ambient

> Planificada: no está en el control hasta cerrarse.

## Objetivo

Ampliar la biblioteca más allá de plate, shimmer y freeze, con los algoritmos de la investigación: hall FDN, cloud, cinta, reverse, lo-fi y swell. Cada uno con su prueba acústica y su huella.

## Origen

Investigación §1.1 (catálogo de algoritmos) y §4.3 (lista de efectos).

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
