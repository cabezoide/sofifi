# Fase 04 — Núcleo DSP en RTL equivalente al modelo

> Cerrada el 2026-10-07. Enmiendas respecto de esta spec: ver la fila 04 de `docs/fases/estado_fases.csv`.

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

## Ampliaciones de la Fase 03

Hoja de ruta (`docs/investigacion/ESTADO_DEL_ARTE_2026.md`, hoja de ruta). El núcleo no las implementa, pero **reserva su sitio** para no rehacer la ISA después:

- códigos de operación para `RDAA` y `WRAA`, el direccionamiento absoluto (punto 11, Fase 07);
- un flag de acceso para la línea de retardo en coma flotante de 12 bit (punto 14, Fase 07);
- un LFO que entregue seno y coseno a la vez, para la matriz de Givens (punto 3, Fase 06).

## Hallazgos de la Fase 03 (primitivas en la placa)

| Primitiva | Resultado | Consecuencia para el núcleo |
|---|---|---|
| DSP 27×18 | Yosys no lo infiere para gw5a. `rtl/primitivas/mult_27x18.v` instancia `MULT27X36`, que ocupa 2 de los 28 bloques. 2 500 productos sin error (MED-06). | El diseño dice «MULT27X18 inferido»: se usa el envoltorio. Estudiar `MULTALU27X18` (1 bloque, con acumulador) si hacen falta más multiplicadores. |
| BSRAM | 43 008 × 18 se infiere como 42 DPX9B. 1 600 millones de lecturas sin error, también con colisión (MED-07). | El array único funciona. Su multiplexor de salida cuesta unos 1 270 MUX2: se puede cambiar por un OR si los bloques no seleccionados ponen su salida a 0 con RESET [INF]. |
| PLL | 100 MHz exactos respecto al cristal (MED-08). apicula exige fijar todos los divisores. | Usar `rtl/primitivas/pll_100.v`. |

## Lo que NO entra

I2S, SD, controles físicos.
