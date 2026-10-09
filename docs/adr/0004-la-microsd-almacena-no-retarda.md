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

## Actualización 2026-10-07 (Fase 01, ADR 0008)

La reserva sube de unos 12 a **14 bloques**: el microcódigo de 54 bit para 2 048 instrucciones ocupa 6 bloques (2 048 × 54 bit), no 4. La memoria de retardo queda en **42 bloques = 43 008 palabras** de 18 bit, unos 0,88 s a 48 828 Hz. La decisión no cambia.

## Actualización 2026-10-09 (Fase 08: pines de la microSD)

La microSD va en un **Sipeed PMOD TF**, en el conector **J6** del Dock (dato de la persona propietaria). `rtl/top/primer25k.cst` añade sus pines. Las bolas salen del esquema del Dock y de los dos esquemas del PMOD TF de Sipeed [V]:

| Señal | PMOD TF v2 | PMOD TF v1 |
|---|---|---|
| CS | F5 | G5 |
| SCK | H5 | G8 |
| MOSI | G7 | G7 |
| MISO | H8 | H8 |

- La revisión del módulo no está serigrafiada. El top `prueba_sd` prueba la v2 y, si la tarjeta no arranca, la v1. Los pines de la otra revisión quedan en alta impedancia: en modo SPI son DAT1 y DAT2, que la tarjeta no usa.
- Ningún `.cst` publicado usa el PMOD TF en J6. La v1 está comprobada contra un `.cst` de Sipeed en J4. La correspondencia de la v2 sale de `.cst` de terceros en J4 [INF].
- La v1 no tiene pull-ups: MISO lleva `PULL_MODE=UP`.
- La decisión no cambia: la microSD almacena el banco y no retarda audio.
