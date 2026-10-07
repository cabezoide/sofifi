# Fase 05 — Biblioteca de programas ambient

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

## Lo que NO entra

Granular y looper (Fase 06).
