# ADR 0011 — El timing se mide en la placa, no se cree a nextpnr

- **Estado:** Aceptado · 2026-10-07
- **Revisión prevista:** cuando nextpnr y apicula tengan un modelo de tiempos del GW5A contrastado con el silicio, o si el proyecto pasa al IDE de Gowin para la síntesis final.

## Contexto

En la Fase 05, el núcleo fallaba en la placa a 100 MHz aunque nextpnr daba 132 MHz (fails.md, F-11). Con el mismo rutado y solo el divisor del PLL cambiado, funcionaba a 88,9 MHz. La BSRAM en modo *bypass*, la única que infiere Yosys, era la más optimista del modelo: fallaba por encima de 100 MHz con 117 MHz de análisis.

Tras segmentar el núcleo, nextpnr da 155 MHz y la placa funciona entre 106 y 114 MHz. El análisis estático es optimista en torno a un 30 %, y no de forma uniforme.

## Opciones evaluadas

1. Fiarse de nextpnr con un margen fijo (por ejemplo, exigir 130 MHz para 100).
2. Pasar al IDE de Gowin, con un modelo de tiempos propietario.
3. Medir el margen en la placa con el mismo rutado y exigirlo.

## Decisión

Opción 3, con la 1 como aviso previo.

- **Método:** `scripts/margen_reloj.py` cambia solo el divisor del PLL en el JSON rutado (colocación y rutado idénticos), vuelve a empaquetar y repite la captura del HIL (`scripts/hil_nucleo.py`) a cada frecuencia.
- **Criterio de una release del núcleo:** todas las capturas iguales al modelo a 100 MHz (3 de 3) y el margen medido declarado en `docs/mediciones.yaml`.
- **Objetivo:** que el núcleo funcione al menos a 120 MHz en la placa (margen del 20 %). Hoy no se cumple (106-114 MHz) y queda como brecha.
- **Reglas de diseño** (`docs/arquitectura_fpga.md`): ninguna salida de BSRAM va a lógica en el mismo ciclo (se usa `bsram_pipe`, con el registro de salida del bloque), y ninguna aritmética de 50 bit encadenada en un ciclo.

## Consecuencias

- Una release necesita la placa conectada. La compuerta del pre-push no la necesita.
- El margen de seguridad cuesta ciclos: el núcleo pasó de unos 6 a unos 13 ciclos por instrucción.
- La compuerta `optimizacion` (ADR 0010) sigue exigiendo que nextpnr cierre a 100 MHz, pero eso ya no basta.

## Alternativas descartadas

- **Solo un margen fijo sobre nextpnr:** el error no es uniforme. La BSRAM fallaba con un 17 % de margen aparente y el DSP llegaba a 160 MHz.
- **IDE de Gowin:** rompe la cadena libre instalable por pip (ADR 0001, Fase 02).
