<!-- i18n: fuente=README.md sha=60b9652e1d30 estado=al_dia -->
# SOFIFI — 集成 FPGA 上的沉浸式波形与滤波合成器

*英文名：Soundscapes On FPGA: Integrated Filters & Impulses；西班牙文名：Sintetizador de Ondas y Filtros Inmersivos en FPGA Integrada。*

**语言：** [Español](README.md)（源文本） · [English](README.en.md) · 简体中文

SOFIFI 是一款氛围（ambient）吉他效果器（混响、shimmer、磁带延迟、冻结、颗粒合成），
基于 **Sipeed Tang Primer 25K** FPGA（高云 GW5A-LV25）实现。

**版本：** `0.1`（版本号即最后一个已关闭的阶段；见 `docs/fases/estado_fases.csv`）。

> 状态：**逐位精确参考模型已完成**（阶段 01）。现在已可在电脑上试听 plate、
> shimmer 和 freeze 程序。尚无 RTL。初始调研见
> `docs/investigacion/INVESTIGACION.md`（西班牙语）。

## 试听效果（无需硬件）

```bash
.venv/bin/sofifi render programas/plate.sasm guitar.wav out/plate.wav --pot pot0=0.6 --pot pot2=0.4 --cola 4
.venv/bin/sofifi render programas/shimmer.sasm guitar.wav out/shimmer.wav --pot pot0=0.7 --pot pot2=0.5 --pot pot3=0.6 --cola 6
.venv/bin/sofifi render programas/freeze.sasm guitar.wav out/freeze.wav --pot pot2=0.5 --freeze 1.5:8 --cola 8
```

| 程序 | pot0 | pot1 | pot2 | pot3 | 脚踏开关 |
|---|---|---|---|---|---|
| `programas/plate.sasm` | 衰减 | 阻尼 | 干湿比 | — | — |
| `programas/shimmer.sasm` | 衰减 | 阻尼 | 干湿比 | shimmer 量 | — |
| `programas/freeze.sasm` | 衰减 | 阻尼 | 干湿比 | — | `--freeze 开始:结束`（秒） |

`demo_examples/` 中有预先渲染好的演示：一段合成吉他（Em9 琶音）分别经过
三个程序处理。可用 `scripts/generar_demos.py` 重新生成。

输入 WAV 可以是 16、24 或 32 位、任意采样率，会被重采样到 48,828 Hz。
`sofifi asm` 生成微码（`.hex` + `.json`）。（`--cola` 为尾音时长，单位秒。）

## 将要构建的内容

- **微码 DSP 内核**，风格仿照 Spin FV-1 并加以扩展：每个采样 2,048 条指令、
  48 位累加器和三次插值（ADR 0006）。效果是*程序*，而不是 RTL 模块。
- **所有音频都在 BSRAM 中**（约 0.9–1.4 秒的延迟线）。microSD 用于存储预设和
  录音，但不能用作延迟存储器（ADR 0004）。
- **fs = 48,828 Hz**，系统时钟 100 MHz：每个采样恰好 2,048 个时钟周期（ADR 0005）。
- **Python 编写的逐位精确（bit-exact）参考模型**，作为验证 RTL 的基准（ADR 0003）。

## 快速开始

```bash
make install    # 创建 .venv，包含模型和检查门所需工具
make hooks      # 安装版本化的 pre-push 钩子
make ci         # 完整的本地检查门
```

工作规范见 `docs/SPEC_RAIZ.md`；冷启动导览见 `AGENTS.md`（均为西班牙语）。

### 可选工具（软检查门）

- `verilator`：RTL 静态检查。
- `shellcheck`：脚本静态检查。
- Gowin EDA 教育版（≥ 1.9.9Beta-4）或 Yosys + nextpnr-himbaechel + apicula：
  综合。将成为发布检查门。

如果缺少某个工具，检查门会明确提示（`WARN … NO CORRIÓ`），而不会假装通过。

## 硬件

| 部件 | 状态 |
|---|---|
| Tang Primer 25K + Dock 底板 | 已有 |
| 64 GB microSD（PMOD TF） | 已有 |
| I2S 音频编解码器（PCM1808 + PCM5102A 或 Digilent Pmod I2S2） | **缺少** |
| 吉他输入缓冲 | 缺少（临时方案：任意带缓冲的效果器） |
| Sipeed SDRAM 模块 | 未来（可实现长循环录音和长颗粒合成） |

## 语言

西班牙语为规范源文本。译文带有所翻译版本的指纹印记，`scripts/check_i18n.py`
会阻止译文在已过时的情况下声称是最新的（ADR 0007）。ADR、阶段规格和代理导览
仅提供西班牙语版本。

## 许可证

MIT（见 `LICENSE`）。只移植采用宽松许可证的第三方代码，且每个来源都在
`docs/terceros.yaml` 中声明（ADR 0002）。
