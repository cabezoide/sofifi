# Fase 11 — Audio I2S con el códec PCM1808 y PCM5102A

> Planificada: no está en el control hasta cerrarse.
>
> **Hardware que falta:** el códec I2S (PCM1808 + PCM5102A o Pmod I2S2). La fase va al final del plan para avanzar antes en todo lo que no lo necesita; lo que dependa de él se declara `no_verificada`.

## Objetivo

Tener el RTL de audio real: maestro I2S (MCLK 12,5 MHz, BCLK 3,125 MHz, LRCK 48 828 Hz), recepción del ADC y transmisión al DAC. Debe quedar verificado en simulación y listo para la placa en cuanto llegue el códec.

## Origen

ADR 0005 (relojes) e investigación §8.5 (códec recomendado).

## Diagnóstico

- **Se reutiliza:** el tick de muestra y el núcleo.
- **Falta:**
  - `i2s_maestro.v`;
  - modelos cocotb de un ADC y un DAC I2S;
  - top de paso directo (passthrough) y top con efecto;
  - asignación de pines a un PMOD.

## El hallazgo que decide el diseño

El PCM1808 exige SCKI = 256·fs **sincronizado** con LRCK, y el PCM5102A tolera que no llegue SCK. Si los tres relojes salen de un único contador a 100 MHz (÷8, ÷32, ÷2 048), la sincronía es correcta por construcción y no hay cruces de dominio de reloj.

## Diseño

- **Relojes:** MCLK = clk/8, BCLK = clk/32 (64·fs) y LRCK = clk/2 048, todos con fase fija.
- **Formato:** I2S estándar de 24 bit en tramas de 32 bit.
- **Pines:** PMOD 1 de la Dock, con MCLK, BCLK, LRCK, DOUT del ADC y DIN del DAC.
- **Verificación:** testbench con un ADC simulado que envía una rampa conocida y un DAC simulado que la recibe.

## Plan de PRs

1. `i2s_maestro.v` con su testbench.
2. Tops `passthrough` y `efecto`, con pines y guía de cableado del códec.

## Criterios de aceptación

- Ida y vuelta exacta en simulación, con la latencia en muestras declarada.
- Bitstream generado.
- La prueba con el códec físico se declara `no_verificada` hasta que haya códec.

## Ampliaciones de la Fase 03

Punto 21 de la hoja de ruta (`docs/investigacion/ESTADO_DEL_ARTE_2026.md`, hoja de ruta): medir y publicar la latencia total y la relación señal/ruido real, no la de la ficha del códec. Se registran en `docs/mediciones.yaml`.

## Lo que NO entra

Front-end analógico, controles.
