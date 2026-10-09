<!-- i18n: fuente=docs/scripts.md sha=baeca6d7c17e estado=al_dia -->
# 脚本与 `sofifi` 命令行工具

本指南说明 `scripts/` 中的每个脚本和 `sofifi` 命令行工具的每条命令。内容按任务组织。每个工具都说明：做什么、典型命令、需要什么、属于哪个检查门或阶段。

每个脚本的文件头或 docstring 给出全部细节。使用 argparse 的 Python 脚本和 `sofifi` 也可以用 `--help` 显示帮助。

## 开始之前

- 脚本在仓库根目录运行。`sofifi` 可在任意文件夹运行：它向上查找第一个包含 `programas/` 和 `presets/banco.toml` 的文件夹。
- 用 `make install` 创建一次环境。它把模型、检查门工具和 EDA 工具链装进 `.venv`。
- 用 `make hooks` 安装一次钩子。
- 要使用开发板，先安装 udev 规则 `scripts/udev/99-tang-primer-25k.rules`。其文件头给出命令。

几乎所有工具共用的退出码：

| 退出码 | 含义 |
|---|---|
| 0 | 正确：检查通过或任务完成。 |
| 1 | 检查失败，或开发板的结果与模型不同。 |
| 2 | 用法错误：缺少参数，或作业不存在。 |

## 1. CI 检查门

检查门位于仓库内（ADR 0001）。`scripts/ci_local.sh` 是唯一的作业列表。钩子 `scripts/hooks/pre-push` 以 `--no-soft` 调用它，自己不维护列表。

### `scripts/ci_local.sh` 的作业

下表按 `scripts/ci_local.sh` 中 `JOBS` 列表的执行顺序排列。类别名沿用脚本中的西班牙语：`dura`（硬）、`blanda`（软）、`release`（发布）。

| 作业 | 类别 | 检查内容 | 脚本或命令 |
|---|---|---|---|
| `tech-debt` | 硬 | 没有以债务标记开头的注释。 | `scripts/check_tech_debt.sh` |
| `secrets` | 硬 | 没有禁止的文件和凭据。单个文件不超过 1 MiB；演示 `.ogg` 不超过 4 MiB。 | `scripts/check_secrets_hygiene.sh` |
| `licenses` | 硬 | 每个源文件都有 SPDX 文件头。外来代码登记在 `docs/terceros.yaml`（ADR 0002）。 | `scripts/check_licenses.py` |
| `adr-gate` | 硬 | 改动 `docs/adr/sentinelas.txt` 中哨兵文件的 diff 也必须改动某个 ADR。 | `scripts/check_adr_gate.sh` |
| `docs` | 硬 | 地图文档引用的路径、`make` 目标和 ADR 都存在。还检查阶段、版本、钩子和登记表。 | `scripts/check_docs.py` |
| `i18n` | 硬 | 每份译文都存在，且其印章真实（ADR 0007）。 | `scripts/check_i18n.py` |
| `cierre` | 硬 | README 和信息图声明正确版本，截图为最新。 | `scripts/check_cierre.py` |
| `model` | 硬 | 模型的风格、格式、类型和测试。 | `ruff check`、`ruff format --check`、`mypy` 和 `pytest -n auto` |
| `rtl-lint` | 硬 | 对 `rtl/top/tops.txt` 中每个顶层以及 `rtl/comun/`、`rtl/primitivas/`、`rtl/nucleo/`、`rtl/sd/` 中每个模块做 lint。 | `verilator --lint-only -Wall -DSIMULACION` |
| `sim` | 硬 | cocotb 测试平台与模型给出相同的比特（ADR 0003）。 | `pytest sim -n 4` |
| `ratchets` | 硬 | `docs/ratchets.yaml` 中的任何度量都不比其门槛更差。 | `scripts/check_ratchets.py` |
| `shell-lint` | 软 | 对 `scripts/*.sh` 和 `scripts/hooks/*` 运行 shellcheck。 | `shellcheck` |
| `esquematicos` | 软 | `schematics/` 中每个 PDF 与其 RTL 源一致（ADR 0012）。 | `scripts/esquematicos.py --comprobar` |
| `optimizacion` | 发布 | 每个顶层都能综合并满足时序；打印提示（ADR 0010）。 | `scripts/check_optimizacion.py` |

类别：

- **硬**：失败会阻止 push。摘要显示 `ROJO`（红）。
- **软**：失败显示 `WARN`，不阻止 push。如果缺少工具，作业显示 `NO CORRIÓ`（未运行）。不要把它报告为绿色。
- **发布**：只有点名时才运行。它综合所有顶层，约需 3 分钟。

### 命令

| 任务 | 命令 |
|---|---|
| 硬作业和软作业 | `make ci` |
| 只运行硬作业（pre-push 运行的内容） | `make ci-dura` |
| 查看作业列表 | `scripts/ci_local.sh --list` |
| 只运行指定作业 | `scripts/ci_local.sh model docs` |
| 模型 | `make test` |
| RTL 仿真 | `make sim` |
| 地图文档与登记表 | `make docs` |
| PR 之前的第二轮优化 | `make optimizacion`（作业 `optimizacion` 和 `ratchets`） |

`scripts/ci_local.sh` 会在 `.ci_timing.log` 中追加一行耗时。该文件不在 git 中。

### 钩子与绕过方式

| 工具 | 作用 | 何时 |
|---|---|---|
| `scripts/install_hooks.sh` | 设置 `core.hooksPath = scripts/hooks`。 | 一次，用 `make hooks`。 |
| `scripts/hooks/pre-push` | 运行 `scripts/ci_local.sh --no-soft`。 | 每次 `git push`。 |

有名字的绕过方式。只在有理由时使用：

| 变量或选项 | 效果 |
|---|---|
| `ADR_GATE_ACK=1` | `adr-gate` 接受没有 ADR 的 diff。含义是“我检查过，没有决策改变”。 |
| `PREPUSH_SKIP=1` 或 `git push --no-verify` | 钩子不运行检查门。 |

### 单独检查

`check_*` 脚本没有选项。不带参数运行。除 `check_i18n.py --sellar` 外，它们不写文件。

| 脚本 | 典型命令 |
|---|---|
| `scripts/check_docs.py` | `.venv/bin/python scripts/check_docs.py` |
| `scripts/check_i18n.py` | `.venv/bin/python scripts/check_i18n.py` |
| `scripts/check_i18n.py --sellar` | `.venv/bin/python scripts/check_i18n.py --sellar docs/EXTENDING.en.md`（每次调用一个文件） |
| `scripts/check_cierre.py` | `.venv/bin/python scripts/check_cierre.py` |
| `scripts/check_licenses.py` | `.venv/bin/python scripts/check_licenses.py` |
| `scripts/check_ratchets.py` | `.venv/bin/python scripts/check_ratchets.py`（在 `model` 作业之后） |

## 2. 综合与开发板

开发板是 Sipeed Tang Primer 25K。EDA 工具链是开源的，位于 `.venv`：yowasp-yosys、yowasp-nextpnr-himbaechel-gowin、gowin_pack 和 openFPGALoader。顶层及其源文件的唯一列表是 `rtl/top/tops.txt`。

> **警告。** 如果某个顶层以满速率通过 UART 发送，而 PC 停止读取，BL616 桥会卡死。这时必须重新连接 USB。请限制每个新顶层的发送速率（`rtl/AGENTS.md`，`fails.md` 中的 F-02）。

| 工具 | 作用 | 典型命令 | 需要 |
|---|---|---|---|
| `scripts/fpga.sh synth` | 对一个顶层做综合、布局、布线和打包。生成 `build/<top>.fs` 和 `build/<top>_recursos.json`。 | `make synth TOP=hil_nucleo` | `.venv` |
| `scripts/fpga.sh prog` | 把比特流加载到 FPGA 的 SRAM。断电后丢失。 | `make prog TOP=hil_nucleo`（先综合） | USB 连接的开发板 |
| `scripts/informe_recursos.py` | 汇总 nextpnr 报告：使用的单元和 MHz。 | 由 `fpga.sh synth` 调用。 | nextpnr 报告 |
| `scripts/check_optimizacion.py` | 综合所有顶层，要求时序收敛，并给出 `PISTA` 提示。 | `make optimizacion` | `.venv`；不需要开发板 |
| `scripts/leer_uart.py` | 读取 FPGA 的 UART，并要求出现某段文本。 | `make uart` | 开发板；`/dev/ttyUSB1` |

`scripts/fpga.sh` 的变量：

| 变量 | 默认值 | 用途 |
|---|---|---|
| `TOP`（Makefile） | `hola_uart` | `make synth` 和 `make prog` 使用的 `rtl/top/tops.txt` 顶层。 |
| `FREQ_MHZ` | 100 | nextpnr 的时钟目标（ADR 0005）。 |
| `SEMILLAS_PNR` | `2 3 4` | 时钟不收敛时 nextpnr 尝试的种子（F-33）。 |
| `SYNTH_OPCIONES` | 空 | `synth_gowin` 的附加选项。 |
| `CST` | `rtl/top/primer25k.cst` | 引脚约束文件。 |

BL616 调试器提供两个端口：`/dev/ttyUSB0` 是 JTAG，`/dev/ttyUSB1` 是 FPGA 的 UART，波特率 115 200。

## 3. 板上测试（HIL）

比特精确模型是基准（ADR 0003）。时序在开发板上测量（ADR 0011）。这些工具加载一个顶层，通过 UART 请求一次采集，并与模型比较。

| 工具 | 作用 | 典型命令 | 退出 |
|---|---|---|---|
| `make hil` | 生成一个程序或链的 ROM，综合 `hil_programa`，加载并运行 `scripts/hil_nucleo.py`。 | `make hil HIL=marea` | 4 096 个样本全部一致时为 0 |
| `scripts/hil_nucleo.py` | 将开发板的 4 096 个样本和 CRC-32 与模型比较。使用 `--traza K0` 时，找出第一条不一致的指令。 | `.venv/bin/python scripts/hil_nucleo.py --programa plate` | 全部一致时为 0 |
| `scripts/hil_lote.py` | 对多个名字运行 `make hil`，并写入 build/hil_lote.csv。每个名字约需 4 分钟。超过 20 分钟的名字记为“TIEMPO AGOTADO”（超时）。 | `.venv/bin/python scripts/hil_lote.py --todos` | 全部一致时为 0 |
| `scripts/margen_reloj.py` | 只修改已布线设计的 PLL 分频，并在每个频率重复采集。 | `.venv/bin/python scripts/margen_reloj.py --divisores 8 7 6` | 100 MHz 始终通过时为 0 |
| `scripts/verificar_primitivas.py` | 检查原语测试顶层：`dsp`、`bsram`、`pll` 和 `fs`。 | `.venv/bin/python scripts/verificar_primitivas.py dsp` | 所有行都正确时为 0 |

每项测试加载的顶层：

| 测试 | 顶层 | 脚本 |
|---|---|---|
| 运行 `plate` 的内核 | `make prog TOP=hil_nucleo` | `scripts/hil_nucleo.py` |
| 循环录音器 | `make prog TOP=hil_looper` | `scripts/hil_nucleo.py --programa looper` |
| 任意程序或链 | `make hil HIL=NOMBRE` | `scripts/hil_nucleo.py --programa NOMBRE`（由 `make hil` 调用） |
| 时钟裕量 | `make synth TOP=hil_nucleo` 和 `make synth TOP=prueba_pll` | `scripts/margen_reloj.py`（循环录音器用 `--base hil_looper --programa looper`） |
| DSP 乘法器 | `make prog TOP=prueba_dsp` | `scripts/verificar_primitivas.py dsp` |
| BSRAM | `make prog TOP=prueba_bsram` | `scripts/verificar_primitivas.py bsram` |
| PLL | `make prog TOP=prueba_pll` | `scripts/verificar_primitivas.py pll` |
| 采样率与 UART RX | `make prog TOP=prueba_fs` | `scripts/verificar_primitivas.py fs` |
| microSD | `make prog TOP=prueba_sd` | `scripts/prueba_sd.py`（第 4 节） |

说明：

- `make hil` 接受能放进 `hil_nucleo` 存储器的程序或链：38 912 个字。`sofifi rom` 拒绝其余的。
- `scripts/margen_reloj.py` 需要 `build/<base>.pnr.json` 和 build/prueba_pll.fs。没有 build/prueba_pll.fs 时，它不操作开发板并返回退出码 2。结束时它加载 `prueba_pll`，该顶层通过 UART 发送的数据很少。
- 这些工具默认读取 `/dev/ttyUSB1`。用 `--puerto` 更改端口。

## 4. microSD

microSD 存储程序，不做音频延迟（ADR 0004）。完整步骤以及关于 `dd` 的警告见 [microsd.md](microsd.md)（仅西班牙语）。

| 工具 | 作用 | 典型命令 | 需要 |
|---|---|---|---|
| `sofifi banco` | 写入程序库镜像。不给名字时，写入所有能放下的内容。 | `.venv/bin/sofifi banco build/banco.img` | 无 |
| `sofifi banco --leer` | 检查每个槽位的 CRC 和限制，并列出槽位。 | `.venv/bin/sofifi banco --leer build/banco.img` | 无 |
| `scripts/prueba_sd.py` | 让 `prueba_sd` 加载每个槽位，并与模型比较。 | `.venv/bin/python scripts/prueba_sd.py --imagen build/banco.img` | 开发板、J6 上的 PMOD TF、已写入的卡、`/dev/ttyUSB1` |

第 08 阶段：`scripts/prueba_sd.py` 还没有用真实的卡测试过。

## 5. 文档与媒体

| 工具 | 作用 | 典型命令 | 何时 |
|---|---|---|---|
| `scripts/check_i18n.py --sellar` | 更新一份译文的印章。 | `.venv/bin/python scripts/check_i18n.py --sellar README.en.md` | 每次更新译文之后（ADR 0007）。 |
| `scripts/capturar_infografia.py` | 把信息图的各节截成 PNG，并在 `docs/img/capturas.json` 中记录其哈希。 | `.venv/bin/python scripts/capturar_infografia.py --todas` | 关闭一个阶段时（检查门 `cierre`）。 |
| `scripts/esquematicos.py` | 在 `schematics/` 中为每个 RTL 模块生成一个 PDF。 | `make esquematicos` | 修改 RTL 模块之后（ADR 0012）。 |
| `scripts/generar_demos.py` | 重新生成 `demo_examples/` 中的 Ogg 演示及其说明。 | `.venv/bin/python scripts/generar_demos.py` | 修改带演示的程序之后。 |
| `scripts/medir_presets.py` | 用模型测量每个预设的电平：饱和、超过 +6 dB 或无声时发出警告。 | `.venv/bin/python scripts/medir_presets.py plate` | 添加预设或修改程序之后。整个预设库约需 3 分钟。 |
| `sofifi catalogo` | 重新生成程序、预设和链的目录。 | `.venv/bin/sofifi catalogo` | 修改程序、预设或链之后。 |

需求：

- `scripts/capturar_infografia.py` 和 `scripts/esquematicos.py` 需要 Playwright 缓存中的 chrome-headless-shell（`~/.cache/ms-playwright`）。
- `scripts/esquematicos.py` 还需要 netlistsvg：`make esquematicos` 会先在 `herramientas/esquematicos/` 中运行 `npm install`。选项 `--comprobar` 两者都不需要。
- `scripts/generar_demos.py` 需要 `demos` 附加依赖（`make install` 会安装）。在 8 核上约需 2 分钟。只有音频改变时才重写 `.ogg`。

## 6. 模型与程序：`sofifi` 命令行工具

`sofifi` 是比特精确模型的入口。`make install` 把它装到 `.venv/bin/sofifi`。每条命令都可用 `sofifi 命令 --help` 显示帮助。

| 命令 | 作用 | 示例 | 写入 |
|---|---|---|---|
| `asm` | 汇编一个程序，并给出它在 2 048 个 RTL 周期中占用的周期数（ADR 0005）。 | `sofifi asm programas/plate.sasm build/plate` | build/plate.hex 和 build/plate.json |
| `tablas` | 重新生成 Hermite 表和 RTL 的 ROM 程序。 | `sofifi tablas` | `rtl/` 中的 `.v` 文件 |
| `catalogo` | 重新生成程序、预设和链的目录。 | `sofifi catalogo` | `docs/programas.md` 及其译文 |
| `render` | 用一个程序处理 WAV 文件。 | `sofifi render programas/plate.sasm seca.wav plate.wav --preset 'Placa corta'` | 输出 WAV |
| `presets` | 列出 `presets/banco.toml` 的预设。 | `sofifi presets plate` | 无 |
| `cadenas` | 列出各链的开销，并说明是否放得下（ADR 0013）。 | `sofifi cadenas` | 无 |
| `componer` | 把一条链写成一个程序。 | `sofifi componer "Eco y muelle" build/eco.sasm` | 输出 `.sasm` |
| `cadena` | 用一条链处理 WAV 文件。 | `sofifi cadena "Eco y muelle" seca.wav eco.wav` | 输出 WAV |
| `rom` | 为一个程序或链写出 `programa_hil` ROM。 | `sofifi rom marea build/programa_hil.v` | 输出 `.v` |
| `banco` | 写入或检查 microSD 镜像。 | `sofifi banco build/banco.img` | 镜像 |

`render` 和 `cadena` 的选项：

| 选项 | 效果 |
|---|---|
| `--pot potN=V` | 把旋钮 N 设为 V（0 到 1）。可重复。 |
| `--freeze INICIO:FIN` | 在这两个秒数之间按下脚踏开关。可重复。 |
| `--cola S` | 在末尾加 S 秒静音。 |
| `--preset NOMBRE` | 仅 `render`：从某个预设的旋钮值开始，然后应用每个 `--pot`。 |

链从 `presets/cadenas.toml` 中的旋钮位置开始。

要添加程序、RTL 模块或检查门，请阅读 [EXTENDING.zh-CN.md](EXTENDING.zh-CN.md)。

### 内核验收测试

`sim/nucleo/nucleo_test.py` 将 RTL 内核与模型比较。检查门 `sim` 使用 1 000 个样本。完整验收：

```sh
SOFIFI_MUESTRAS=4883 .venv/bin/python -m pytest sim/nucleo/nucleo_test.py
```

## 需要了解的行为

- `scripts/generar_demos.py` 接受 `--readme`、`--help` 或不带参数。其他参数返回退出码 2，不生成任何演示。
- `check_*` 脚本没有选项。带 `--help` 时打印帮助；带其他参数时返回退出码 2，且不运行。
- `scripts/informe_recursos.py` 需要 nextpnr 报告的路径。没有它时，显示用法并返回退出码 2。
- 参数不正确时，`scripts/capturar_infografia.py` 返回退出码 2。缺少 chrome-headless-shell 时，它说明安装方法并返回退出码 1。
- `scripts/ci_local.sh --help` 以及不带命令的 `scripts/fpga.sh` 会打印其文件头。
