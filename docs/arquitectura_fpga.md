# Arquitectura del FPGA

Qué hay dentro de la FPGA, cómo se conecta y cómo ha cambiado fase a fase. Se actualiza al cerrar cada fase y en cada PR que cambie bloques del FPGA. La explicación sencilla de cada componente está en `SBOM.md`; los fallos que dieron forma al diseño, en `fails.md`.

Chip: **Gowin GW5A-LV25** (Tang Primer 25K): 23 040 LUT4, 56 bloques de BSRAM de 18 Kbit, 28 bloques DSP, 6 PLL.

## Vista general (Fase 05)

```
 cristal 50 MHz ─► PLL ─► 100 MHz ──────────────────────────────────────────┐
                                                                            │
 ROM del programa ─► cargador ─► microcódigo (2 048 × 54, BSRAM) ─┐          │
                                                                  ▼          │
 tick 48 828 Hz ─► ┌──────────────── NÚCLEO DSP ─────────────────────────┐   │
 (cada 2 048 ciclos)│ secuenciador ─► decodificación ─► operandos        │   │
                    │      │                              │               │   │
 entradas ─────────►│ banco de registros (64 × 24)   multiplicador 27×36 │   │
 (adc, pots, sw)    │      │                         (2 bloques DSP)      │   │
                    │ LFO ×4 · ROM Hermite · curva suave    │             │   │
                    │      │                               ▼             │   │
                    │ memoria de retardo (38–42 BSRAM) ─► ALU (2 etapas) ─► ACC
                    └──────────────────────────────────────────────────────┘
                                         │
                                         ▼  dac_l, dac_r
 UART RX ─► órdenes ─► captura (BSRAM) ─► volcado + CRC-32 ─► UART TX ─► PC
```

Todo corre en **un solo dominio de reloj de 100 MHz** (ADR 0005). La única excepción es el medidor de frecuencia de las pruebas, que cruza al dominio del cristal en código Gray.

## Bloques

| Bloque | Fichero | Recursos | Latencia |
|---|---|---|---|
| PLL 50 → 100 MHz | `rtl/primitivas/pll_100.v` | 1 PLLA | — |
| Generador de muestra | `rtl/comun/generador_muestra.v` | ~20 LUT | 1 tick / 2 048 ciclos |
| Secuenciador del núcleo | `rtl/nucleo/nucleo.v` | la mayor parte de la lógica | ~13 ciclos por instrucción |
| Microcódigo | `bsram_pipe` 2 048 × 54 | 6 BSRAM | 3 ciclos |
| Banco de registros | dentro de `nucleo.v` | 64 × 24 en flip-flops | 1 ciclo (en la decodificación) |
| Multiplicador | `rtl/primitivas/mult_27x36.v` + 2 registros | 2 DSP | 5 ciclos (`LAT`) |
| ALU | `rtl/nucleo/alu.v` | ~1 000 LUT y 300 ALU | 2 etapas + escritura |
| Memoria de retardo | `rtl/nucleo/memoria_retardo.v` + `bsram_pipe` | 1 BSRAM por cada 1 024 palabras | 5 ciclos (`LAT`) |
| LFO ×4 | `rtl/nucleo/lfo_banco.v` | ~380 LUT y 377 ALU | 26 ciclos por muestra |
| ROM Hermite | `rtl/nucleo/tabla_hermite.v` (generada) | ~820 LUT | combinacional + registro |
| Curva suave | `rtl/nucleo/curva_fin.v` | una resta y una saturación | registrada |
| UART TX / RX | `rtl/comun/uart_tx.v`, `uart_rx.v` | ~50 LUT cada una | 115 200 baudios |
| Cargador de programa | `rtl/comun/carga_programa.v` | ~30 LUT | instrucciones + 1 ciclos |

## Presupuesto (top `hil_nucleo`, Fase 05)

| Recurso | Uso | Notas |
|---|---|---|
| LUT4 | ~8 600 de 23 040 (37 %) | |
| BSRAM | 56 de 56 | 38 de retardo + 6 de microcódigo + 12 de captura. En el pedal final, la captura no existe: 42 + 6 = 48. |
| DSP | 2 de 28 | |
| Frecuencia | 155 MHz según nextpnr; **entre 106 y 114 MHz medidos en la placa** | margen real de al menos un 6 % sobre 100 MHz (F-11); objetivo: más del 20 % |
| Ciclos por muestra | plate 1 258, freeze 1 393, shimmer 1 601 de 2 048 | |

## Reglas de diseño que salen de los fallos

- **Ninguna salida de BSRAM va a lógica en el mismo ciclo.** Las memorias se hacen con `bsram_pipe`, que usa el registro de salida interno del bloque (F-11).
- **Ninguna aritmética de 50 bit encadenada en un ciclo.** La ALU va en dos etapas; las entradas del multiplicador salen de registros (F-10, F-11).
- **Las ROM van en lógica**, con `rom_style` en el `case`, para no caer en BSRAM `SPX9` (F-09).
- **El timing se mide en la placa** (ADR 0011): nextpnr es optimista en torno a un 30 % en el GW5A.

## Historia por fase

### Fase 02 · Primer bitstream

UART TX y un contador. Sin PLL, a 50 MHz. 207 LUT4 tras la primera segunda vuelta (F-07).

### Fase 03 · Primitivas

Se añaden los envoltorios del PLL (`pll_100`), del DSP (`mult_27x18`) y de la BSRAM inferida (`bsram_dp`), verificados en la placa (MED-06 a MED-08).

### Fase 04 · Núcleo DSP en RTL

- Secuenciador multiciclo: decodificación, ejecución con espera común y una latencia `LAT = 3`.
- Un solo multiplicador 27×36 para todo (24×18 y 24×24).
- Memoria de retardo de 42 bloques, LFO, ROM Hermite generada desde el modelo.
- Igual al modelo en 63 477 muestras (simulación). nextpnr: 140 MHz.

### Fase 05 · Núcleo verificado en la placa

- **Borrado de la memoria de retardo** al salir del reset, para empezar como el modelo.
- **UART RX** y top `hil_nucleo`: captura a velocidad real, volcado con CRC-32 a petición del PC.
- **Segmentación para el silicio** (F-11):
  - `LAT` pasa de 3 a 5;
  - BSRAM con registro de salida (`bsram_bloque`, `bsram_pipe`);
  - ALU en dos etapas;
  - la dirección del `CHO`, en tres pasos.
- El plate coincide bit a bit con el modelo **en el silicio** a 100 MHz.
- Coste: unos 13 ciclos por instrucción, frente a unos 6 en la Fase 04.

### Próximo cambio previsto (antes de la Fase 06)

Leer la instrucción siguiente mientras se ejecuta la actual, y solapar la escritura del ACC con la lectura siguiente. El shimmer ya usa el 78 % del presupuesto de ciclos.
