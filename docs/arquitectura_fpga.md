# Arquitectura del FPGA

Qué hay dentro de la FPGA, cómo se conecta y cómo ha cambiado fase a fase. Se actualiza al cerrar cada fase y en cada PR que cambie bloques del FPGA. La explicación sencilla de cada componente está en `SBOM.md`; los fallos que dieron forma al diseño, en `fails.md`.

Chip: **Gowin GW5A-LV25** (Tang Primer 25K): 23 040 LUT4, 56 bloques de BSRAM de 18 Kbit, 28 bloques DSP, 6 PLL.

## Vista general (Fase 06, requisito previo)

```mermaid
flowchart LR
    cristal["Cristal 50 MHz"] --> pll["PLL → 100 MHz<br/>(reloj de todo)"]
    rom["ROM del programa"] --> cargador["Cargador"] --> mc["Microcódigo<br/>2 048 × 54 · BSRAM"]
    gen["Generador de muestra<br/>tick cada 2 048 ciclos"] --> sec

    subgraph nucleo["Núcleo DSP"]
        direction LR
        mc --> sec["Secuenciador<br/>lectura adelantada"] --> deco["Decodificación"]
        deco --> regs["Banco de registros<br/>64 × 24"]
        deco --> lfo["LFO ×4 · ROM Hermite<br/>curva suave"]
        regs --> mult["Multiplicador 27×36<br/>2 DSP"]
        lfo --> mult
        mem["Memoria de retardo<br/>38–42 BSRAM, por grupos"] --> mult
        mult --> alu["ALU<br/>2 etapas"] --> acc["ACC 48 bit"]
        acc --> regs
        acc --> mem
    end

    entradas["Entradas<br/>adc, pots, sw"] --> regs
    regs --> dac["dac_l, dac_r"]

    subgraph pruebas["Solo en el top de pruebas (HIL)"]
        direction LR
        rx["UART RX<br/>órdenes C y T"] --> cap["Captura · BSRAM<br/>muestras o traza"]
        cap --> crc["Volcado + CRC-32"] --> tx["UART TX"]
    end

    dac --> cap
    acc -. traza .-> cap
    tx --> pc["PC"]
```

Todo corre en **un solo dominio de reloj de 100 MHz** (ADR 0005). La única excepción es el medidor de frecuencia de las pruebas, que cruza al dominio del cristal en código Gray.

## Bloques

| Bloque | Fichero | Recursos | Latencia |
|---|---|---|---|
| PLL 50 → 100 MHz | `rtl/primitivas/pll_100.v` | 1 PLLA | — |
| Generador de muestra | `rtl/comun/generador_muestra.v` | ~20 LUT | 1 tick / 2 048 ciclos |
| Secuenciador del núcleo | `rtl/nucleo/nucleo.v` | la mayor parte de la lógica | ~14 ciclos por instrucción; lee la siguiente mientras ejecuta la actual |
| Microcódigo | `bsram_pipe` 2 048 × 54 + un registro | 6 BSRAM | 4 ciclos; sin salto, ya está leída |
| Banco de registros | dentro de `nucleo.v` | 64 × 24 en flip-flops + 8 candidatos | 2 niveles: candidatos en `E_LEER`, elección en `E_DECO` |
| Multiplicador | `rtl/primitivas/mult_27x36.v` (con `PREG`) + 1 registro | 2 DSP | 5 ciclos (`LAT`) |
| ALU | `rtl/nucleo/alu.v` | ~1 000 LUT y 300 ALU | 2 etapas + escritura |
| Memoria de retardo | `rtl/nucleo/memoria_retardo.v` + `bsram_pipe` segmentada | 1 BSRAM por cada 1 024 palabras; ~1 700 flip-flops de copias | 9 ciclos (`LAT_MEM`), solo en `RDA` y `CHO` |
| Copias de un registro | `rtl/primitivas/registro_copia.v` | flip-flops `DFF` con `keep` | 1 ciclo |
| LFO ×4 | `rtl/nucleo/lfo_banco.v` | ~380 LUT y 377 ALU | 26 ciclos por muestra |
| ROM Hermite | `rtl/nucleo/tabla_hermite.v` (generada) | ~820 LUT | combinacional + registro |
| Curva suave | `rtl/nucleo/curva_fin.v` | una resta y una saturación | registrada |
| UART TX / RX | `rtl/comun/uart_tx.v`, `uart_rx.v` | ~50 LUT cada una | 115 200 baudios |
| Cargador de programa | `rtl/comun/carga_programa.v` | ~30 LUT | instrucciones + 1 ciclos |
| Traza del núcleo (solo HIL) | `rtl/top/hil_nucleo.v`, orden `T` | ~150 flip-flops | graba (pc, ACC) en la captura |

## Presupuesto (top `hil_nucleo`, Fase 06, requisito previo)

| Recurso | Uso | Notas |
|---|---|---|
| LUT4 | 11 490 de 23 040 (50 %) | Según nextpnr, con las LUT de paso de los flip-flops. Lógica real según Yosys: unas 7 900. |
| Flip-flops | 6 523 de 23 040 (28 %) | Unos 3 100 son copias y registros de segmentación (F-15). |
| BSRAM | 56 de 56 | 38 de retardo + 6 de microcódigo + 12 de captura. En el pedal final, la captura no existe: 42 + 6 = 48. |
| DSP | 2 de 28 | |
| Frecuencia | 154 MHz según nextpnr; **120 MHz en la placa sin errores (4 de 4)**; 125 MHz, 3 de 4 | margen real de al menos un 20 % sobre 100 MHz (F-15, ADR 0011) |
| Ciclos por muestra | reverse 431, lofi 620, cinta 658, plate 1 195, freeze 1 313, cloud 1 356, swell 1 467, shimmer 1 514, hall 1 578 de 2 048 | coste de cada instrucción en `model/sofifi/domain/coste.py` |

## Reglas de diseño que salen de los fallos

- **Ninguna salida de BSRAM va a lógica en el mismo ciclo.** Las memorias se hacen con `bsram_pipe`, que usa el registro de salida interno del bloque (F-11).
- **Ninguna aritmética de 50 bit encadenada en un ciclo.** La ALU va en dos etapas; las entradas del multiplicador salen de registros (F-10, F-11).
- **Ningún registro alimenta bloques de todo el chip.** Las memorias grandes van segmentadas: copias de la dirección por grupo y por bloque, y salida registrada junto a cada bloque (F-15).
- **Ningún multiplexor ancho en un ciclo.** El banco de registros (64:1) va en dos niveles (F-15).
- **Sumas en paralelo antes que en serie.** Si una corrección depende de un signo, se calculan todas las opciones y el signo elige (F-15).
- **Las ROM van en lógica**, con `rom_style` en el `case`, para no caer en BSRAM `SPX9` (F-09).
- **El timing se mide en la placa** (ADR 0011): nextpnr es optimista en un factor de 1,45 a 1,5 en el GW5A. Para el 20 % de margen hace falta que nextpnr dé unos 150 MHz o más, y medirlo. Si falla, `margen_reloj.py --traza` dice qué instrucción.

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

### Fase 06 · Requisito previo: lectura adelantada y margen del 20 %

- **Lectura adelantada:** al decodificar una instrucción se pide la siguiente al microcódigo. Si no hay salto, ya está leída cuando hace falta.
- **Segmentación para el silicio** (F-15):
  - memoria de retardo segmentada en grupos de 8 bloques, con copias locales de la dirección (`registro_copia`) y salidas registradas; la lectura tarda 9 ciclos (`LAT_MEM`);
  - banco de registros en dos niveles;
  - dirección física con tres sumas en paralelo;
  - `PREG` dentro del DSP.
- **Traza del núcleo en la placa:** el top HIL graba (pc, ACC) y el PC dice qué instrucción falla primero.
- Margen medido: **120 MHz sin errores**, frente a 106 MHz en la Fase 05.
- Ciclos por muestra: shimmer 1 514 (antes 1 601). La lectura adelantada ahorra unos 150 ciclos y la memoria segmentada gasta unos 65.

### Fase 06 · Biblioteca de programas (el RTL no cambia)

- Seis programas nuevos, iguales al modelo en la simulación: hall, cloud, reverse, lofi y swell en 4 883 muestras; cinta en 12 000, para llegar a su primer eco.
- **Cuantizar sin AND:** el lo-fi escala la muestra hacia abajo, la redondea al escribirla en un registro (`WRAX`) y la vuelve a escalar con `SOF`.
- **Retardo variable sin instrucción nueva:** la cinta para un LFO senoidal en un cuarto de vuelta. Su forma vale 1 y el retardo del `CHO` sigue a `lfo0_depth`, que escribe el programa.
- **Coste de cada instrucción en el RTL**, medido en simulación y copiado al modelo (`coste.py`):

| Instrucción | Ciclos |
|---|---|
| `NOP`, `LDAX`, `CLR`, `ABSA`; `SKP` que no salta | 6 |
| `SKP` que salta | 8 |
| `RDAX`, `WRAX`, `WRA`, `WRAP`, `MAXX`, `MULX`, `SOF` | 10 |
| `RDFX` | 11 |
| `CLIP` | 14 |
| `RDA` | 19 |
| `CHO` (con `na`: 57) | 52 |
| Fijos por muestra (cota) | 34 |

- Un programa cabe si la suma es de 2 048 o menos. `sofifi asm` la da y `programas_test.py` la exige.
- **El cloud usa 42 814 palabras: no cabe en `hil_nucleo`**, que tiene 38 bloques de retardo para dejar sitio a la captura. Para probarlo en la placa hace falta reducir la captura.

### Próximo cambio previsto

Hoy cada instrucción espera a su resultado (unos 14 ciclos). La siguiente palanca es no esperar cuando la instrucción siguiente no usa el ACC ni el registro que se escribe. Hay que detectar las dependencias entre instrucciones. El resultado sigue igual al modelo; el cambio es grande y se decidirá en un ADR.
