# Fase 03 — Núcleo DSP en RTL equivalente al modelo

> Planificada: no está en el control hasta cerrarse.

## Objetivo

Escribir el núcleo de la ISA de 54 bit (ADR 0009) en Verilog y demostrar en simulación que, para los programas plate, shimmer y freeze, coincide **muestra a muestra** con el modelo (ADR 0003).

## Origen

Fase 01 (modelo bit-exact) y Fase 02 (cadena EDA y verilator).

## Diagnóstico

- **Se reutiliza:**
  - la semántica, los formatos y las tablas del modelo;
  - el volcado `.hex` de `sofifi asm`.
- **Falta:**
  - decodificador, ALU de 48 bit, banco de registros y memoria de retardo en BSRAM;
  - LFOs, ROM Hermite, `curva_suave` y secuenciador de muestra;
  - testbench cocotb que compare contra el modelo.

## El hallazgo que decide el diseño

El modelo ejecuta las instrucciones una detrás de otra, con efectos inmediatos. En hardware, las lecturas de BSRAM tardan un ciclo y el multiplicador está segmentado. Un pipeline con adelantamiento rompería la equivalencia de formas sutiles. Por eso la primera versión es **multiciclo sin solapamiento**, cuatro o cinco ciclos por instrucción. Aun así cabe: el plate usa unas 100 instrucciones × 5 ciclos = 500 de 2 048. Se optimiza solo cuando un programa lo necesite.

## Diseño

- **Interfaz con el exterior:** `rtl/nucleo/nucleo.v` recibe `muestra_tick`, entradas, pots y sw, y entrega las salidas.
- **Microcódigo:** BSRAM de 2 048×54, cargable por un puerto de escritura.
- **Memoria de retardo:** 42 bloques de 1K×18 inferidos como un solo array, con puntero decreciente.
- **Multiplicaciones:** 24×18 → `MULT27X18` inferido; `MULX` 24×24 en dos pasos.
- **Tablas:** ROM Hermite generada por el modelo (`sofifi tablas`).
- **Verificación:** `sim/nucleo/` con cocotb sobre verilator. Carga el `.hex`, alimenta impulsos y tonos y compara con `procesar()`.

## Plan de PRs

1. ALU y formatos, con pruebas unitarias contra `aritmetica.py`.
2. Memoria, LFOs y Hermite.
3. Secuenciador, instrucciones y comparación con plate, shimmer y freeze.

## Criterios de aceptación

- Igualdad exacta con el modelo en 0,1 s de impulso para los tres programas, y en 1 s para el plate.
- La síntesis cabe y cierra timing a 100 MHz. Si no cierra, se declara la frecuencia real y se revisa el ADR 0005.

## Lo que NO entra

I2S, SD, controles físicos.
