# ADR 0004 — La microSD almacena, no retarda

- **Estado:** Aceptado · 2026-10-07
- **Revisión prevista:** cuando se instale el módulo SDRAM de Sipeed. Se añadirá una actualización con el nuevo mapa de memoria.

## Contexto

El hardware disponible es una Tang Primer 25K con Dock y una microSD de 64 GB. No hay SDRAM. Una línea de retardo con realimentación necesita leer y escribir cada muestra con latencia determinista. La microSD tiene latencias de ms y picos de escritura de hasta 250 ms (especificación SDHC); absorberlos exigiría FIFOs mayores que toda la BSRAM.

## Opciones evaluadas

1. Usar la microSD como memoria de delay con FIFOs.
2. Todo el audio en BSRAM y la microSD solo como almacenamiento.
3. Esperar a tener SDRAM.

## Decisión

Opción 2.

- **BSRAM:** 56 bloques de 18 Kbit. Tras reservar unos 12 bloques para CPU, microcódigo, FIFOs y tablas quedan unas 45 000 palabras de delay. Eso da 0,92 s a 18 bit y fs = 48,8 kHz, o 2,8 s en μ-law de 9 bit a 32 kHz.
- **Reparto por programa:** la memoria se reparte por programa, como en el FV-1. Cada preset dispone de toda la RAM de delay.
- **microSD:** guarda presets, microcódigo, tablas y grabaciones WAV de depuración. Un looper en streaming queda como experimento tardío y sin garantías.

## Consecuencias

- No entran en esta etapa el looper largo, el granular largo ni los delays de minutos.
- El núcleo accede a una "memoria de delay" abstracta, para que la SDRAM se pueda añadir después sin rediseñarlo.

## Alternativas descartadas

- **SD como delay:** latencia no determinista.
- **Esperar:** bloquea todo lo que sí cabe.
