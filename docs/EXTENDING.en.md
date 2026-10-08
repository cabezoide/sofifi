<!-- i18n: fuente=docs/EXTENDING.md sha=a578f7b153a1 estado=al_dia -->
# How to extend

This guide gives the steps for each type of part. Sometimes an addition makes
you change a location that is not in this list. Then the list is incomplete:
correct it in the same PR.

## An effect (core program)

An effect is a program, not an RTL module (ADR 0006 (Spanish)).

1. If the effect comes from a third party, add its entry in `docs/terceros.yaml`.
   `uso: portado` is permitted only with a permissive license (ADR 0002 (Spanish)).
2. Write `programas/<nombre>.sasm`. The header has `; familia:`,
   `; resumen:` and one line `; potN = nombre` for each control. Get the
   blocks that exist from `programas/comun/` with `include`.
3. Make sure that the program fits. `sofifi asm` gives the RTL cycles. The
   cycles must be 2,048 or less (`model/sofifi/domain/coste.py`).
4. Write the test of its acoustic property in the file of its family
   (`model/tests/programas_<familia>_test.py`). The common measurements are in
   `model/tests/acustica.py`.
5. Add its fingerprint in `HUELLAS` (`model/tests/programas_test.py`). The
   tests for "fits", for the fingerprint and for equality with the RTL
   (`sim/nucleo/nucleo_test.py`) examine all the `.sasm` files. They fail if
   a part is missing.
6. Add a minimum of 5 presets in `presets/banco.toml`, in a table with the
   name of the program. `model/tests/presets_test.py` checks the controls.
7. Generate the catalog again with `sofifi catalogo`.
8. Add the demo in `DEMOS` (`scripts/generar_demos.py`) and in
   `demo_examples/README.en.md`.

## A core instruction

This is a structural decision. `model/sofifi/domain/isa.py` is a sentinel file.
Thus the change must have its own ADR or an update of ADR 0009 (Spanish).

1. Add the value in `Op`. If the instruction costs more than one cycle, also add it in `CICLOS` (`model/sofifi/domain/isa.py`).
2. Write the handler in `model/sofifi/domain/nucleo.py`. Register it in `MANEJADORES`.
3. Add the mnemonic and its operands in `model/sofifi/domain/ensamblador.py`.
4. The contracts in `model/tests/nucleo_test.py` and `model/tests/ensamblador_test.py` fail if one of the three steps is missing.
5. Add its cost in RTL cycles in `CICLOS_RTL` (`model/sofifi/domain/coste.py`). Add one line in `MUESTRA_COSTE` (`sim/nucleo/nucleo_test.py`). The simulation measures the cost and compares it with the table.

## An RTL module

1. Write the model first, in `model/sofifi/domain/`.
2. Put the RTL in `rtl/`, with an SPDX header.
3. Put the testbench in `sim/`. The testbench compares the output sample by sample.
4. If the module is a top, put it in `rtl/top/tops.txt` with its sources. Add
   the ratchets `recursos:<top>:LUT4` and `recursos:<top>:ALU` in
   `docs/ratchets.yaml`. Set them at the current values (ADR 0010 (Spanish)).
5. If the module sets pins, clocks or the memory map, it must have its own ADR.
   Those files are sentinels (`docs/adr/sentinelas.txt`).
6. Generate its schematic again with `make esquematicos` (ADR 0012 (Spanish)).

## A gate

1. Add the script in `scripts/`. Add one line `"nombre:dura|blanda|release"` in
   the `JOBS` array of `scripts/ci_local.sh`. Add its branch in `run_job`. Do
   not change the hook.
2. Declare the class. Use hard only if all persons can run it and repair it
   today (P1). Use release if it is expensive and runs only when you name it
   (`make release-check`, `make optimizacion`).
3. If the gate starts EDA tools, put them in `(ulimit -u "$TOPE_PROCESOS"; …)`.
4. A change to `scripts/ci_local.sh` touches a sentinel. Thus it must have its
   own ADR or an ADR update.

## An ADR

1. Create `docs/adr/<NNNN>-<regla-en-kebab>.md`. Use the structure of
   `docs/adr/0001-la-compuerta-vive-en-el-repositorio.md` (Spanish).
2. Add the row to the index `docs/adr/README.md` (Spanish). The `docs` gate
   checks that the index and the files agree.

## A phase

1. Write the spec in `docs/fases/` with the fixed sections (SPEC_RAIZ §2.5 (Spanish)).
2. Do **not** add the phase to the control until you close it. When you close
   it, add a row in `docs/fases/estado_fases.csv` with the finding and the
   amendments. Then increase the README version to `0.<fase>`.
3. In the same PR, update all the documentation and the infographics in the four
   languages. Make the captures again with
   `scripts/capturar_infografia.py --todas`. The `cierre` gate checks this.
