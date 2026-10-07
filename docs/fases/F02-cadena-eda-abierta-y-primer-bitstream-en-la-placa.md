# Fase 02 — Cadena EDA abierta y primer bitstream en la placa

> Cerrada el 2026-10-07. Enmiendas respecto de esta spec: ver la fila 02 de `docs/fases/estado_fases.csv`.

## Objetivo

Sintetizar, colocar, rutear y programar la Tang Primer 25K desde el repositorio con herramientas instalables por pip. El primer bitstream debe demostrar que funciona: que la FPGA hable por la UART del depurador.

## Origen

ADR 0001: la síntesis era compuerta de release pendiente. Además, la placa está conectada al equipo de desarrollo (BL616 = FT2232 `0403:6010`, `/dev/ttyUSB0` y `/dev/ttyUSB1`).

## Diagnóstico

- **Se reutiliza:**
  - `scripts/ci_local.sh`, con su trabajo blando `rtl-lint`;
  - los pines verificados en los ejemplos de Sipeed y apicula: reloj E2, UART TX C3 / RX B3, botones H10/H11, LED L6.
- **Falta:**
  - Yosys (YoWASP), nextpnr-himbaechel-gowin, apicula, openFPGALoader, verilator y cocotb en `.venv`;
  - objetivos `make synth` y `make prog`;
  - informe de recursos;
  - UART de transmisión en RTL;
  - permisos USB (regla udev).

## El hallazgo que decide el diseño

Sin el códec no hay audio, pero la UART del propio depurador es un canal de datos bidireccional que ya existe. Todo lo que el pedal calcula se puede sacar por ahí y compararlo en el PC con el modelo. La UART se convierte así en el **banco de pruebas en hardware** de las fases siguientes.

## Diseño

- `rtl/top/primer25k.cst`: constraints de pines.
- `rtl/comun/uart_tx.v`: UART de transmisión.
- `rtl/top/hola_uart.v`: top que envía "SOFIFI <contador>\r\n" una vez por segundo.
- `scripts/fpga.sh`: síntesis → PnR → pack → programación SRAM.
- `scripts/leer_uart.py`: lectura de la UART con pyserial.
- **Compuertas:**
  - `rtl-lint` pasa a dura, porque verilator se instala con pip y todo el mundo puede correrla;
  - `synth` queda como compuerta de release y escribe `build/informe_recursos.json`.

## Plan de PRs

1. Herramientas, Makefile, UART TX con testbench cocotb y `rtl-lint` dura.
2. Top, constraints, síntesis y programación. Medición MED de recursos y del mensaje recibido.

## Criterios de aceptación

- `make synth` produce el bitstream.
- `make prog` lo carga en SRAM.
- `scripts/leer_uart.py` recibe "SOFIFI" desde la placa.

## Lo que NO entra

Núcleo DSP, audio, flash (se programa solo la SRAM).
