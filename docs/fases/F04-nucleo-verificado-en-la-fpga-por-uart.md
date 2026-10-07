# Fase 04 — Núcleo verificado en la FPGA por UART

> Planificada: no está en el control hasta cerrarse.

## Objetivo

Ejecutar el núcleo **en la placa real** a 100 MHz y fs = 48 828 Hz, con una señal de prueba en ROM. La salida se envía por UART y se compara bit a bit con el modelo: verificación hardware-in-the-loop sin necesidad del códec.

## Origen

Fase 02 (UART y programación) y Fase 03 (núcleo RTL equivalente en simulación).

## Diagnóstico

- **Se reutiliza:** UART TX, núcleo, PLL y la cadena de programación.
- **Falta:**
  - PLL de 50 a 100 MHz;
  - generador del tick de 48 828 Hz;
  - ROM de estímulo;
  - FIFO entre el dominio de audio y la UART;
  - `scripts/hil_nucleo.py`, que captura, compara e informa.

## El hallazgo que decide el diseño

La UART a 3 Mbaud o menos no transporta 48 828 muestras/s × 48 bit (2,3 Mbit/s más el encuadre) con margen. Por eso la prueba captura **N muestras en BSRAM a velocidad real** y después las vuelca despacio. Así se verifica el tiempo real sin exigirle ancho de banda a la UART.

## Diseño

- **Top `rtl/top/hil_nucleo.v`:**
  - PLL a 100 MHz;
  - núcleo con el plate precargado (`$readmemh`);
  - estímulo: un impulso más un tono en ROM;
  - captura de 4 096 muestras estéreo;
  - volcado por UART a 115 200 baud con CRC.
- **`scripts/hil_nucleo.py`:** programa la placa, lee la captura, la compara con el modelo y registra el resultado en `docs/mediciones.yaml`.

## Plan de PRs

1. PLL y reloj de muestra medidos por UART: contar ticks contra el cristal.
2. Captura, volcado y comparación HIL, con medición.

## Criterios de aceptación

- 4 096 muestras estéreo del plate idénticas al modelo, capturadas en la placa.
- fs medida = 48 828 ± 1 Hz (verifica la promesa P-002).

## Lo que NO entra

Códec, controles.
