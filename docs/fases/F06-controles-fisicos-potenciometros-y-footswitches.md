# Fase 06 — Controles físicos: potenciómetros y footswitches

> Planificada: no está en el control hasta cerrarse.

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

## Lo que NO entra

OLED, presets.
