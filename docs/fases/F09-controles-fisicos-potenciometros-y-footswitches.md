# Fase 09 — Controles físicos: potenciómetros y footswitches

> Planificada: no está en el control hasta cerrarse.
>
> **Hardware que falta:** el MCP3208 y los potenciómetros (los botones de la Dock sustituyen a los footswitches). La fase va al final del plan para avanzar antes en todo lo que no lo necesita; lo que dependa de él se declara `no_verificada`.

## Objetivo

Leer 6 potenciómetros y 2 footswitches, con antirrebote y suavizado, y llevarlos a los registros `pot0`–`pot5` y `sw` del núcleo.

## Origen

ISA (ADR 0009: `pot0`–`pot5` y `sw`) e investigación §3 (ADC interno de 0–1 V, MCP3208).

## Diagnóstico

- **Se reutiliza:** el registro de entradas del núcleo.
- **Falta:**
  - lector SPI del MCP3208;
  - envoltorio del ADC interno del GW5A;
  - antirrebote;
  - filtro de un polo con zona muerta, para que no haya *zipper noise* ni temblor de la última cifra.

## El hallazgo que decide el diseño

Un potenciómetro leído con 10 o 12 bit tiembla en el LSB. En un tanque con decay ≈ 1, ese temblor modula el feedback y se oye. El suavizado no basta: hace falta **histéresis**, de modo que el valor solo cambie si se mueve más de 2 LSB. Ese bloque se escribe en el modelo antes que en el RTL.

## Diseño

- **Modelo:** `domain/controles.py`, con histéresis y suavizado.
- **RTL:**
  - `rtl/controles/mcp3208.v`, lector SPI a 1 MHz que recorre los 8 canales en ciclo;
  - `rtl/controles/antirrebote.v`, con 10 ms;
  - `rtl/controles/suavizado.v`.
- **Prueba en hardware:** los botones de la Dock (H10/H11) hacen de footswitch, y la UART informa del estado.

## Plan de PRs

1. Modelo y RTL de antirrebote y suavizado, con testbench.
2. Lector MCP3208 y prueba en hardware de los botones.

## Criterios de aceptación

- Equivalencia entre modelo y RTL.
- Los botones de la Dock se leen sin rebotes, verificado por UART.
- El MCP3208 queda `no_verificada` mientras no esté el chip.

## Ampliaciones de la Fase 03

Puntos de la hoja de ruta (`docs/investigacion/ESTADO_DEL_ARTE_2026.md`, hoja de ruta).

| Punto | Función | Hardware |
|---|---|---|
| 17 | Segunda capa con A+B mantenidos, rampas, morphing por expresión y *pickup* del mando | Jack de expresión |
| 18 | Trails al hacer bypass y kill-dry (solo señal procesada) | Ninguno |
| 19 | MIDI por TRS tipo A: program change, CC y clock; tap tempo | Falta: optoacoplador y jack TRS |

Reparto propuesto de los pulsadores:

| Acción | Función |
|---|---|
| Pulsador A | Bypass con trails |
| Pulsador B, pulsación corta | Freeze enclavado |
| Pulsador B, mantenido | Freeze momentáneo |
| A y B mantenidos | Segunda capa de mandos |

## Lo que NO entra

OLED, presets.
