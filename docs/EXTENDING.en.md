<!-- i18n: fuente=docs/EXTENDING.md sha=24e37a7d6593 estado=al_dia -->
# How to extend

This guide gives the steps for each type of part. Sometimes an addition makes
you change a location that is not in this list. Then the list is incomplete.
Correct it in the same PR.

## A program (an effect)

An effect is a program, not an RTL module (ADR 0006 (Spanish)).

1. If the program comes from a third party, add its entry in `docs/terceros.yaml`.
   `uso: portado` is permitted only with a permissive license (ADR 0002 (Spanish)).
2. Write `programas/<nombre>.sasm`. The header has these lines:
   - `; familia:` and `; resumen:`;
   - `; resumen.en:`, `; resumen.zh-CN:` and `; resumen.ja:`, the translated summary;
   - `; potN = nombre`, one line for each control.
3. Get the blocks that exist from `programas/comun/` with `include`.
4. Make sure that the program fits. `sofifi asm programas/<nombre>.sasm out/<nombre>`
   gives the RTL cycles. They must be 2,048 or less (`model/sofifi/domain/coste.py`).
5. Write the test of its acoustic property in `model/tests/`, in the file of its
   family or in a new file. The common measurements are in `model/tests/acustica.py`.
6. Add its fingerprint in `HUELLAS` (`model/tests/programas_test.py`). The tests
   for "fits", for the fingerprint and for equality with the RTL
   (`sim/nucleo/nucleo_test.py`) examine all the `.sasm` files. They fail if a part is missing.
7. If a control has a new name, add its translation in `MANDOS`
   (`model/sofifi/services/catalogo_textos.py`). `model/tests/catalogo_test.py` requires it.
8. Add a minimum of 12 presets (section "A preset").
9. Generate the catalog again in the four languages with `sofifi catalogo`.
10. Add the demo in `DEMOS` (`scripts/generar_demos.py`). Run the script:
    it writes the `.ogg` file and the guides `demo_examples/README*.md`.
11. If the program fits in the 38 blocks of `hil_nucleo`, test it on the board
    with `make hil HIL=<nombre>`.

## A change to a program that exists

> **Warning.** A change in `programas/comun/` changes all the programs that
> include it. F-32 changed the fingerprints of 74 programs.

1. Update the fingerprints that change in `HUELLAS`.
2. If `plate`, `looper` or a block that they include changes, run `sofifi tablas`.
   It generates the ROMs `rtl/top/programa_plate.v` and `rtl/top/programa_looper.v` again.
   `model/tests/tablas_test.py` requires it.
3. Generate the catalog again with `sofifi catalogo`.
4. Generate the demos again with `scripts/generar_demos.py`. The script writes
   an `.ogg` file again only if its audio changes.

## A preset

A preset is the same program with different control values and a name.

1. Add a line `"Nombre" = [pot0, pot1, …]` in the table of the program, in
   `presets/banco.toml`. The values go from 0 to 1. A control that the program does not use is 0.
2. Listen to the preset: `sofifi render programas/<programa>.sasm entrada.wav salida.wav --preset "Nombre"`.
3. Measure its level: `.venv/bin/python scripts/medir_presets.py <programa>`. No preset can give SATURA or FUERTE.
4. Generate the catalog again with `sofifi catalogo`: the catalog counts the presets.
   `model/tests/presets_test.py` checks the program, the controls and the ranges.

## A chain (two programs in one)

A chain joins programs that already exist, with no change to the RTL (ADR 0013, Spanish).

1. Look with `sofifi cadenas` at how much a similar chain uses. Each program
   uses its own registers and LFOs. The core has 32 general registers and 4 LFOs.
2. Add a `[[cadena]]` in `presets/cadenas.toml`:
   - in `mandos`, a number is a fixed value and `"potN"` is pot N of the pedal;
   - `pots` gives the six pots when the chain loads.
3. If the chain only needs memory, set `requiere = "sdram"`.
   `model/tests/cadenas_test.py` requires that each chain fits, or that it only needs memory.
4. Listen with `sofifi cadena NOMBRE entrada.wav salida.wav`. The volume test
   fails if the chain is more than twice as loud as the plate.
5. To see the composed program, run `sofifi componer NOMBRE salida.sasm`.
6. Generate the catalog again with `sofifi catalogo`. The RTL simulation runs
   the chains that fit.
7. For a demo, add the chain in `DEMOS_CADENAS` (`scripts/generar_demos.py`).
8. If the chain fits in `hil_nucleo`, test it on the board with `make hil HIL="NOMBRE"`.

## A core instruction

A new instruction is a structural decision. `model/sofifi/domain/isa.py` is a
sentinel file: the change must have its own ADR or an update of ADR 0009 (Spanish).

1. Add the value in `Op`. If the instruction costs more than one cycle, also add it in `CICLOS` (`model/sofifi/domain/isa.py`).
2. Write the handler in `model/sofifi/domain/nucleo.py`. Register it in `MANEJADORES`.
3. Add the mnemonic and its operands in `model/sofifi/domain/ensamblador.py`.
   The contracts in `model/tests/nucleo_test.py` and `model/tests/ensamblador_test.py`
   fail if one of the three steps is missing.
4. Add its execution cycles in `DURACION` (`model/sofifi/domain/coste.py`).
5. If the instruction reads the ACC or the register bank, also add it to `LEE_ACC` or to `LEE_REGISTRO`.
6. Add one line in `MUESTRA_COSTE` (`sim/nucleo/nucleo_test.py`). The
   simulation requires the same cycles as the timing model, alone and next to
   each instruction (ADR 0014, Spanish).

## An RTL module

1. Write the model first, in `model/sofifi/domain/`.
2. Write the RTL in `rtl/`, with an SPDX header.
3. Write the testbench in `sim/`. It compares with the model sample by sample.
4. If the module sets pins, clocks or the memory map, write its ADR in the
   same PR. Those files are sentinels (`docs/adr/sentinelas.txt`).
5. Generate its schematic again with `make esquematicos` (ADR 0012 (Spanish)).
6. Update `docs/arquitectura_fpga.md` and `SBOM.md`, and their translations.

## A top

A top is a full design for the board: the pins, the PLL and the modules.

1. Write `rtl/top/<top>.v`. The pins are in `rtl/top/primer25k.cst`.
2. Add a line in `rtl/top/tops.txt` with the top and its sources. The first
   source defines the top. The Makefile and the gate read this list.
3. Add the ratchets `recursos:<top>:LUT4` and `recursos:<top>:ALU` in
   `docs/ratchets.yaml`. Set them at the current values (ADR 0010 (Spanish)).
4. Synthesize and load with `make prog TOP=<top>`.
5. If the top sends data through the UART, limit the data rate. If you do not,
   the BL616 bridge stops (`rtl/AGENTS.md`).
6. Measure the clock margin on the board, not in nextpnr (ADR 0011 (Spanish)).

## A gate

> **Warning.** `scripts/ci_local.sh` is a sentinel: a change to it must have
> its own ADR or an ADR update.

1. Add the script in `scripts/`.
2. Add one line `"nombre:dura|blanda|release"` in the `JOBS` array of
   `scripts/ci_local.sh`, and its branch in `run_job`. Do not change the hook.
3. Declare the class:
   - hard, only if all persons can run it and repair it today (P1);
   - release, if it is expensive and runs only when you name it (`make release-check`, `make optimizacion`);
   - soft, in all other cases.
4. If the gate starts EDA tools, put it in `(ulimit -u "$TOPE_PROCESOS"; …)`.

## An ADR

1. Create `docs/adr/<NNNN>-<regla-en-kebab>.md` with the structure of
   `docs/adr/0001-la-compuerta-vive-en-el-repositorio.md` (Spanish).
2. Add its row to the index `docs/adr/README.md` (Spanish). The `docs` gate
   checks that the index and the files agree.

## A phase

1. Write the spec in `docs/fases/` with the fixed sections (SPEC_RAIZ §2.5 (Spanish)).
2. Do **not** add the phase to the control until you close it.
3. When you close it, add its row in `docs/fases/estado_fases.csv`, with the finding and the amendments.
4. Increase the version of the four README files to `0.<fase>`.
5. In the same PR, update all the documentation and the infographics in the four
   languages. Make the captures again with `scripts/capturar_infografia.py --todas`.
   The `cierre` gate checks this.
