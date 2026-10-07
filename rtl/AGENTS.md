# rtl/AGENTS.md — Verilog sintetizable (tiene precedencia en esta carpeta)

Vacío en la versión 0.0. Las reglas se escriben antes que el código.

## Reglas

- **Verilog-2005, o el subconjunto de SystemVerilog que aceptan a la vez Gowin
  EDA y Yosys.** Si una construcción solo la acepta una de las dos herramientas,
  no entra.
- **Un solo dominio de reloj para el audio** (100 MHz; ADR 0005). Los cruces de
  dominio (por ejemplo, con la SD) usan FIFOs asíncronas y se declaran en el
  módulo.
- **Ningún bloque DSP sin modelo** en `model/` y sin testbench de comparación en
  `sim/` (ADR 0003).
- **Cabecera SPDX** en cada fichero; lo portado se declara en `docs/terceros.yaml`.
- **Primitivas Gowin** (BSRAM, DSP, PLL) siempre detrás de un envoltorio propio,
  para poder simular y para portar a otra FPGA.

## Trampas

- apicula tiene un issue abierto con la PLLA del GW5A-25 (#427). Hay que verificar
  la frecuencia real con un contador antes de fiarse del reloj.
- Al usar BSRAM en modo 2K×9 hay que tener en cuenta que el bit 9 viene en otro
  bus.
