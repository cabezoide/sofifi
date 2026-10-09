<!-- i18n: fuente=fails.md sha=89f1e6883b89 estado=al_dia -->
# Failures and their resolution

This is the record of the failures found in the project. Each entry has a symptom, a diagnosis, a root cause, a resolution and a lesson. The record helps us not to repeat them. It also explains why the design is as it is.

Add a new entry when a failure is diagnosed and resolved. Do not rewrite the entries: if something changes later, add a note with the date.

| ID | Phase | Failure | Status |
|---|---|---|---|
| F-01 | 02 | The verilator wrapper started itself and stopped the machine | resolved |
| F-02 | 03 | The BL616 UART bridge hangs | resolved (with a usage rule) |
| F-03 | 03 | apicula 0.32 does not pack a PLLA with default dividers | resolved |
| F-04 | 03 | Yosys does not infer DSP blocks for the GW5A | resolved |
| F-05 | 03 | nextpnr does not find the output frequency of the PLL | resolved |
| F-06 | 03 | In simulation, the reset never occurred | resolved |
| F-07 | 02 | The first bitstream used two times the necessary logic | resolved |
| F-08 | 04 | Unsigned shifts and an overflow in the RTL | resolved |
| F-09 | 04 | Hold violations in the single-port BSRAMs | resolved |
| F-10 | 04 | The core did not close timing (70 MHz) | resolved |
| F-11 | 05 | The silicon failed at 100 MHz, but nextpnr gave 132 | resolved; measured margin ≥ 6 %, to increase |
| F-12 | 05 | A test of the memory clear found nothing | resolved |
| F-13 | 05 | The first line of the dump was lost | resolved |
| F-14 | 05 | apicula 0.32 does not pack BSRAM without initial contents | resolved |
| F-15 | 06 | The read-ahead worked in simulation and failed in the silicon at 100 MHz | resolved; measured margin ≥ 20 % |
| F-16 | 06 | Large simulations did not compile with the pip verilator | resolved |
| F-17 | 06 | The velvet-noise diffuser did not do better than the allpass filters | rejected: not published |
| F-18 | 06 | Four programming faults in the Phase 06 catalog | resolved before publication |
| F-19 | 07 | With RDAA and WRAA, the silicon failed at 114 MHz in the first sample | resolved; measured margin ≥ 25 % |
| F-20 | 07 | The clear of the absolute region did not clear two words | resolved |
| F-21 | 07 | In marea, the software LFO stayed at +1 | resolved before publication |
| F-22 | 07 | The shoegaze program was five times louder than the plate | resolved before publication |
| F-23 | 07 | A chain with saturation was six times louder than the plate | resolved before publication |
| F-24 | 07 | The microcode queue took the last BSRAM | resolved |
| F-25 | 08 | Three failures of the SD controller, found in simulation | resolved before the board |
| F-26 | 08 | Four fixed-point traps in batch 9 of the catalogue | resolved before publication |
| F-27 | 08 | Small constants, control loops and a blind fingerprint in batch 10 | resolved before publication |
| F-28 | 08 | The minimum speed of phaser and filtro was 0, and three traps in batch 11 | resolved |
| F-29 | 08 | Five modulation and level traps in batch 12 | resolved before publication |
| F-30 | 08 | Detectors, seams and read limits in batch 13 | resolved before publication |

---

## F-01 · The verilator wrapper started itself

- **Symptom:** the development machine stopped two times. The kernel killed processes because there was not sufficient memory (OOM).
- **Diagnosis:** the OOM dump showed approximately 14,000 `verilator` processes.
- **Root cause:** someone made the link `.venv/bin/verilator -> verilator-cli` manually. The pip wrapper finds `verilator` in PATH and runs it. With the link, the wrapper found itself and started itself again without end.
- **Resolution:** no link. `sim/conftest.py` and `scripts/ci_local.sh` call the real binary of the package with `VERILATOR_ROOT`. The gate runs the EDA tools under `ulimit -u`.
- **Lesson:** when you test a new tool that starts subprocesses, use `ulimit -u` and `timeout`.

## F-02 · The BL616 UART bridge hangs

- **Symptom:** the board stops sending data to the PC, with any bitstream, until you connect the USB again. The FPGA configuration is correct (openFPGALoader reports `Done Final`).
- **Diagnosis:** we did seven tests with reconnection during phases 03 and 05. In Phase 03 it looked like a BSRAM failure. In Phase 05 the pattern became clear:

  | Condition | Result |
  |---|---|
  | The FPGA sends at a high rate and the PC reads continuously (HIL dumps, 11.5 kB/s) | does not hang |
  | You program the FPGA again while it sends ≥ 2 kB/s (the PC does not read during JTAG) | hangs |
  | You program it again while it sends ~1.4 kB/s or less | continues to operate |

- **Root cause:** the BL616 firmware cannot accept unread bytes that collect while it does a different task, specially during JTAG programming. We cannot change this firmware.
- **Resolution:**
  - the test tops limit their rate (approximately 300 B/s to 1.4 kB/s);
  - the HIL sends a dump only when the PC asks for it;
  - the scripts load a silent design (`prueba_pll`) **before** they release the port.
- **Lesson:** before you program the FPGA again, make sure that it does not send at a high rate. If it does, read the port while you program it.

## F-03 · apicula 0.32 does not pack a PLLA with default dividers

- **Symptom:** `gowin_pack` stops with `invalid literal for int() with base 2: '8'`.
- **Root cause:** apicula keeps the default values of the PLLA in decimal and reads them as binary.
- **Resolution:** `rtl/primitivas/pll_100.v` sets all the dividers, also the dividers of the outputs that are not used.

## F-04 · Yosys does not infer DSP blocks for the GW5A

- **Symptom:** an `a * b` became LUTs and ALUs.
- **Root cause:** Yosys 0.69 infers DSP only for the gw1n and gw2a families.
- **Resolution:** we instantiate `MULT27X36` in `rtl/primitivas/mult_27x36.v`. It uses 2 of the 28 DSP blocks. We verified it on the board up to 160 MHz.

## F-05 · nextpnr does not find the output frequency of the PLL

- **Symptom:** the report applied the generic 50 MHz target to `clk_100`.
- **Resolution:** `scripts/fpga.sh` sets a 100 MHz target on all the clocks.

## F-06 · In simulation, the reset never occurred

- **Symptom:** a test top sent incorrect data in simulation.
- **Root cause:** verilator starts the registers at 0. With the simulated PLL, `bloqueado` is 1 from the start, and the reset that comes from it never becomes active.
- **Resolution:** each clock domain has its own start counter.

## F-07 · The first bitstream used two times the necessary logic

- **Symptom:** `hola_uart` used 353 LUT4 and 146 ALU. The owner asked if this was normal.
- **Root cause:** the design converted the 8 digits of the counter to ASCII in parallel, and then selected one.
- **Resolution:** the design now selects the digit first and converts it one time: 207 LUT4 and 82 ALU. This failure is the origin of the second optimization pass (ADR 0010).

## F-08 · Unsigned shifts and an overflow in the RTL

- **Symptom:** unit tests against the model failed, but the tests of the programs passed.
- **Root cause:** in Verilog, a bit selection (`p[49:0]`) and a concatenation (`{...}`) are **unsigned**, thus `>>>` does a logical shift. This occurred two times (in `curva_fin`). Also, in the RND LFO, `objetivo − actual` needed 25 bit, but the design calculated it in 24.
- **Resolution:** go through a `signed` wire before the shift; calculate the difference in 25 bit.
- **Lesson:** test each block against its model function with thousands of random vectors. The tests of the programs cover only the values that those programs make.

## F-09 · Hold violations in the single-port BSRAMs

- **Symptom:** 104 hold violations in the first synthesis of the core.
- **Root cause:** Yosys put the ROMs (Hermite table, program) and part of the microcode in `SPX9` BSRAMs. In the GW5A, these BSRAMs cause hold violations; the `DPX9B` BSRAMs do not.
- **Resolution:** ROMs in logic with `(* rom_style = "logic" *)` **on the `case`** (on the port it has no effect); the microcode with a dual-port wrapper.

## F-10 · The core did not close timing (70 MHz)

- **Symptom:** the first synthesis of the core gave 70 MHz, against a target of 100.
- **Root cause:** four steps were in series in one cycle:
  - the decoding;
  - the register bank (64:1 multiplexer);
  - the rounding of `a24`;
  - `CLIP` (three 50-bit operations).
- **Resolution:** registered operands in the decoding, and `CLIP` in two steps: 140 MHz from nextpnr. This was not sufficient in the silicon: see F-11.

## F-11 · The silicon failed at 100 MHz, but nextpnr gave 132

- **Symptom:** on the board, the plate gave the first sample at half its value. In simulation, in the synthesis and in the synthesized netlist, the result was the same as the model.
- **Diagnosis**, step by step:
  1. We removed the multiplier with a 24-bit B as a cause: 300 products without error on the board.
  2. We removed the BSRAM in 2K × 9 mode as a cause: 0 errors on the board.
  3. We simulated the Yosys netlist: it was the same as the model, thus the synthesis was correct.
  4. A minimum program with the same calculation operated correctly on the board. The failure was related to the placement.
  5. **Decisive test:** we changed only the PLL divider in the JSON after routing, without a new placement. At 50, 72.7, 80 and 88.9 MHz it operated correctly; at 100 it did not. The cause was timing.
  6. With the same method, the DSP operated correctly up to 160 MHz. The inferred BSRAM failed above 100 MHz, with 117 MHz from the static analysis.
- **Root cause:** the nextpnr timing model for the GW5A is optimistic by approximately 30 %. This is mostly true for the BSRAM in *bypass* mode (without an output register), the only mode that Yosys infers. It is also true for the logic after the BSRAM.
- **Resolution:**
  - `rtl/primitivas/bsram_bloque.v`: a manually instantiated BSRAM with its internal output register (`READ_MODE1 = 1`);
  - `rtl/primitivas/bsram_pipe.v`: large memories made of these blocks, with a registered multiplexer;
  - the multiplier output, registered two times; the ALU, in two stages; the `CHO` address, in three steps; the program loader, registered.
- **Measured result:** nextpnr gives 155 MHz. On the board: 9 of 9 perfect captures at 100 MHz, 3 of 3 at 106.25 MHz and 2 of 5 at 114.3 MHz. The real maximum frequency is between 106 and 114 MHz: **a margin of minimum 6 %**. This is small for a pedal that becomes hot. The target is more than 20 % when we design the sequencer again (before Phase 06).
- **Cost:** the cycles per sample increase from 661 to 1,258 (plate) and from 840 to 1,601 (shimmer), of 2,048.
- **Lesson:** the nextpnr analysis is not sufficient. Measure the margin on the board: change only the PLL divider on the same routing (ADR 0011).

## F-12 · A test of the memory clear found nothing

- **Symptom:** the test also passed with the memory clear disabled.
- **Root cause:** with the long lines of the plate, the old data comes back to a read only after thousands of samples.
- **Resolution:** a program with a delay of 8 samples on 9 words. It fails without the memory clear and passes with it.
- **Lesson:** make sure that each new test fails when the code is incorrect.

## F-13 · The first line of the dump was lost

- **Symptom:** 4,095 of 4,096 samples arrived, and all of them moved by one position.
- **Root cause:** the BL616 keeps bytes from a previous design. `reset_input_buffer()` empties only the PC buffer, and the first line arrived attached to those old bytes.
- **Resolution:** `scripts/hil_nucleo.py` discards the data that arrives during 0.3 s before it asks for the capture.

## F-14 · apicula 0.32 does not pack BSRAM without initial contents

- **Symptom:** `gowin_pack` stops with `IndexError` in `write_gw5_bsram_init_map`, and it makes an incomplete bitstream.
- **Root cause:** if no BSRAM in the design declares `INIT_RAM_xx`, apicula fails. This occurred when we instantiated all the blocks manually.
- **Resolution:** `bsram_bloque.v` declares the 64 initialization words at zero.
- **Lesson:** examine the exit code of `fpga.sh`; a `.fs` file can exist although the packing failed.

## F-15 · The read-ahead failed in the silicon at 100 MHz

- **Symptom:** with the read-ahead of the microcode, the plate was the same as the model in simulation. On the board it failed at 100 MHz, always from sample 924. With the same routing it operated correctly at 88.9 MHz and lower. nextpnr gave 157 MHz.
- **Diagnosis**, step by step:
  1. The design of `main` continued to pass at 100 MHz on the same day: the board had not changed.
  2. The measurements on the board removed these causes: the 50-bit carry chain, the saturated addition, the BSRAM alone, the DSP and the clock routing. The Yosys `-nodffe` option has no effect on the GW5A.
  3. Sample 924 is the sample where the plate tail reaches the long taps of the memory: there the memory starts to give values that are not zero. This is why the failure "was related to the data".
  4. **New tool:** the `hil_nucleo` top records the core trace (command `T`): the pc and the ACC at each change of the ACC. `scripts/margen_reloj.py --traza` compares the trace with the model and shows which instruction fails first.
  5. With the trace, each routing failed at a different location. These operations failed: the delay memory read (`RDA` gave 0: an incorrect address), the ALU addition (bit 25) and the multiplier (`MULX`).
  6. The placement of the carry chains had no breaks. There was no broken path.
- **Root cause:** nextpnr overestimates the speed of **all** the design on the GW5A, by a factor of 1.45 to 1.5. Each routing fails on the path with the smallest margin. The BSRAM paths are the worst: one address must go in one cycle to 38 blocks across the chip, and a multiplexer has 38 outputs.
- **Resolution:**
  - pipelined `bsram_pipe` (`GRUPO = 8` in the delay memory):
    - one copy of the address for each group and for each block (`registro_copia`, which Yosys does not merge);
    - the output of each block, registered near the block;
    - registered multiplexers for each group.
  - The read increases from 3 to 7 cycles. The core waits `LAT_MEM = 9` only in `RDA` and `CHO`.
  - Register bank in two levels: 8 candidates registered in each cycle, and the selection in `E_DECO`. The microcode word is registered again before the decoding.
  - The physical memory address uses three additions in parallel, and `puntero ± P` values that decrease with the pointer.
  - The multiplier uses the internal `PREG` register of the DSP.
- **Measured result** (nextpnr gives 154 MHz for this routing): 100 MHz, 4 of 4; 114.3 MHz, 2 of 2; **120 MHz, 4 of 4**; 125 MHz, 3 of 4; 133.3 MHz, 0 of 1. **A margin of minimum 20 %**, against 6 % in Phase 05.
- **Cost:** approximately 3,100 more flip-flops (LUT4 in the nextpnr report: from 8,204 to 11,490, because of the pass-through LUTs). The cycles per sample decrease less than expected: shimmer 1,514 (before 1,601), plate 1,195 (before 1,258), freeze 1,313 (before 1,393). Approximately 14 cycles per instruction: the wait for the result of each instruction is still the largest cost.
- **Lesson:** when the silicon fails and nextpnr does not, find the instruction on the board (the trace) before you change the design. Memories that use half of the chip need local copies of the address and registered outputs near each block. To measure between 114.3 and 133.3 MHz, `margen_reloj.py --mdiv` also changes the VCO.

## F-16 · Large simulations did not compile with the pip verilator

- **Symptom:** `c++: error: Vtop__pch.h.fast: linker input file not found`, only in large designs (`hil_nucleo` with the trace).
- **Root cause:** the `verilated.mk` of the package leaves the variable `CFG_CXXFLAGS_PCH_I` empty. Its correct value is `-include`. When verilator divides a large design into many files, it uses a precompiled header, and g++ receives it as an input file.
- **Resolution:** `sim/conftest.py` adds `CFG_CXXFLAGS_PCH_I=-include` to `MAKEFLAGS`.
- **Lesson:** a compilation failure that occurs only when the design becomes larger is usually in the tool configuration, not in the code.

## F-17 · The velvet noise diffuser was not better than the allpasses

- **Symptom:** we tested a hall with a velvet noise diffuser (24 taps in 50 ms) instead of its 4 input allpasses.
  - The tail was **less** dense: 10 % of significant samples, against 28 %.
  - It had a higher crest: 12.9 against 8.8.
  - With 4 lines instead of 8, it was also the tail with the most color in the catalog: 6.4 between octave bands, against 1.9 for the plate.
- **Root cause:** a chain of allpasses gives an infinite response that becomes denser over time. Velvet noise gives only as many pulses as it has taps. In SOFIFI each tap is an `RDA` of 19 cycles. The 100 taps necessary for the same density cost approximately 1,900 cycles, and they do not fit together with the network.
- **Resolution:** we do not publish the program. The hall (8-line network with Householder) covers the Phase 03 roadmap (item 5).
- **Lesson:** measure the property that you promise (density, color) before you name the program. An algorithm that operates well on a PC is possibly not the best when each memory read costs 19 cycles.

## F-18 · Four programming failures in the Phase 06 catalog

- **Symptom:** before publication, the acoustic tests found:
  1. an autopan, a tilt and a duty cycle that did not reach their limit;
  2. a slicer that never closed with pot1 = 1;
  3. a compressor with a gain that went across 0 and down to −1;
  4. four delays with the same fingerprint.
- **Root cause**, in sequence:
  1. `rdax potN, C` with C > 1 followed by `sof`: `SOF` uses the ACC after it is **saturated** to ±1 (a24), thus 2·pot never went above 1.
  2. `1 − pot` with pot = 0.99999988 and D = 0.99997 gives −0.00003: a `skp gez` did not jump.
  3. The loop subtracted the excess linearly (an integrator), while the envelope, which decreases slowly, stayed high.
  4. In 0.1 s of impulse, only the dry signal was audible: the echoes arrived later.
- **Resolution:**
  1. Multiply inside the `SOF` (`rdax pot, 1.0` and `sof 1.999, −1.0`).
  2. Unconditional jumps (`skp gez|neg`) when the branch does not depend on the sign.
  3. A decrease proportional to the gain itself: exponential, it never goes across 0.
  4. Longer fingerprints, and a test that requires different fingerprints between programs.
- **Lesson:** in the core, the ACC is wide, but each instruction that reads a24 (`SOF`, `WRAX`, `MULX`, `RDFX`) saturates. A test that measures the limit of the control finds these failures; a test that measures the center does not.

## F-19 · With RDAA and WRAA, the silicon failed at 114 MHz in the first sample

- **Symptom:** the core with `RDAA` and `WRAA` was the same as the model in simulation and on the board at 100 MHz. At 114.3 MHz it always failed, from sample 0. In Phase 06, the same plate passed at 120 MHz. nextpnr gave 157 MHz.
- **Diagnosis:**
  1. The trace (`margen_reloj.py --traza`) gave entry 2: board pc = 8, model pc = 4.
  2. The board ACC in that entry was the model ACC at pc = 8. Thus `rdax tmp` (pc 3 and pc 5) gave 0 both times.
  3. `wrax tmp` (pc 2) did not write the register, or the read failed. In sample 0 the memory does not give data yet: the failure was on a control path.
  4. In the routing, the 24 bits of `reg7` (`tmp`) were spread across all the chip (x from 12 to 53). The control (`estado`, `es_wrax`) was at x = 51, and `a24` at x from 12 to 21.
- **Root cause:** the `WRAX` write decoded `rg` and the state conditions in the same cycle as the write. That net goes to the 1,536 flip-flops of the register bank, which are spread across all the chip. The design became larger in Phase 07, the placement changed, and that path became the path with the smallest margin.
- **Resolution:**
  - Register bank write in two stages. `E_EJEC` registers a 64-bit mask and the data. In the next cycle, each register is written with its bit of the mask. This costs no cycles: the next read occurs some cycles later.
  - The `RDAA` subtraction `M[i+1] − M[i]` is registered before the multiplier (rule of F-11). `RDAA` increases from 26 to 27 cycles.
- **Measured result** (nextpnr gives 144 MHz for this routing): 100 MHz, 2 of 2; 114.3 MHz, 2 of 2; 120 MHz, 3 of 3; **125 MHz, 3 of 3**; 133.3 MHz, 1 of 1. In Phase 06 the results were 125 MHz, 3 of 4, and 133.3 MHz, 0 of 1.
- **Lesson:** a register that writes to all the register bank goes across the chip, the same as a memory address. Do the decoding in one cycle and the write in the next cycle. nextpnr decreased from 157 to 144 MHz and the board result became better: you cannot use the nextpnr value to compare two routings.

## F-20 · The clear of the absolute region did not clear two words

- **Symptom:** the test `absoluta_igual_al_modelo` failed at sample 67 when it ran after a different test. When it ran alone, it passed.
- **Diagnosis:**
  1. At sample 67, `rdaa pe, 0.5, 32700` reads index 32,767 of the region. The model reads 0. The RTL read a value from the previous test.
  2. The cocotb filter is a regular expression: `igual_al_modelo` also selected `absoluta_igual_al_modelo`. Thus the test ran after each program, with data in the memory.
- **Root cause:** in `E_BORRAR`, `mdir_w` comes from a register, but the absolute mode came directly from `borrar_abs`. The mode was one cycle before the address. The last circular word was written in the region, and the last word of the region was written in the circular area.
- **Resolution:**
  - `mabs_borrar` is registered on the same clock edge as `mdir_w`.
  - The test has the new name `absoluta_como_el_modelo`. Before the clear, it writes data to the limits of the region with `WRAA`. With the old failure, the test fails.
- **Lesson:** register the signals that go with a registered address together with that address. A test of the memory clear needs a memory with data in it. The simulation starts with the memory at zero, so the clear is not tested (as in F-12).

## F-21 · In marea, the software LFO stayed at +1

- **Symptom:** in the `marea` test, the right tail was approximately ten times quieter than the left tail, and neither tail made waves.
- **Diagnosis:** the left gain was 1 and the right gain was 0.1 in all samples. Both gains come from the LFO: the LFO was always at +1.
- **Root cause:** the program rounded the triangle with `CLIP` and wrote the result into `tri`. `tri` is the state of `comun/lfo_triangulo.sasm`. `CLIP` has a slope of 1.5 at the origin: each sample pushed the value towards 1, and the value stayed there.
- **Resolution:** the rounded value goes into a different register (`ola`). Only the common block writes `tri`.
- **Lesson:** do not write the state register of a common block outside the block. Put the values that you calculate from it into a different register.

## F-22 · The shoegaze program was five times louder than the plate

- **Symptom:** the `shoegaze` demo had an RMS level of 0.13; the plate demo had 0.027. The acoustic test passed.
- **Diagnosis:** with saturation, the tail is clipped near ±1. The plate keeps the tail near ±0.1. The gain of ×16 raises the tail to the limit.
- **Root cause:** the output gain was fixed (0.5). The test measured the compression, not the level against the plate.
- **Resolution:** the output decreases from 0.6 to 0.1 when pot3 increases. With the mix at half, the level stays within ±25 % of the plate across the full range of the knob.
- **Lesson:** a jump in volume when you change the program is a risk (SECURITY.md). Compare the level of each new program with the plate before publication.

## F-23 · A chain with saturation was six times louder than the plate

- **Symptom:** the demo of «Fuzz en la nube» (`saturacion` → `cloud`) clipped: a peak of 1.03 and an RMS level ten times that of the plate.
- **Diagnosis:** the «nivel» (level) knob of `saturacion` was fixed at 0.6 and the mix at 1. With a soft guitar, the saturation raises the signal to the limit; `cloud` receives it at almost full scale.
- **Root cause:** the lesson of F-22 was applied to the `shoegaze` program, but there was no level test for the chains. A program that is correct alone can be wrong in a chain.
- **Resolution:** «nivel» at 0.1 in that chain and a gain of 0.2 in «Sustain en la placa». New test `ninguna_cadena_salta_de_volumen`: with a soft note and a loud note, no chain is more than twice as loud as the plate.
- **Lesson:** make a test from each rule that comes from a failure. If the rule stays in a note, the same failure comes back by a different path.

## F-24 · The microcode queue took the last BSRAM

- **Symptom:** with the pipelined core (ADR 0014), nextpnr stopped: «no BELs remaining to implement cell type 'DP'». The simulation passed.
- **Diagnosis:** the resource report gave 56 BSRAM of 56. One more BSRAM came from the microcode fetch queue (8 × 54 bit).
- **Root cause:** Yosys changes each array that is read by index into BSRAM, also a small array. In `hil_nucleo`, the capture already uses all the free BSRAM.
- **Resolution:** `(* ram_style = "logic" *)` on the queue. Then the second pass made the queue smaller: 4 words.
- **Lesson:** give each new array in the RTL its `ram_style` from the start. In this chip, each BSRAM is delay memory.

## F-25 · Three failures of the SD controller, found in simulation

- **Symptom 1:** the loader rejected all banks with the reason «header».
  - **Cause:** the magic value was compared with the string `"SOFIFI\0\0"`. In Verilog, `\0` is not a reliable escape, and the constant did not have the 8 expected bytes.
  - **Resolution:** the magic value is the constant `64'h534F_4649_4649_0000`.
- **Symptom 2:** block reads failed with the reason «token» at 25 MHz, and worked at the slow clock.
  - **Cause:** MISO goes through two synchronisation flip-flops. With a half period of SCK of 2 cycles, the bit arrived late for the sample.
  - **Resolution:** the fast half period is a minimum of 4 cycles (12.5 MHz). The parameter tells this.
- **Symptom 3:** the program arrived correctly at the core, but with the memory and the LFOs of a different program.
  - **Cause:** the microcode blocks wrote over the saved bytes of the metadata.
  - **Resolution:** the loader saves only the bytes of the header and of the metadata.
- **Lesson:** the card model in cocotb and the images from `sofifi banco` found the three failures before the board. Write constants of more than one byte in hexadecimal.

## F-26 · Four fixed-point traps in batch 9 of the catalogue

The acoustic tests of the new programs found four failures before publication.

- **The FV-1-form allpass saturates with poles near 1** (`desplazador`).
  - **Symptom:** the echo came out at one quarter of its level, and the opposite sideband fell only 31 dB.
  - **Cause:** the RDA + WRAP form keeps a state that grows as 1/(1 − k). With k = 0.998, the 18-bit word saturates.
  - **Resolution:** direct form I: each stage keeps its output and the next stage reads it as x[n−1]. The opposite sideband falls 64 dB.
- **An RDAX coefficient larger than 1 saturates before SOF** (`desplazador`).
  - **Symptom:** the width knob and the footswitch did nothing.
  - **Cause:** SOF reads a24, the ACC saturated to [−1, 1). `rdax pot, -2.0` is already −1 before the addition.
  - **Resolution:** `rdax pot, -1.0` and then `sof 1.999, 0.99999`.
- **WRAX saturates the register below 1** (`arcoiris`).
  - **Symptom:** a regeneration of 1.1 stayed at 0.99999 and the loop did not oscillate.
  - **Resolution:** the gain larger than 1 goes in the coefficient (`rdax fb, 1.1`), not in a register.
- **A fractional loop length stops the loop** (`erosion`).
  - **Symptom:** with erosion 0, the loop lost treble and level on each pass.
  - **Cause:** the read fell between two samples. The interpolation is a low-pass filter, and it applies once on each pass.
  - **Resolution:** the length is rounded to whole samples. With erosion 0, the loop repeats bit for bit.
- **Lesson:** in fixed point, the ACC and the registers saturate to [−1, 1). In a loop with feedback, a hidden filter is raised to the number of passes. The tests measure the level and the exact repetition, not only that «it makes a sound».

## F-27 · Small constants, control loops and a blind fingerprint in batch 10

- **A constant smaller than 1/32,768 does not fit in the D operand of SOF** (`violin`).
  - **Symptom:** the age of the note and the slowest ramp did not move.
  - **Cause:** D is S2.15: its smallest step is 1/32,768. 1/fs is smaller.
  - **Resolution:** the constant comes from the product of two SOF, or from a ×64 factor that then multiplies a register of 1/64.
- **A low-pass filter with a very small coefficient stops before it arrives** (`arco`).
  - **Symptom:** the output fade stayed at 0.002 and did not get to 0.
  - **Cause:** with RDFX and a coefficient of 2^-15, the step of each sample rounds to 0 near the target.
  - **Resolution:** a fixed linear term and a floor at 0.
- **An automatic gain control gets stuck or stops the loop** (`arco`, `oscilador`).
  - **Symptom:** in `arco`, the gain stayed at 0 for ever. In `oscilador`, the loop stopped after the first note.
  - **Cause:** a multiplicative gain that gets to 0 does not go up again. And a strong attack with a slow recovery pushed the gain below the value that keeps the oscillation.
  - **Resolution:** a floor for the gain (1/256). In `oscilador`, a softer attack and a recovery of 85 ms.
- **A fingerprint with neutral knobs does not tell programs apart** (`dinamica`).
  - **Symptom:** `dinamica` and `freeze` had the same fingerprint.
  - **Cause:** the fingerprint test sets pot3 = 0.5, which in `dinamica` is «no dynamics»: the program is then a plate with the CLIP tank, the same as `freeze` without the footswitch.
  - **Resolution:** `POTS_HUELLA` gives `dinamica` a depth of 0.9, with a note of 0.6 s.
- **Lesson:** long time constants do not fit in one instruction: build them. A control loop needs a floor. A fingerprint is useful only if the stimulus and the knobs get to the effect.

## F-28 · The minimum speed of phaser and filtro was 0, and three traps in batch 11

- **A constant that rounds to 0** (`phaser` and `filtro`, published in Phase 06).
  - **Symptom:** with pot0 = 0, the sweep did not go at 0.05 Hz: it stopped. The author of `estelar` saw it when writing the same calculation.
  - **Cause:** `sof 1.0, 4*0.05/fs` asks for a D of 4·10⁻⁶. The step of D is 1/32,768 ≈ 3·10⁻⁵, and the value rounded to 0 without a warning.
  - **Resolution:** the speed is calculated ×64 and then divided (`sof 1/64, 0`). **The assembler now rejects** a coefficient or a D that is not 0 and rounds to 0. When it assembled the 63 programs, only `filtro` failed.
- **Feedback from the sum of many taps does not work** (`enjambre`, `probabilidad`, `dados`).
  - **Symptom:** the tail died in less than 0.5 s, or the loop oscillated and saturated.
  - **Cause:** the sum of N taps has gain peaks of N at some frequencies and a much lower average gain.
  - **Resolution:** the loop comes from one tap only, the longest.
- **The cost counts all the SKP branches** (`probabilidad`, `dados`).
  - **Symptom:** a counter for each tap or a three-way choice used more than 2,000 cycles.
  - **Resolution:** one counter only, or two ways for each tap.
- **An SKP that does not jump leaves the comparison in the ACC** (`dados`).
  - **Symptom:** the output saturated without input.
  - **Resolution:** a `clr` at the start of the branch.
- **Lesson:** a rule that a person can forget goes in the assembler. Design a feedback loop with its worst gain, not with the average.

## F-29 · Five modulation and level traps in batch 12

- **The `media` option of CHO does not invert a SIN LFO** (`dimension`).
  - **Symptom:** the L + R sum wobbled the same as each channel: there was no antiphase.
  - **Cause:** `media` only moves the RAMP and the window by half a turn; the sine does not change. The model and the RTL agree.
  - **Resolution:** two SIN LFOs with the same speed; the second line uses a negative `depth`.
- **A chorus centred at 8 ms makes a comb with the dry signal** (`orilla`).
  - **Symptom:** at 196 Hz the level fell to 0.22 times that of the plate.
  - **Cause:** the dry signal and the voice at 50 % cancelled near 187 Hz.
  - **Resolution:** the delay goes from 3 to 15 ms.
- **An asymmetric triangle LFO stays at the edge** (`vibe`).
  - **Symptom:** with the rise faster than the fall, the sweep stopped at +1.
  - **Cause:** the fall step did not move the LFO out of the edge zone, and the direction changed on each sample.
  - **Resolution:** the edge is checked on tri·direction. `comun/lfo_triangulo.sasm` does not change.
- **A register shared by two filters erases their state** (`baldosa`).
  - **Symptom:** with decay at maximum, the tail fell 36 dB in 0.4 s.
  - **Cause:** the allpass wrote its output into the register of the low-pass filter.
  - **Resolution:** each filter has its own register.
- **A compressor and an expander that do not match** (`eco_casero`).
  - **Symptom:** each note started with a peak of 2.4 times, and with feedback at maximum the loop went out of control.
  - **Resolution:** both use the same mean detector, and the compressor uses feedback (1/envelope without division).
- **Lesson:** test a modulation effect on the mono sum and at low frequencies, not only on one channel. Each filter state needs its own register.

## F-30 · Detectors, seams and read limits in batch 13

- **The attack detector of `comun/compuerta.sasm` fires on low notes** (`tartamudeo`).
  - **Symptom:** a held note of 82 Hz fired 12 times a second, and the notes of an arpeggio did not fire.
  - **Cause:** the fast envelope has much ripple on low notes. The rule «fast > 2·slow» is not true while the previous note sounds.
  - **Resolution:** a peak detector with MAXX (fall of approximately 30 ms) and the rule «peak > 1.5·slow + threshold». The common block does not change.
- **A read head gets to the seam of the ring** (`frenada`).
  - **Symptom:** with a long echo and a long brake, a click on footswitch release.
  - **Cause:** the write head got to the braking read head, which read the point where the ring turns.
  - **Resolution:** a window turns that head off near the write head.
- **A variable speed needs a division** (`resbalon`).
  - **Cause:** the window phase moves (1 − v)/L on each sample, and the ISA has no division.
  - **Resolution:** a reciprocal that corrects itself on each sample: r ← r + 2·(1/32 − L·r).
- **A CHO reaches only 2·E samples from its base** (`dos_ecos`).
  - **Symptom:** the tap at 1.5 times the time did not get to 0.82 s.
  - **Cause:** the excursion E of an LFO is a maximum of 16,384 samples.
  - **Resolution:** two taps with two LFOs of different base and a crossfade between them.
- **Lesson:** validate a common block with low notes and with arpeggios. Each read head of a ring needs its window near the write head.

## F-31 · Loops, periods and detectors in batch 14

- **A pitch spiral does not sustain** (`espiral`).
  - **Symptom:** with the footswitch and a feedback of 1.9, the tail stopped in 1-2 s.
  - **Cause:** the shifter in the loop moves the energy out of the band on each pass. The gain alone does not return it.
  - **Resolution:** with the footswitch, a part of the signal goes around the shifter in the loop. The CLIP sets the ceiling.
- **A write head with a period of 32,767** (`compas`).
  - **Symptom:** a read `wp − d` that crosses the wrap reads a delay that is one sample short.
  - **Cause:** RDAA masks to 32,768 samples, and the head goes back to 0 at 32,767.
  - **Resolution:** the head goes through [0, 1) with a period of exactly 32,768. `granular` already had a period of 32,768 (checked in F-32). `looper` had a different failure: see F-32.
- **The attack detector triggers many times on a low note** (`swell_ritmico`).
  - **Cause:** the peak falls 8 % between half periods, and the rule "peak > 1.5·slow + threshold" crosses 0 many times.
  - **Resolution:** a dead time of approximately 60 ms after each attack.
- **A sustained note and its echo make a comb** (`arpegio`).
  - **Symptom:** the +4 voice was 65 % lower at 330 Hz than at 262 Hz.
  - **Resolution:** the echo lasts one step, and only the echo goes into the reverb.
- **A coefficient that a knob changes cannot go in RDFX** (`semilla`).
  - **Resolution:** the low-pass uses MULX with a register, as in `cloud`.
- **Lesson:** a loop with transposition needs a path without transposition. A head that wraps has the period of the mask.

## F-32 · The inverted dry signal of the mix and the wrap of the looper at ½×

- **`comun/mezcla.sasm` gives the dry signal inverted when the mix is at maximum.**
  - **Symptom:** with pot2 = 1, the output had the dry signal at −60 dB with the phase inverted.
  - **Cause:** `sof 1.0, 0.999` gives kdry = 0.999 − pot2, which is −0.001 when pot2 = 1.
  - **Resolution:** `sof 1.0, 1.0`. D of SOF is S2.15 and gets to 1.0. The fingerprints of 74 programs change.
- **At ½×, the looper interpolates the last sample with a cell that is not in the loop** (`looper`).
  - **Symptom:** at ½×, the sample between the end and the start of the loop was M[L−1]/2, not (M[L−1] + M[0])/2. This was a click on each pass.
  - **Cause:** RDAA interpolates between cell L−1 and cell L. Cell L is not in the loop.
  - **Resolution:** on each sample, the program copies cell 0 into cell L (RDAA and WRAA, 2 instructions).
- **F-31 said that the wrap of `granular` was incorrect.**
  - **Cause:** the review read the comparison with 32,767 as the end of the wrap. The head writes cell 32,767 before it goes back to 0.
  - **Resolution:** the model shows that `granular` writes all 32,768 cells. Nothing changes.
- **Lesson:** a read that interpolates needs the cell after the end of the loop. Check a statement from a subagent with the model before you record it.

## F-33 · The nextpnr clock result depends on the seed

- **Symptom:** after a change to one constant in the ROM of `plate`, `nucleo_placa` did not close timing: 95.41 MHz for 100.
- **Cause:** the nextpnr placement depends on the seed. With the same netlist, we measured these values:

  | Seed | Fmax |
  |---|---|
  | default | 95.41 MHz |
  | 1 | 98.77 MHz |
  | 2 | 109.41 MHz |
  | 3 | 112.10 MHz |
  | 4 | 107.99 MHz |

- **Resolution:** if nextpnr fails only the clock, `scripts/fpga.sh` tries seeds 2, 3 and 4 (`SEMILLAS_PNR`). The first try does not change, and the script tells which seed closes timing.
- **The resources are not noise:** `nucleo_placa` goes from 11,709 to 11,982 LUT4 and from 1,208 to 1,242 ALU. In that top, Yosys removes the bits that the ROM never uses. The new constant uses bit 15 of the D field (RAT-11 and RAT-12).
- **Lesson:** a clock failure after a change that does not touch the logic is placement noise. Measure the real margin on the board (ADR 0011).
