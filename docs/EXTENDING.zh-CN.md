<!-- i18n: fuente=docs/EXTENDING.md sha=3bfc3280c871 estado=al_dia -->
# 如何扩展

本文按部件类型逐步说明。如果添加某样东西需要改动本清单之外的位置，说明清单不完整。在同一个 PR 中修正它。

## 一个程序（一个效果）

效果是程序，不是 RTL 模块（ADR 0006（西班牙语））。

1. 如果程序来自第三方，在 `docs/terceros.yaml` 中添加其条目。
   只有许可证为宽松许可证时，才可使用 `uso: portado`（ADR 0002（西班牙语））。
2. 编写 `programas/<nombre>.sasm`。文件头包含以下各行：
   - `; familia:` 和 `; resumen:`；
   - `; resumen.en:`、`; resumen.zh-CN:` 和 `; resumen.ja:`，即翻译后的摘要；
   - `; potN = nombre`，每个旋钮一行。
3. 用 `include` 从 `programas/comun/` 引入已有的模块。
4. 检查程序是否放得下：`sofifi asm programas/<nombre>.sasm out/<nombre>` 给出 RTL 周期数。
   周期数必须不超过 2,048（`model/sofifi/domain/coste.py`）。
5. 在 `model/tests/` 中编写其声学特性的测试，放在其所属系列的文件或单独的文件中。
   通用测量位于 `model/tests/acustica.py`。
6. 在 `HUELLAS`（`model/tests/programas_test.py`）中添加其指纹。“放得下”、指纹以及与 RTL
   一致性（`sim/nucleo/nucleo_test.py`）的测试会遍历所有 `.sasm`，缺少任何内容都会失败。
7. 如果某个旋钮使用新名称，在 `MANDOS`（`model/sofifi/services/catalogo_textos.py`）中添加其翻译。
   `model/tests/catalogo_test.py` 要求这一点。
8. 添加至少 5 个预设（见“一个预设”一节）。
9. 用 `sofifi catalogo` 以四种语言重新生成目录。
10. 在 `DEMOS`（`scripts/generar_demos.py`）中添加演示。运行该脚本：
    它写出 `.ogg` 和指南 `demo_examples/README*.md`。
11. 如果程序能装进 `hil_nucleo` 的 38 个块，用 `make hil HIL=<nombre>` 在开发板上测试。

## 修改一个已有的程序

> **警告。** 对 `programas/comun/` 的改动会改变所有引入它的程序。
> F-32 改变了 74 个程序的指纹。

1. 在 `HUELLAS` 中更新发生变化的指纹。
2. 如果 `plate`、`looper` 或它们引入的模块发生变化，运行 `sofifi tablas`。
   它重新生成 ROM `rtl/top/programa_plate.v` 和 `rtl/top/programa_looper.v`。
   `model/tests/tablas_test.py` 要求这一点。
3. 用 `sofifi catalogo` 重新生成目录。
4. 用 `scripts/generar_demos.py` 重新生成演示。只有音频发生变化时，才会重写 `.ogg`。

## 一个预设

预设是同一个程序，配上其他旋钮值和一个名称。

1. 在 `presets/banco.toml` 中该程序的表里添加一行 `"Nombre" = [pot0, pot1, …]`。
   取值范围为 0 到 1；未使用的旋钮为 0。
2. 试听预设：`sofifi render programas/<programa>.sasm entrada.wav salida.wav --preset "Nombre"`。
3. 用 `sofifi catalogo` 重新生成目录：目录会统计预设数量。
   `model/tests/presets_test.py` 检查程序、旋钮和取值范围。

## 一条链（两个程序合为一个）

链把已有的程序连在一起，不改动 RTL（ADR 0013，西班牙语）。

1. 用 `sofifi cadenas` 查看类似的链用了多少资源。每个程序使用自己的寄存器和 LFO。
   核心有 32 个通用寄存器和 4 个 LFO。
2. 在 `presets/cadenas.toml` 中添加一个 `[[cadena]]`：
   - 在 `mandos` 中，数字是固定值，`"potN"` 是踏板的第 N 个电位器；
   - `pots` 给出加载链时六个电位器的位置。
3. 如果链只缺存储器，设置 `requiere = "sdram"`。
   `model/tests/cadenas_test.py` 要求每条链都能装入，或者只缺存储器。
4. 用 `sofifi cadena 名称 输入.wav 输出.wav` 试听。如果链的响度超过 plate 的两倍，
   音量测试会失败。
5. 要查看组合程序，运行 `sofifi componer 名称 输出.sasm`。
6. 用 `sofifi catalogo` 重新生成目录。RTL 仿真会运行能装入的链。
7. 要制作演示，在 `DEMOS_CADENAS`（`scripts/generar_demos.py`）中添加该链。
8. 如果链能装进 `hil_nucleo`，用 `make hil HIL="名称"` 在开发板上测试。

## 一条核心指令

新指令是结构性决策。`model/sofifi/domain/isa.py` 是哨兵文件：
改动必须附带其 ADR 或 ADR 0009（西班牙语）的更新。

1. 在 `Op` 中添加值；如果耗时超过一个周期，同时在 `CICLOS`（`model/sofifi/domain/isa.py`）中添加。
2. 在 `model/sofifi/domain/nucleo.py` 中编写处理函数，并在 `MANEJADORES` 中注册。
3. 在 `model/sofifi/domain/ensamblador.py` 中添加助记符及其操作数。
   缺少上述三步中的一步，`model/tests/nucleo_test.py` 和 `model/tests/ensamblador_test.py`
   中的契约测试就会失败。
4. 在 `DURACION`（`model/sofifi/domain/coste.py`）中添加其执行周期。
5. 如果指令读取 ACC 或寄存器组，也把它加入 `LEE_ACC` 或 `LEE_REGISTRO`。
6. 在 `MUESTRA_COSTE`（`sim/nucleo/nucleo_test.py`）中添加一行。仿真要求与时序模型的
   周期数相同，单独运行和与每条指令相邻时都一样（ADR 0014，西班牙语）。

## 一个 RTL 模块

1. 先写模型，放在 `model/sofifi/domain/`。
2. 在 `rtl/` 中编写 RTL，带 SPDX 文件头。
3. 在 `sim/` 中编写测试平台。它逐个样本与模型比较。
4. 如果模块固定引脚、时钟或存储器映射，在同一个 PR 中编写其 ADR。
   这些文件是哨兵文件（`docs/adr/sentinelas.txt`）。
5. 用 `make esquematicos` 重新生成其原理图（ADR 0012（西班牙语））。
6. 更新 `docs/arquitectura_fpga.md` 和 `SBOM.md` 及其译本。

## 一个顶层

顶层是开发板上的完整设计：引脚、PLL 和各模块。

1. 编写 `rtl/top/<top>.v`。引脚位于 `rtl/top/primer25k.cst`。
2. 在 `rtl/top/tops.txt` 中添加一行，写明顶层及其源文件。第一个源文件定义顶层。
   Makefile 和检查门都读取这个列表。
3. 在 `docs/ratchets.yaml` 中添加门槛 `recursos:<top>:LUT4` 和 `recursos:<top>:ALU`，
   取当前值（ADR 0010（西班牙语））。
4. 用 `make prog TOP=<top>` 综合并加载。
5. 如果顶层通过 UART 发送数据，限制其速率：否则 BL616 的桥接会挂起（`rtl/AGENTS.md`，西班牙语）。
6. 在开发板上测量时钟余量，而不是在 nextpnr 中（ADR 0011（西班牙语））。

## 一个检查门

> **警告。** `scripts/ci_local.sh` 是哨兵文件：对它的改动必须附带其 ADR 或某个 ADR 的更新。

1. 在 `scripts/` 中添加脚本。
2. 在 `scripts/ci_local.sh` 的 `JOBS` 数组中添加一行 `"nombre:dura|blanda|release"`，
   并在 `run_job` 中添加其分支。不要改动 hook。
3. 声明类别：
   - 硬检查门：只有当所有人今天都能运行并修复它时（P1）；
   - release：如果开销大且只在点名时运行（`make release-check`、`make optimizacion`）；
   - 软检查门：其他情况。
4. 如果检查门启动 EDA 工具，将其放在 `(ulimit -u "$TOPE_PROCESOS"; …)` 内。

## 一个 ADR

1. 以 `docs/adr/0001-la-compuerta-vive-en-el-repositorio.md`（西班牙语）的结构，
   创建 `docs/adr/<NNNN>-<regla-en-kebab>.md`。
2. 在索引 `docs/adr/README.md`（西班牙语）中添加其一行。`docs` 检查门检查两者是否一致。

## 一个阶段

1. 在 `docs/fases/` 中编写规格，包含固定章节（SPEC_RAIZ §2.5（西班牙语））。
2. 在阶段关闭之前，**不要**将其加入管控。
3. 关闭阶段时，在 `docs/fases/estado_fases.csv` 中添加其一行，写明发现和修订。
4. 将四个 README 的版本升至 `0.<fase>`。
5. 在同一个 PR 中，用四种语言更新全部文档和信息图。用 `scripts/capturar_infografia.py --todas`
   重新截图。`cierre` 检查门会检查这一点。
