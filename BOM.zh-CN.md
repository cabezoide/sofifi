<!-- i18n: fuente=BOM.md sha=38e7dbe6cc99 estado=al_dia -->
# BOM · SOFIFI 硬件

这是效果器的采购清单。链接检查日期为 **2026 年 10 月 7 日**：[V] = 页面已加载，商品在售；[?] = 页面无法加载。价格为该日期的价格，不含运费，价格会变动。

## 现在需要的物品（到第 08 阶段为止）

| # | 物品 | 用途 | 大约价格 | 购买渠道 |
|---|---|---|---|---|
| 1 | **Sipeed Tang Primer 25K Dock Kit**（FPGA GW5A-LV25 + 带 USB-C 调试器、3 个 PMOD 和 40 针连接器的 Dock） | 运行 DSP 核心的 FPGA。Dock 上的调试器为 FPGA 编程，同时充当 UART：不需要另外的调试器。 | 29 USD | [V] [SpotPear（Sipeed 经销商）](https://spotpear.com/shop/Sipeed-FPGA-Tang-Primer-25K-Dock-Gowin-PMOD-SDRAM-GW5A-LV25MG121-RISCV-Retro-Game-Open-Source-linux/Tang-Primer-25K-Dock-Kit.html) · [?] [AliExpress 上的 Sipeed 官方店](https://www.aliexpress.us/item/3256806038278266.html) |
| 2 | **Sipeed PMOD TF-CARD**（microSD 读卡器） | 在 microSD 中保存程序和预设（第 08 阶段）。 | — | 无经过验证的链接。官方资料：[V] [Sipeed wiki](https://wiki.sipeed.com/hardware/en/tang/tang-PMOD/FPGA_PMOD.html)。Sipeed PMOD 套件：[?] [AliExpress](https://www.aliexpress.us/item/1005006265716790.html)。搜索“Sipeed Tang PMOD TF-CARD”。 |
| 3 | **64 GB microSD**（例如 Samsung EVO Select） | 存储。可容纳数百万个程序。 | 15 USD | [V] [Samsung](https://www.samsung.com/us/computing/memory-storage/memory-cards/evo-select-adapter-microsdxc-64gb-mb-me64ka-am/)（10 月 7 日缺货）。替代品：SanDisk Ultra 64 GB。 |
| 4 | **USB-A 转 USB-C 数据线** | 将 Dock 连接到 PC。 | 5 USD | [V] [Adafruit #4474](https://www.adafruit.com/product/4474) |

## 第 09 至 11 阶段还缺少的物品

| # | 物品 | 用途 | 阶段 | 大约价格 | 购买渠道 |
|---|---|---|---|---|---|
| 5 | **Digilent Pmod I2S2**（ADC CS5343 + DAC CS4344） | 24 bit 立体声音频输入和输出。这是推荐的编解码器。 | 11 | 30 USD | [V] [DigiKey 410-379](https://www.digikey.com/en/products/detail/digilent-inc/410-379/9445907) · [?] [Digilent](https://digilent.com/shop/pmod-i2s2-stereo-audio-input-and-output) |
| 6a | **PCM1808** ADC 模块（I2S） | Pmod I2S2 的替代方案：音频输入。 | 11 | 13 USD | [V] [Newegg](https://www.newegg.com/p/2TP-005G-00609)（由第三方卖家销售：可靠性最低的链接） |
| 6b | **Adafruit PCM5102** I2S DAC | Pmod I2S2 的替代方案：音频输出。 | 11 | 5 USD | [V] [Adafruit #6250](https://www.adafruit.com/product/6250) |
| 7 | **Microchip MCP3208-CI/P**（12 bit、8 通道 SPI ADC） | 读取 6 个电位器。 | 09 | 3 USD | [V] [DigiKey](https://www.digikey.com/en/products/detail/microchip-technology/MCP3208-CI-P/305928) |
| 8 | **B10K 线性电位器** ×6 | 效果器的旋钮。 | 09 | 每个 0.39 USD | [V] [Tayda A-5523](https://www.taydaelectronics.com/tayda-b10k-ohm-linear-taper-potentiometer-round-shaft-pc-mount.html) |
| 9 | **SPST 瞬时软触脚踏开关** ×2 | Bypass 和 freeze。在此之前，可以使用 Dock 上的按键。 | 09 | 每个 3 USD | [V] [Tayda](https://www.taydaelectronics.com/spst-momentary-soft-touch-push-button-stomp-foots-pedal-switch-on-off.html) |
| 10 | **128×64 SSD1306 OLED** | 用四种语言显示预设和每个旋钮的功能。 | 10 | 20 USD | [V] [Adafruit #938](https://www.adafruit.com/product/938)（10 月 7 日缺货） |
| 11 | **输入缓冲器**（JFET 或运算放大器） | 将吉他（高阻抗）适配到 ADC 输入。任何带缓冲器的效果器都可以。 | 11 | 0.50 USD（仅 PCB） | [V] [PedalPCB Simple JFET Buffer](https://www.pedalpcb.com/product/jfetbuffer/) · [?] [PedalPCB MicroBuffer](https://www.pedalpcb.com/product/pcb678/) |

## 以后需要的物品

| # | 物品 | 用途 | 大约价格 | 购买渠道 |
|---|---|---|---|---|
| 12 | 用于 Tang Primer 25K 的 **Sipeed SDRAM 模块**（40 针） | 外部存储器：长时间 looper 和数秒的 granular 效果（第 12 阶段之后）。 | 10 USD | [V] [SpotPear“Only-SDRAM”](https://spotpear.com/shop/Sipeed-FPGA-Tang-Primer-25K-Dock-Gowin-PMOD-SDRAM-GW5A-LV25MG121-RISCV-Retro-Game-Open-Source-linux/Only-SDRAM.html)（页面未给出容量；Sipeed wiki 称为 32 MB [?]） |

## 大约总价

- 到第 08 阶段为止：**约 50 USD**（开发板、microSD、数据线；PMOD 读卡器价格未确认）。
- 使用 Pmod I2S2 的完整效果器：**约 125 USD**，另加外壳、插孔和电源。这些尚未列入清单（将与 PCB 一起规划）。

第 12 阶段及以后的电路板（PCB、外壳、插孔、电源）不在此清单中：将与模拟前端一起设计。
