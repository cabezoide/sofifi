<!-- i18n: fuente=BOM.md sha=38e7dbe6cc99 estado=al_dia -->
# BOM · SOFIFI hardware

This is the shopping list for the pedal. We checked the links on **7 October 2026**: [V] = the page loaded and the item was for sale; [?] = the page did not load. The prices are from that date, without shipping, and they change.

## What you need now (up to Phase 08)

| # | Item | Function | Approx. price | Where to buy |
|---|---|---|---|---|
| 1 | **Sipeed Tang Primer 25K Dock Kit** (FPGA GW5A-LV25 + Dock with USB-C debugger, 3 PMOD and 40-pin connector) | The FPGA that runs the DSP core. The Dock debugger programs the FPGA and is also the UART: you do not need a different one. | 29 USD | [V] [SpotPear (Sipeed distributor)](https://spotpear.com/shop/Sipeed-FPGA-Tang-Primer-25K-Dock-Gowin-PMOD-SDRAM-GW5A-LV25MG121-RISCV-Retro-Game-Open-Source-linux/Tang-Primer-25K-Dock-Kit.html) · [?] [official Sipeed store on AliExpress](https://www.aliexpress.us/item/3256806038278266.html) |
| 2 | **Sipeed PMOD TF-CARD** (microSD reader) | Keeps the programs and presets on the microSD (Phase 08). | — | No verified link. Official datasheet: [V] [Sipeed wiki](https://wiki.sipeed.com/hardware/en/tang/tang-PMOD/FPGA_PMOD.html). Sipeed PMOD kit: [?] [AliExpress](https://www.aliexpress.us/item/1005006265716790.html). Search for "Sipeed Tang PMOD TF-CARD". |
| 3 | **64 GB microSD** (for example, Samsung EVO Select) | Storage. It holds millions of programs. | 15 USD | [V] [Samsung](https://www.samsung.com/us/computing/memory-storage/memory-cards/evo-select-adapter-microsdxc-64gb-mb-me64ka-am/) (sold out on 7 October). Alternative: SanDisk Ultra 64 GB. |
| 4 | **USB-A to USB-C data cable** | Connects the Dock to the PC. | 5 USD | [V] [Adafruit #4474](https://www.adafruit.com/product/4474) |

## What is missing for phases 09 to 11

| # | Item | Function | Phase | Approx. price | Where to buy |
|---|---|---|---|---|---|
| 5 | **Digilent Pmod I2S2** (ADC CS5343 + DAC CS4344) | 24-bit stereo audio input and output. This is the recommended codec. | 11 | 30 USD | [V] [DigiKey 410-379](https://www.digikey.com/en/products/detail/digilent-inc/410-379/9445907) · [?] [Digilent](https://digilent.com/shop/pmod-i2s2-stereo-audio-input-and-output) |
| 6a | **PCM1808** ADC module (I2S) | Alternative to the Pmod I2S2: the audio input. | 11 | 13 USD | [V] [Newegg](https://www.newegg.com/p/2TP-005G-00609) (a third party sells it: the least reliable link) |
| 6b | **Adafruit PCM5102** I2S DAC | Alternative to the Pmod I2S2: the audio output. | 11 | 5 USD | [V] [Adafruit #6250](https://www.adafruit.com/product/6250) |
| 7 | **Microchip MCP3208-CI/P** (12-bit, 8-channel SPI ADC) | Reads the 6 potentiometers. | 09 | 3 USD | [V] [DigiKey](https://www.digikey.com/en/products/detail/microchip-technology/MCP3208-CI-P/305928) |
| 8 | **B10K linear potentiometer** ×6 | The knobs of the pedal. | 09 | 0.39 USD each | [V] [Tayda A-5523](https://www.taydaelectronics.com/tayda-b10k-ohm-linear-taper-potentiometer-round-shaft-pc-mount.html) |
| 9 | **SPST momentary soft-touch footswitch** ×2 | Bypass and freeze. Until then, use the buttons on the Dock. | 09 | 3 USD each | [V] [Tayda](https://www.taydaelectronics.com/spst-momentary-soft-touch-push-button-stomp-foots-pedal-switch-on-off.html) |
| 10 | **128×64 SSD1306 OLED** | Shows the preset and the function of each knob, in four languages. | 10 | 20 USD | [V] [Adafruit #938](https://www.adafruit.com/product/938) (sold out on 7 October) |
| 11 | **Input buffer** (JFET or operational amplifier) | Adapts the guitar (high impedance) to the ADC input. Any pedal with a buffer is satisfactory. | 11 | 0.50 USD (PCB only) | [V] [PedalPCB Simple JFET Buffer](https://www.pedalpcb.com/product/jfetbuffer/) · [?] [PedalPCB MicroBuffer](https://www.pedalpcb.com/product/pcb678/) |

## For later

| # | Item | Function | Approx. price | Where to buy |
|---|---|---|---|---|
| 12 | **Sipeed SDRAM module** for the Tang Primer 25K (40-pin) | External memory: long looper and granular effects of several seconds (after Phase 12). | 10 USD | [V] [SpotPear "Only-SDRAM"](https://spotpear.com/shop/Sipeed-FPGA-Tang-Primer-25K-Dock-Gowin-PMOD-SDRAM-GW5A-LV25MG121-RISCV-Retro-Game-Open-Source-linux/Only-SDRAM.html) (the page does not give the capacity; the Sipeed wiki says 32 MB [?]) |

## Approximate total

- Up to Phase 08: **approximately 50 USD** (board, microSD, cable; the PMOD reader has no confirmed price).
- Full pedal with the Pmod I2S2: **approximately 125 USD**, plus enclosure, jacks and power supply. These are not on the list yet (we will plan them with the PCB).

The board for Phase 12 and later (PCB, enclosure, jacks, power supply) is not on this list: we will design it with the analog front end.
