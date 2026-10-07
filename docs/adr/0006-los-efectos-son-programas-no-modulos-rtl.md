# ADR 0006 — Los efectos son programas, no módulos RTL

- **Estado:** Aceptado · 2026-10-07
- **Revisión prevista:** cuando el primer programa (un plate de Dattorro) corra en el núcleo. Se confirmará con el uso de LUT, DSP y BSRAM medido en síntesis.

## Contexto

El objetivo es meter "todo lo que quepa": plate, hall, cloud, shimmer, blackhole, cinta, reverse, lo-fi, freeze, micro-looper… Escribir cada efecto en Verilog multiplica el área y obliga a resintetizar cada vez que se cambia un algoritmo. El Spin FV-1 demostró que 128 instrucciones por muestra y 32K palabras bastan para reverbs comerciales.

## Opciones evaluadas

1. Un módulo RTL por efecto.
2. Un núcleo DSP microcodificado tipo FV-1, ampliado: 2 048 instrucciones por muestra, acumulador de 48 bit, datos de 24 bit, coeficientes de 18 bit e interpolación cúbica.
3. Una CPU RISC-V haciendo el DSP.

## Decisión

Opción 2. La ISA será un superconjunto de la del FV-1, lo que permite reutilizar los programas `.spn` existentes (Spin Open Reverb License) y SpinCAD como editor. Una CPU pequeña carga el microcódigo desde la microSD.

## Consecuencias

- Un efecto nuevo es un programa, sin resíntesis.
- El modelo bit-exact del núcleo (ADR 0003) es la pieza central de la Fase 1.
- Las prestaciones dependen del ancho de la ISA. Es una apuesta que se revisa con la primera síntesis.

## Alternativas descartadas

- **RTL por efecto:** no escala.
- **RISC-V para el DSP:** a 100 MHz no llega a 2 000 MAC por muestra con interpolación.
