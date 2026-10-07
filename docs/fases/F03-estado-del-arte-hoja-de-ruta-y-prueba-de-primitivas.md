# Fase 03 — Estado del arte, hoja de ruta y prueba de primitivas

> Planificada: no está en el control hasta cerrarse.

## Objetivo

Saber qué hace un pedal ambient de referencia en 2026 y decidir qué añadir a SOFIFI. Después, quitar el mayor riesgo técnico antes del núcleo RTL: tres primitivas de la FPGA sin probar.

## Origen

La persona propietaria pidió una fase intermedia de investigación. Quiere que SOFIFI sea el pedal ambient de referencia.

La fase va antes del núcleo RTL (Fase 04). Cambiar la ISA (ADR 0009) es barato antes de escribir el RTL y caro después.

## Diagnóstico

- **Se reutiliza:**
  - `docs/investigacion/INVESTIGACION.md`, la investigación de partida;
  - la cadena EDA y el banco de pruebas por UART de la Fase 02;
  - la compuerta `optimizacion` (ADR 0010).
- **Falta:**
  - una investigación actual del mercado, de arXiv y de las plataformas abiertas;
  - una hoja de ruta con coste por función;
  - las specs posteriores actualizadas con esa hoja de ruta;
  - una prueba en placa de los bloques DSP 27×18, de la BSRAM de doble puerto y del PLL.

## El hallazgo que decide el diseño

A SOFIFI le sobra cómputo y le falta memoria. Tiene 2 048 instrucciones por muestra, 16 veces las del FV-1 [?]. Pero solo tiene 0,88 s de memoria de retardo, y los pedales insignia tienen loopers de 30 a 60 s [V].

Casi toda la mejora de calidad que propone la investigación se ejecuta como programa:

- modulación aleatoria filtrada;
- matriz de Givens en el freeze;
- FDN incolora;
- difusor de velvet noise.

Todo eso cuesta menos de 250 instrucciones y no cambia la ISA [INF].

El riesgo real está en la cadena de herramientas. Hasta hoy solo se usaron LUT, ALU, DFF e IOB. El núcleo necesita además bloques DSP, BSRAM de doble puerto y un PLL a 100 MHz. Ninguno de los tres está probado con apicula.

## Diseño

- **Informe:** `docs/investigacion/ESTADO_DEL_ARTE_2026.md`, con una hoja de ruta de 27 puntos.
- **Specs:** cada spec posterior recibe la sección «Ampliaciones de la Fase 03» con sus puntos de la hoja de ruta.
- **Pruebas de primitivas:** tres tops pequeños en `rtl/top/`. Cada uno informa por la UART.
  - `prueba_dsp.v`: multiplicaciones 27×18 conocidas. Compara el resultado con el esperado.
  - `prueba_bsram.v`: escribe un patrón por un puerto y lo lee por el otro en el mismo ciclo.
  - `prueba_pll.v`: genera 100 MHz desde el cristal de 50 MHz. Cuenta ciclos durante un segundo del cristal.
- Cada top entra en `rtl/top/tops.txt` y recibe sus listones de recursos (ADR 0010).

## Plan de PRs

1. Informe, hoja de ruta, specs actualizadas y renumeración de las fases 03 a 11, que pasan a ser 04 a 12.
2. Pruebas de primitivas: tops, testbenches cocotb y medición en placa.

## Criterios de aceptación

- El informe está en el repositorio, con marcas de confianza y fuentes.
- Cada punto de la hoja de ruta tiene una fase asignada, o queda «posterior a 12».
- Los tres tops pasan su testbench y la compuerta `optimizacion`.
- En la placa, la UART informa:
  - productos DSP iguales a los esperados;
  - lectura de BSRAM igual a la escritura;
  - 100 000 000 ± 100 ciclos del PLL por segundo del cristal.
- Si una primitiva falla, el fallo se documenta y el ADR afectado se actualiza antes de la Fase 04.

## Lo que NO entra

- Implementar funciones de la hoja de ruta: cada una va en su fase.
- SDRAM, coprocesador STFT, MIDI y USB-MIDI: van después de la Fase 12.
