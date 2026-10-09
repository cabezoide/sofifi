<!-- i18n: fuente=docs/scripts.md sha=35d6b1ed2f0c estado=al_dia -->
# Scripts and the `sofifi` CLI

This guide describes each script in `scripts/` and each command of the `sofifi` CLI. It is organized by task. For each tool, it tells what the tool does, the typical command, what the tool needs, and which gate or phase uses it.

The header or the docstring of each script gives all the details. The Python scripts that use argparse and the `sofifi` CLI also show their help with `--help`.

## Before you start

- Run all commands from the root of the repository. The `sofifi` CLI looks for `programas/` and `presets/` in the current directory.
- Make the environment one time with `make install`. It installs the model, the gate tools and the EDA tool chain in `.venv`.
- Install the hook one time with `make hooks`.
- To work with the board, install the udev rule `scripts/udev/99-tang-primer-25k.rules`. Its header gives the commands.

Exit codes that almost all tools use:

| Code | Meaning |
|---|---|
| 0 | Correct: the check passes or the task ends. |
| 1 | The check fails, or the board gives a result that is different from the model. |
| 2 | Incorrect use: an argument is missing, or the job does not exist. |

## 1. CI gates

The gate is in the repository (ADR 0001). `scripts/ci_local.sh` is the only list of jobs. The hook `scripts/hooks/pre-push` runs it with `--no-soft` and has no list of its own.

### Jobs of `scripts/ci_local.sh`

The table uses the run order of the `JOBS` list in `scripts/ci_local.sh`. The class names are the Spanish words in the script: `dura` (hard), `blanda` (soft) and `release`.

| Job | Class | What it checks | Script or command |
|---|---|---|---|
| `tech-debt` | hard | No comment starts with a debt marker. | `scripts/check_tech_debt.sh` |
| `secrets` | hard | There are no prohibited files and no credentials. No file is larger than 1 MiB; a demo `.ogg` can be 4 MiB. | `scripts/check_secrets_hygiene.sh` |
| `licenses` | hard | Each source file has an SPDX header. Code from other persons is in `docs/terceros.yaml` (ADR 0002). | `scripts/check_licenses.py` |
| `adr-gate` | hard | A diff that changes a sentinel of `docs/adr/sentinelas.txt` also changes an ADR. | `scripts/check_adr_gate.sh` |
| `docs` | hard | The paths, `make` targets and ADRs that the maps refer to exist. It also checks phases, version, hook and registers. | `scripts/check_docs.py` |
| `i18n` | hard | Each translation exists and its stamp is honest (ADR 0007). | `scripts/check_i18n.py` |
| `cierre` | hard | The READMEs and the infographics show the version, and the screenshots are current. | `scripts/check_cierre.py` |
| `model` | hard | Style, format, types and tests of the model. | `ruff check`, `ruff format --check`, `mypy` and `pytest -n auto` |
| `rtl-lint` | hard | Lint of each top in `rtl/top/tops.txt` and of each module in `rtl/comun/`, `rtl/primitivas/` and `rtl/nucleo/`. | `verilator --lint-only -Wall -DSIMULACION` |
| `sim` | hard | The cocotb testbenches give the same bits as the model (ADR 0003). | `pytest sim -n 4` |
| `ratchets` | hard | No measurement in `docs/ratchets.yaml` becomes worse than its limit. | `scripts/check_ratchets.py` |
| `shell-lint` | soft | shellcheck on `scripts/*.sh` and `scripts/hooks/*`. | `shellcheck` |
| `esquematicos` | soft | Each PDF in `schematics/` agrees with its RTL source (ADR 0012). | `scripts/esquematicos.py --comprobar` |
| `optimizacion` | release | Each top synthesizes and closes timing; the job prints hints (ADR 0010). | `scripts/check_optimizacion.py` |

Classes:

- **hard**: a failure stops the push. The summary shows `ROJO` (red).
- **soft**: a failure shows `WARN` and does not stop the push. If the tool is missing, the job shows `NO CORRIÓ` (did not run). Do not report it as green.
- **release**: the job runs only when you name it. It synthesizes all the tops and takes approximately 3 minutes.

### Commands

| Task | Command |
|---|---|
| Hard and soft jobs | `make ci` |
| Only hard jobs (what the pre-push hook runs) | `make ci-dura` |
| Show the list of jobs | `scripts/ci_local.sh --list` |
| Only some jobs | `scripts/ci_local.sh model docs` |
| Model | `make test` |
| RTL simulation | `make sim` |
| Maps and registers | `make docs` |
| Second pass before the PR | `make optimizacion` (jobs `optimizacion` and `ratchets`) |

`scripts/ci_local.sh` adds a line with its duration to `.ci_timing.log`. This file is not in git.

### Hook and bypasses

| Tool | What it does | When |
|---|---|---|
| `scripts/install_hooks.sh` | Sets `core.hooksPath = scripts/hooks`. | One time, with `make hooks`. |
| `scripts/hooks/pre-push` | Runs `scripts/ci_local.sh --no-soft`. | At each `git push`. |

Named bypasses. Use them only when you have a reason:

| Variable or option | Effect |
|---|---|
| `ADR_GATE_ACK=1` | `adr-gate` accepts a diff without an ADR. It means "I examined it and no decision changes". |
| `PREPUSH_SKIP=1` or `git push --no-verify` | The hook does not run the gate. |

### Single checks

The `check_*` scripts have no options. You run them without arguments. They do not write files, except `check_i18n.py --sellar`.

| Script | Typical command |
|---|---|
| `scripts/check_docs.py` | `.venv/bin/python scripts/check_docs.py` |
| `scripts/check_i18n.py` | `.venv/bin/python scripts/check_i18n.py` |
| `scripts/check_i18n.py --sellar` | `.venv/bin/python scripts/check_i18n.py --sellar docs/EXTENDING.en.md` (one file for each call) |
| `scripts/check_cierre.py` | `.venv/bin/python scripts/check_cierre.py` |
| `scripts/check_licenses.py` | `.venv/bin/python scripts/check_licenses.py` |
| `scripts/check_ratchets.py` | `.venv/bin/python scripts/check_ratchets.py` (after the `model` job) |

## 2. Synthesis and board

The board is a Sipeed Tang Primer 25K. The EDA tool chain is open and is in `.venv`: yowasp-yosys, yowasp-nextpnr-himbaechel-gowin, gowin_pack and openFPGALoader. The only list of tops and their sources is `rtl/top/tops.txt`.

> **Warning.** A top that sends at full rate on the UART stops the BL616 bridge if the PC stops reading. Then you must connect the USB again. Limit the rate of each new top (`rtl/AGENTS.md`, F-02 in `fails.md`).

| Tool | What it does | Typical command | It needs |
|---|---|---|---|
| `scripts/fpga.sh synth` | Synthesizes, places, routes and packs a top. It writes `build/<top>.fs` and `build/<top>_recursos.json`. | `make synth TOP=hil_nucleo` | `.venv` |
| `scripts/fpga.sh prog` | Loads the bitstream into the SRAM of the FPGA. The bitstream is lost at power-off. | `make prog TOP=hil_nucleo` (synthesizes first) | board on USB |
| `scripts/informe_recursos.py` | Summarizes the nextpnr report: used cells and MHz. | `fpga.sh synth` runs it. | nextpnr report |
| `scripts/check_optimizacion.py` | Synthesizes all the tops, requires timing closure and gives `PISTA` hints. | `make optimizacion` | `.venv`; it does not need the board |
| `scripts/leer_uart.py` | Reads the UART of the FPGA and requires a text. | `make uart` | board; `/dev/ttyUSB1` |

Variables of `scripts/fpga.sh`:

| Variable | Default value | Use |
|---|---|---|
| `TOP` (Makefile) | `hola_uart` | Top from `rtl/top/tops.txt` for `make synth` and `make prog`. |
| `FREQ_MHZ` | 100 | Clock target for nextpnr (ADR 0005). |
| `SEMILLAS_PNR` | `2 3 4` | Seeds that nextpnr tries if the clock does not close (F-33). |
| `SYNTH_OPCIONES` | empty | Added options for `synth_gowin`. |
| `CST` | `rtl/top/primer25k.cst` | Pin constraint file. |

The BL616 debugger gives two ports: `/dev/ttyUSB0` is JTAG and `/dev/ttyUSB1` is the UART of the FPGA, at 115 200 baud.

## 3. Tests on the board (HIL)

The bit-exact model is the reference (ADR 0003). Timing is measured on the board (ADR 0011). These tools load a top, request a capture on the UART and compare it with the model.

| Tool | What it does | Typical command | Exit |
|---|---|---|---|
| `make hil` | Writes the ROM of a program or a chain, synthesizes `hil_programa`, loads it and runs `scripts/hil_nucleo.py`. | `make hil HIL=marea` | 0 if the 4 096 samples agree |
| `scripts/hil_nucleo.py` | Compares 4 096 samples and the CRC-32 from the board with the model. With `--traza K0`, it finds the first instruction that is different. | `.venv/bin/python scripts/hil_nucleo.py --programa plate` | 0 if all agree |
| `scripts/hil_lote.py` | Runs `make hil` for many names and writes build/hil_lote.csv. Each name takes approximately 4 minutes. | `.venv/bin/python scripts/hil_lote.py --todos` | 0 if all agree |
| `scripts/margen_reloj.py` | Changes only the PLL divider of the routed design and repeats the capture at each frequency. | `.venv/bin/python scripts/margen_reloj.py --divisores 8 7 6` | 0 if 100 MHz always passes |
| `scripts/verificar_primitivas.py` | Checks the test tops of the primitives: `dsp`, `bsram`, `pll` and `fs`. | `.venv/bin/python scripts/verificar_primitivas.py dsp` | 0 if all lines are correct |

Which top each test loads:

| Test | Top | Script |
|---|---|---|
| Core with `plate` | `make prog TOP=hil_nucleo` | `scripts/hil_nucleo.py` |
| Looper | `make prog TOP=hil_looper` | `scripts/hil_nucleo.py --programa looper` |
| Any program or chain | `make hil HIL=NAME` | `scripts/hil_nucleo.py --programa NAME` (`make hil` runs it) |
| Clock margin | `make synth TOP=hil_nucleo` and `make synth TOP=prueba_pll` | `scripts/margen_reloj.py` (`--base hil_looper --programa looper` for the looper) |
| DSP multiplier | `make prog TOP=prueba_dsp` | `scripts/verificar_primitivas.py dsp` |
| BSRAM | `make prog TOP=prueba_bsram` | `scripts/verificar_primitivas.py bsram` |
| PLL | `make prog TOP=prueba_pll` | `scripts/verificar_primitivas.py pll` |
| Sample rate and UART RX | `make prog TOP=prueba_fs` | `scripts/verificar_primitivas.py fs` |
| MicroSD | `make prog TOP=prueba_sd` | `scripts/prueba_sd.py` (section 4) |

Notes:

- `make hil` accepts a program or a chain that fits in the memory of `hil_nucleo`: 38 912 words. `sofifi rom` refuses the others.
- `scripts/margen_reloj.py` needs `build/<base>.pnr.json` and build/prueba_pll.fs. At the end, it loads `prueba_pll`, which sends little data on the UART.
- All these tools read `/dev/ttyUSB1` by default. Change the port with `--puerto`.

## 4. MicroSD

The microSD stores programs; it does not delay audio (ADR 0004). The full procedure, with the warning about `dd`, is in [microsd.md](microsd.md) (Spanish only).

| Tool | What it does | Typical command | It needs |
|---|---|---|---|
| `sofifi banco` | Writes the bank image. Without names, it contains all that fits. | `.venv/bin/sofifi banco build/banco.img` | nothing |
| `sofifi banco --leer` | Checks the CRC and the limits of each slot and lists the slots. | `.venv/bin/sofifi banco --leer build/banco.img` | nothing |
| `scripts/prueba_sd.py` | Tells `prueba_sd` to load each slot and compares it with the model. | `.venv/bin/python scripts/prueba_sd.py --imagen build/banco.img` | board, PMOD TF on J6, written card, `/dev/ttyUSB1` |

Phase 08: nobody has tested `scripts/prueba_sd.py` with a real card yet.

## 5. Documentation and media

| Tool | What it does | Typical command | When |
|---|---|---|---|
| `scripts/check_i18n.py --sellar` | Updates the stamp of a translation. | `.venv/bin/python scripts/check_i18n.py --sellar README.en.md` | After you update each translation (ADR 0007). |
| `scripts/capturar_infografia.py` | Captures the sections of the infographics as PNG files and records their hash in `docs/img/capturas.json`. | `.venv/bin/python scripts/capturar_infografia.py --todas` | When a phase closes (gate `cierre`). |
| `scripts/esquematicos.py` | Makes one PDF for each RTL module in `schematics/`. | `make esquematicos` | After you change an RTL module (ADR 0012). |
| `scripts/generar_demos.py` | Makes the Ogg demos of `demo_examples/` and their guides again. | `.venv/bin/python scripts/generar_demos.py` | After you change a program that has a demo. |
| `sofifi catalogo` | Makes the catalog of programs, presets and chains again. | `.venv/bin/sofifi catalogo` | After you change a program, a preset or a chain. |

Requirements:

- `scripts/capturar_infografia.py` and `scripts/esquematicos.py` need chrome-headless-shell from the Playwright cache (`~/.cache/ms-playwright`).
- `scripts/esquematicos.py` also needs netlistsvg: `make esquematicos` first runs `npm install` in `herramientas/esquematicos/`. The option `--comprobar` needs neither tool.
- `scripts/generar_demos.py` needs the `demos` extra (`make install` installs it). It takes approximately 2 minutes on 8 cores. It writes an `.ogg` file again only if its audio changes.

## 6. Model and programs: the `sofifi` CLI

The `sofifi` CLI is the entry to the bit-exact model. `make install` installs it in `.venv/bin/sofifi`. Each command shows its help with `sofifi COMMAND --help`.

| Command | What it does | Example | It writes |
|---|---|---|---|
| `asm` | Assembles a program and gives its RTL cycles out of 2 048 (ADR 0005). | `sofifi asm programas/plate.sasm build/plate` | build/plate.hex and build/plate.json |
| `tablas` | Makes the Hermite table and the ROM programs of the RTL again. | `sofifi tablas` | `.v` files in `rtl/` |
| `catalogo` | Makes the catalog of programs, presets and chains again. | `sofifi catalogo` | `docs/programas.md` and its translations |
| `render` | Processes a WAV file with a program. | `sofifi render programas/plate.sasm seca.wav plate.wav --preset 'Placa corta'` | the output WAV |
| `presets` | Lists the presets of `presets/banco.toml`. | `sofifi presets plate` | nothing |
| `cadenas` | Lists the chains with their cost and tells if they fit (ADR 0013). | `sofifi cadenas` | nothing |
| `componer` | Writes a chain as one program. | `sofifi componer "Eco y muelle" build/eco.sasm` | the output `.sasm` |
| `cadena` | Processes a WAV file with a chain. | `sofifi cadena "Eco y muelle" seca.wav eco.wav` | the output WAV |
| `rom` | Writes the `programa_hil` ROM of a program or a chain. | `sofifi rom marea build/programa_hil.v` | the output `.v` |
| `banco` | Writes or checks the microSD image. | `sofifi banco build/banco.img` | the image |

Options of `render` and `cadena`:

| Option | Effect |
|---|---|
| `--pot potN=V` | Sets knob N to the value V, from 0 to 1. You can repeat it. |
| `--freeze INICIO:FIN` | Pushes the footswitch between these seconds. You can repeat it. |
| `--cola S` | Adds S seconds of silence at the end. |
| `--preset NOMBRE` | Only `render`: starts from the knobs of a preset. Then each `--pot` applies. |

A chain starts from the knob positions in `presets/cadenas.toml`.

To add a program, an RTL module or a gate, read [EXTENDING.en.md](EXTENDING.en.md).

### Acceptance test of the core

`sim/nucleo/nucleo_test.py` compares the RTL core with the model. The `sim` gate uses 1 000 samples. For the full acceptance test:

```sh
SOFIFI_MUESTRAS=4883 .venv/bin/python -m pytest sim/nucleo/nucleo_test.py
```

## Behaviors to know

- `scripts/generar_demos.py` accepts `--readme`, `--help` or no argument. Any other argument gives exit code 2 and makes no demo.
- The `check_*` scripts do not read arguments. `scripts/check_optimizacion.py --help` synthesizes all the tops.
- `scripts/informe_recursos.py` needs the path of the nextpnr report. Without it, it shows the usage and gives exit code 2.
- `scripts/capturar_infografia.py` prints its help and exits with 1 if the arguments are not correct or if chrome-headless-shell is missing.
- `scripts/ci_local.sh --help` and `scripts/fpga.sh` without a command print their header.
