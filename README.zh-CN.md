<!-- i18n: fuente=README.md sha=b581423fa49d estado=al_dia -->
# SOFIFI — 集成 FPGA 上的沉浸式波形与滤波合成器

*英文名：Soundscapes On FPGA: Integrated Filters & Impulses；西班牙文名：Sintetizador de Ondas y Filtros Inmersivos en FPGA Integrada。*

**语言：** [Español](README.md)（源文本） · [English](README.en.md) · 简体中文

![SOFIFI：标志与效果器面板，含 OLED、六个旋钮和两个脚踏开关](docs/img/portada.png)

*图片为西班牙语，即本项目的源语言。*

SOFIFI 是一款氛围（ambient）吉他效果器（混响、shimmer、磁带延迟、冻结、颗粒合成），
基于 **Sipeed Tang Primer 25K** FPGA（高云 GW5A-LV25）实现。

**版本：** `0.6`（版本号即最后一个已关闭的阶段；见 `docs/fases/estado_fases.csv`）。

> 状态：**43 个程序与 344 个预设组成的程序库**（阶段 06）：混响、延迟、调制、
> 音高、动态、滤波和质感。43 个程序在 RTL 中的输出都与逐位精确模型一致（仿真）。
> 在开发板上以 100 MHz 运行时，plate 已经验证（阶段 05）。下一步：微型循环器与
> 颗粒引擎（阶段 07）。目前还不能接吉他演奏：缺少音频编解码器（阶段 11）。

## 试听效果（无需硬件）

1. 试听 `demo_examples/` 中的演示：一段合成吉他（Em9 琶音）经过每个程序，格式为 Ogg Vorbis。
2. 用预设处理自己的 WAV：

```bash
.venv/bin/sofifi presets hall                      # 列出一个程序的预设
.venv/bin/sofifi render programas/hall.sasm guitar.wav out/hall.wav --preset "Catedral" --cola 6
.venv/bin/sofifi render programas/shimmer.sasm guitar.wav out/sh.wav --pot pot0=0.7 --pot pot3=0.6 --cola 6
.venv/bin/sofifi render programas/freeze.sasm guitar.wav out/fz.wav --preset "Congelar suave" --freeze 1.5:8 --cola 8
```

| 类别 | 程序 |
|---|---|
| 混响 | plate, plate_vivo, hall, blackhole, cloud, bloom, spring, chorale, resonador, gated, reverb_inversa, infinite, freeze, freeze_givens, shimmer, shimmer_quinta, shimmer_energia |
| 延迟 | delay, cinta, bbd, pingpong, lluvia, ducking, reverse |
| 调制 | chorus, flanger, phaser, tremolo, vibrato, slicer |
| 音高 | octava, armonizador, doblador, escalera |
| 动态 | compresor, puerta, swell |
| 滤波 | autowah, filtro, ancho |
| 质感 | saturacion, lofi, ringmod |

每个程序的作用、旋钮和开销见 `docs/programas.md`（西班牙语，由 `sofifi catalogo` 生成）。
预设位于 `presets/banco.toml`，名称为西班牙语。

输入 WAV 可以是 16、24 或 32 位、任意采样率，会被重采样到 48,828 Hz。
`sofifi asm` 生成微码（`.hex` + `.json`），并给出它在 RTL 中使用的周期数。（`--cola` 为尾音时长，单位秒。）

## 将要构建的内容

- **微码 DSP 内核**，风格仿照 Spin FV-1 并加以扩展：每个采样 2,048 条指令、
  48 位累加器和三次插值（ADR 0006）。效果是*程序*，而不是 RTL 模块。
- **所有音频都在 BSRAM 中**（约 0.9–1.4 秒的延迟线）。microSD 用于存储预设和
  录音，但不能用作延迟存储器（ADR 0004）。
- **fs = 48,828 Hz**，系统时钟 100 MHz：每个采样恰好 2,048 个时钟周期（ADR 0005）。
- **Python 编写的逐位精确（bit-exact）参考模型**，作为验证 RTL 的基准（ADR 0003）。

![为什么选择 SOFIFI？可以阅读、修改并逐位验证；与 FV-1 相比，指令数和采样率更高，但目前还不能接吉他演奏](docs/img/porque.png)

2026 年技术现状与路线图见 `docs/investigacion/ESTADO_DEL_ARTE_2026.md`（西班牙语）。
完整信息图见 `docs/infografias/`。

## 快速开始

```bash
make install    # 创建 .venv，包含模型和检查门所需工具
make hooks      # 安装版本化的 pre-push 钩子
make ci         # 完整的本地检查门
```

工作规范见 `docs/SPEC_RAIZ.md`；冷启动导览见 `AGENTS.md`（均为西班牙语）。

### EDA 工具链（第 02 阶段）

`make install` 通过 pip 安装整条开源工具链：Yosys 与
nextpnr-himbaechel-gowin（YoWASP）、apicula、openFPGALoader、verilator 和 cocotb。

```bash
make sim        # RTL 的 cocotb 测试平台
make prog       # 综合 hola_uart 并加载到 Tang Primer 25K 的 SRAM
make uart       # 读取调试器 UART（/dev/ttyUSB1），要求收到 "SOFIFI"
```

无需 sudo 编程需要为 BL616 调试器（`0403:6010`，`plugdev` 组）安装 udev 规则；
按 `scripts/udev/99-tang-primer-25k.rules` 中的说明安装一次即可。

### 可选工具（软检查门）

- `shellcheck`：脚本静态检查。

如果缺少某个工具，检查门会明确提示（`WARN … NO CORRIÓ`），而不会假装通过。

## 硬件

| 部件 | 状态 |
|---|---|
| Tang Primer 25K + Dock 底板 | 已有 |
| 64 GB microSD（PMOD TF） | 已有 |
| I2S 音频编解码器（PCM1808 + PCM5102A 或 Digilent Pmod I2S2） | **缺少**（阶段 11） |
| MCP3208 + 电位器 | 缺少（阶段 09；Dock 底板按键充当脚踏开关） |
| 128×64 SSD1306 OLED | 缺少（阶段 10） |
| 吉他输入缓冲 | 缺少（临时方案：任意带缓冲的效果器） |
| Sipeed SDRAM 模块 | 未来（可实现长循环录音和长颗粒合成） |

需要缺少硬件的阶段排在计划末尾（09 至 12），因此在阶段 08 之前只需开发板和 microSD。

![13 个阶段：7 个已关闭、下一个阶段以及等待硬件的阶段](docs/img/ruta.png)

## 硬件文档（西班牙语）

- `BOM.md`：硬件采购清单，附购买链接。
- `SBOM.md`：FPGA 中每个组件的作用，以及构建所用的工具。
- `docs/arquitectura_fpga.md`：FPGA 架构及其在各阶段的变化。
- `fails.md`：遇到的故障及其解决方法。
- `schematics/`：每个 RTL 模块的 PDF 原理图，由 Verilog 生成。

## 语言

西班牙语为规范源文本。译文带有所翻译版本的指纹印记，`scripts/check_i18n.py`
会阻止译文在已过时的情况下声称是最新的（ADR 0007）。ADR、阶段规格和代理导览
仅提供西班牙语版本。

## 许可证

MIT（见 `LICENSE`）。只移植采用宽松许可证的第三方代码，且每个来源都在
`docs/terceros.yaml` 中声明（ADR 0002）。
