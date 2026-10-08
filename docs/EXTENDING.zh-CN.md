<!-- i18n: fuente=docs/EXTENDING.md sha=3b5545c20179 estado=al_dia -->
# 如何扩展

本文按部件类型逐步说明。如果添加某样东西需要改动本清单之外的位置，说明清单不完整：在同一个 PR 中修正。

## 一个效果（核心程序）

效果是程序，不是 RTL 模块（ADR 0006（西班牙语））。

1. 如果来自第三方，在 `docs/terceros.yaml` 中添加条目。只有许可证为宽松许可证时，才可使用 `uso: portado`（ADR 0002（西班牙语））。
2. 编写 `programas/<nombre>.sasm`。文件头包含 `; familia:`、
   `; resumen:`，以及每个旋钮一行 `; potN = nombre`。已有的模块用 `include` 从 `programas/comun/` 引入。
3. 检查程序是否放得下：`sofifi asm` 给出 RTL 周期数，必须不超过 2,048（`model/sofifi/domain/coste.py`）。
4. 在其所属系列的文件（`model/tests/programas_<familia>_test.py`）中编写其声学特性的测试。通用测量位于 `model/tests/acustica.py`。
5. 在 `HUELLAS`（`model/tests/programas_test.py`）中添加其指纹。“放得下”、指纹以及与 RTL 一致性（`sim/nucleo/nucleo_test.py`）的测试会遍历所有 `.sasm`：缺少任何内容都会失败。
6. 在 `presets/banco.toml` 中添加至少 5 个预设，放在以程序名命名的表中。`model/tests/presets_test.py` 检查旋钮。
7. 用 `sofifi catalogo` 重新生成目录。
8. 在 `DEMOS`（`scripts/generar_demos.py`）和 `demo_examples/README.zh-CN.md` 中添加演示。

## 一条链（两个程序合为一个）

链把已有的程序连在一起，不需要 RTL（ADR 0013，西班牙语）。

1. 用 `sofifi cadenas` 查看类似的链用了多少资源。每个程序使用自己的寄存器和 LFO；核心有 32 个寄存器和 4 个 LFO。
2. 在 `presets/cadenas.toml` 中添加一个 `[[cadena]]`。在 `mandos` 中，数字是固定值，`"potN"` 是踏板的第 N 个电位器。`pots` 给出加载链时六个电位器的位置。
3. 如果只缺存储器，设置 `requiere = "sdram"`。`model/tests/cadenas_test.py` 要求每条链都能装入，或者只缺存储器。
4. 用 `sofifi cadena 名称 输入.wav 输出.wav` 试听。如果链的响度超过 plate 的两倍，音量测试会失败。
5. 用 `sofifi catalogo` 重新生成目录。RTL 仿真会运行能装入的链。

## 一条核心指令

这是结构性决策：`model/sofifi/domain/isa.py` 是哨兵文件，因此必须附带其 ADR 或 ADR 0009（西班牙语）的更新。

1. 在 `Op` 中添加值；如果耗时超过一个周期，同时在 `CICLOS`（`model/sofifi/domain/isa.py`）中添加。
2. 在 `model/sofifi/domain/nucleo.py` 中编写处理函数，并在 `MANEJADORES` 中注册。
3. 在 `model/sofifi/domain/ensamblador.py` 中添加助记符及其操作数。
4. 缺少上述三步中的任何一步，`model/tests/nucleo_test.py` 和 `model/tests/ensamblador_test.py` 中的契约测试都会失败。
5. 在 `CICLOS_RTL`（`model/sofifi/domain/coste.py`）中添加其 RTL 周期开销，并在 `MUESTRA_COSTE`（`sim/nucleo/nucleo_test.py`）中添加一行。仿真测量开销并与该表比较。

## 一个 RTL 模块

1. 先写模型，放在 `model/sofifi/domain/`。
2. RTL 放在 `rtl/`，带 SPDX 文件头。
3. 测试平台放在 `sim/`，逐个样本比较。
4. 如果是顶层，将其及其源文件写入 `rtl/top/tops.txt`，并在 `docs/ratchets.yaml` 中设置门槛 `recursos:<top>:LUT4` 和 `recursos:<top>:ALU`，取当前值（ADR 0010（西班牙语））。
5. 如果它固定引脚、时钟或存储器映射，必须附带其 ADR：这些文件是哨兵文件（`docs/adr/sentinelas.txt`）。
6. 用 `make esquematicos` 重新生成其原理图（ADR 0012（西班牙语））。

## 一个检查门

1. 在 `scripts/` 中添加脚本，在 `scripts/ci_local.sh` 的 `JOBS` 数组中添加一行 `"nombre:dura|blanda|release"`，并在 `run_job` 中添加其分支。不要改动 hook。
2. 声明类别：只有当所有人今天都能运行并修复它时，才设为硬检查门（P1）；如果开销大且只在点名时运行，设为 release（`make release-check`、`make optimizacion`）。
3. 如果它启动 EDA 工具，将其放在 `(ulimit -u "$TOPE_PROCESOS"; …)` 内。
4. 改动 `scripts/ci_local.sh` 属于触碰哨兵文件，因此必须附带其 ADR 或 ADR 更新。

## 一个 ADR

1. 以 `docs/adr/0001-la-compuerta-vive-en-el-repositorio.md`（西班牙语）的结构为模板，创建 `docs/adr/<NNNN>-<regla-en-kebab>.md`。
2. 在索引 `docs/adr/README.md`（西班牙语）中添加一行。`docs` 检查门检查两者是否一致。

## 一个阶段

1. 在 `docs/fases/` 中编写规格，包含固定章节（SPEC_RAIZ §2.5（西班牙语））。
2. 在阶段关闭之前，**不要**将其加入管控。关闭时：在 `docs/fases/estado_fases.csv` 中添加一行，写明发现和修订，并将 README 的版本升至 `0.<fase>`。
3. 在同一个 PR 中，用四种语言更新全部文档和信息图。用 `scripts/capturar_infografia.py --todas` 重新截图。`cierre` 关卡会检查这一点。
