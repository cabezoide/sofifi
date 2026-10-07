# ADR 0005 — 2 048 ciclos exactos valen más que 48 kHz exactos

- **Estado:** Aceptado · 2026-10-07
- **Revisión prevista:** si el pedal necesita sincronizarse con audio externo (USB o S/PDIF) a 48 kHz exactos.

## Contexto

La placa solo tiene un cristal de 50 MHz, y 12,288 MHz (256 × 48 kHz) no sale de él de forma exacta. Un pedal standalone no se sincroniza con nada.

## Opciones evaluadas

1. PLL aproximada a 12,2857 MHz (fs ≈ 47,99 kHz) con un reloj de sistema arbitrario.
2. Sistema a 100 MHz y MCLK = 12,5 MHz (÷8 = 256·fs), lo que da fs = 48 828,125 Hz.
3. Oscilador de 24,576 MHz en la placa de audio.

## Decisión

Opción 2. Con ella:

- caben **2 048 ciclos de sistema por muestra, exactos**;
- todo vive en un solo dominio de reloj;
- no hace falta hardware extra;
- el PCM1808, el PCM5102A y el CS5343/CS4344 aceptan 256·fs.

## Consecuencias

- Las longitudes de delay de los papers se reescalan a 48 828,125 Hz.
- El desvío de +1,7 % respecto a 48 kHz es inaudible en un pedal.

## Alternativas descartadas

- **PLL aproximada:** el reloj de sistema y fs dejan de ser múltiplos exactos.
- **Oscilador externo:** hardware adicional sin ventaja audible.
