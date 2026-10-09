# BOM · Hardware de SOFIFI

Lista de compra del pedal. Los enlaces se comprobaron el **7 de octubre de 2026**: [V] = página cargada y artículo a la venta; [?] = no se pudo cargar. Los precios son los de esa fecha, sin envío, y cambian.

## Lo que ya hace falta (hasta la Fase 08)

| # | Artículo | Para qué sirve | Precio aprox. | Dónde comprarlo |
|---|---|---|---|---|
| 1 | **Sipeed Tang Primer 25K Dock Kit** (FPGA GW5A-LV25 + Dock con depurador USB-C, 3 PMOD y conector de 40 pines) | La FPGA que ejecuta el núcleo DSP. El depurador de la Dock programa la FPGA y hace de UART: no hace falta otro. | 29 USD | [V] [SpotPear (distribuidor de Sipeed)](https://spotpear.com/shop/Sipeed-FPGA-Tang-Primer-25K-Dock-Gowin-PMOD-SDRAM-GW5A-LV25MG121-RISCV-Retro-Game-Open-Source-linux/Tang-Primer-25K-Dock-Kit.html) · [?] [tienda oficial de Sipeed en AliExpress](https://www.aliexpress.us/item/3256806038278266.html) |
| 2 | **Sipeed PMOD TF-CARD** (lector de microSD) | Lee la microSD en modo SPI (Fase 08). Va en el conector J6 del Dock. El top de prueba reconoce sus dos revisiones. | — | Sin enlace verificado. Ficha oficial: [V] [wiki de Sipeed](https://wiki.sipeed.com/hardware/en/tang/tang-PMOD/FPGA_PMOD.html). Kit de PMOD de Sipeed: [?] [AliExpress](https://www.aliexpress.us/item/1005006265716790.html). Buscar «Sipeed Tang PMOD TF-CARD». |
| 3 | **microSD de 64 GB** (por ejemplo, Samsung EVO Select) | Guarda el banco de programas. El banco usa como máximo unos 14 MB (1 024 programas). Debe ser una SDHC o SDXC: las tarjetas de la versión 1 no funcionan. | 15 USD | [V] [Samsung](https://www.samsung.com/us/computing/memory-storage/memory-cards/evo-select-adapter-microsdxc-64gb-mb-me64ka-am/) (agotado el 7 de octubre). Alternativa: SanDisk Ultra 64 GB. |
| 4 | **Cable USB-A a USB-C con datos** | Conecta la Dock al PC. | 5 USD | [V] [Adafruit #4474](https://www.adafruit.com/product/4474) |

## Lo que falta para las fases 09 a 11

| # | Artículo | Para qué sirve | Fase | Precio aprox. | Dónde comprarlo |
|---|---|---|---|---|---|
| 5 | **Digilent Pmod I2S2** (ADC CS5343 + DAC CS4344) | Entrada y salida de audio estéreo de 24 bit. Es el códec recomendado. | 11 | 30 USD | [V] [DigiKey 410-379](https://www.digikey.com/en/products/detail/digilent-inc/410-379/9445907) · [?] [Digilent](https://digilent.com/shop/pmod-i2s2-stereo-audio-input-and-output) |
| 6a | Módulo ADC **PCM1808** (I2S) | Alternativa al Pmod I2S2: la entrada de audio. | 11 | 13 USD | [V] [Newegg](https://www.newegg.com/p/2TP-005G-00609) (lo vende un tercero: el enlace menos fiable) |
| 6b | **Adafruit PCM5102** I2S DAC | Alternativa al Pmod I2S2: la salida de audio. | 11 | 5 USD | [V] [Adafruit #6250](https://www.adafruit.com/product/6250) |
| 7 | **Microchip MCP3208-CI/P** (ADC SPI de 12 bit y 8 canales) | Lee los 6 potenciómetros. | 09 | 3 USD | [V] [DigiKey](https://www.digikey.com/en/products/detail/microchip-technology/MCP3208-CI-P/305928) |
| 8 | **Potenciómetro lineal B10K** ×6 | Las perillas del pedal. | 09 | 0,39 USD c/u | [V] [Tayda A-5523](https://www.taydaelectronics.com/tayda-b10k-ohm-linear-taper-potentiometer-round-shaft-pc-mount.html) |
| 9 | **Footswitch SPST momentáneo**, de pulsación suave ×2 | Bypass y freeze. Hasta entonces sirven los botones de la Dock. | 09 | 3 USD c/u | [V] [Tayda](https://www.taydaelectronics.com/spst-momentary-soft-touch-push-button-stomp-foots-pedal-switch-on-off.html) |
| 10 | **OLED SSD1306 de 128×64** | Muestra el preset y la función de cada perilla, en cuatro idiomas. | 10 | 20 USD | [V] [Adafruit #938](https://www.adafruit.com/product/938) (agotado el 7 de octubre) |
| 11 | **Buffer de entrada** (JFET o amplificador operacional) | Adapta la guitarra (alta impedancia) a la entrada del ADC. Sirve cualquier pedal con buffer. | 11 | 0,50 USD (solo PCB) | [V] [PedalPCB Simple JFET Buffer](https://www.pedalpcb.com/product/jfetbuffer/) · [?] [PedalPCB MicroBuffer](https://www.pedalpcb.com/product/pcb678/) |

## Para más adelante

| # | Artículo | Para qué sirve | Precio aprox. | Dónde comprarlo |
|---|---|---|---|---|
| 12 | **Módulo SDRAM de Sipeed** para la Tang Primer 25K (40 pines) | Memoria externa: looper largo y granular de varios segundos (después de la Fase 12). | 10 USD | [V] [SpotPear «Only-SDRAM»](https://spotpear.com/shop/Sipeed-FPGA-Tang-Primer-25K-Dock-Gowin-PMOD-SDRAM-GW5A-LV25MG121-RISCV-Retro-Game-Open-Source-linux/Only-SDRAM.html) (la página no da la capacidad; la wiki de Sipeed dice 32 MB [?]) |

## Total aproximado

- Hasta la Fase 08: **unos 50 USD** (placa, microSD, cable; el lector PMOD sin precio confirmado).
- Pedal completo con el Pmod I2S2: **unos 125 USD** más caja, jacks y alimentación, que aún no están en la lista (se planificarán con el PCB).

La placa de la Fase 12 en adelante (PCB, caja, jacks, alimentación) no está en esta lista: se diseñará con el front-end analógico.
