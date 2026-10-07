# Fase 09 — Micro-looper y granular en BSRAM

> Planificada: no está en el control hasta cerrarse.

## Objetivo

Añadir un micro-looper (grabar, reproducir, overdub, ½× y 2×, reverse) y un granular sencillo de 4 voces sobre los ~0,88 s de BSRAM, al estilo Microcosm o MOOD a escala reducida.

## Origen

Investigación §3.5 y §4.3.

## Diagnóstico

- **Se reutiliza:** `CHO` con RAMP y el LFSR.
- **Falta:**
  - un modo de memoria que **congele la escritura**: el puntero circular avanza siempre, así que un loop necesita no sobrescribirse;
  - planificación aleatoria de granos.

## El hallazgo que decide el diseño

La memoria circular del FV-1 no puede guardar un loop. Su puntero avanza siempre, y lo grabado se aleja hasta desaparecer a las 43 008 muestras. Un looper necesita **direccionamiento absoluto**. La extensión mínima a la ISA es `RDAA` / `WRAA`: leer y escribir en una dirección absoluta tomada de un registro (posición de reproducción). Va con una actualización del ADR 0009.

## Diseño

- **ISA:** `RDAA reg, C` y `WRAA reg, C`, con dirección = registro × tamaño del loop. Interpolación lineal en la lectura.
- **`looper.sasm`:**
  - grabación con `sw`;
  - longitud fijada al soltar;
  - velocidad por pot (½×, 1×, 2×) y reverse.
- **`granular.sasm`:**
  - 4 granos con ventana Hann por tabla y posiciones del LFSR;
  - pitch cuantizado a 8vas.

## Plan de PRs

1. `RDAA` / `WRAA` en modelo y RTL, con contratos y actualización del ADR 0009.
2. Looper.
3. Granular, con demos.

## Criterios de aceptación

- Un loop grabado se repite idéntico N veces.
- Con 2× suena una octava arriba; con reverse sale invertido.
- El granular produce granos dentro de la ventana declarada.

## Lo que NO entra

Loops de más de 0,88 s (requieren SDRAM; ADR 0004).
