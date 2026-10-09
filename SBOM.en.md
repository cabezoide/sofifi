<!-- i18n: fuente=SBOM.md sha=a282b2880c99 estado=al_dia -->
# SBOM · SOFIFI components

This document tells which parts make the pedal inside and which tools build it. Each part has a simple explanation: what it does and what it gives to the system. The technical details (resources, latencies, history by phase) are in `docs/arquitectura_fpga.en.md`.

## The idea in one sentence

The FPGA contains a **small custom audio processor** (the core). Each effect (plate, shimmer, freeze…) is a **program**. The processor runs that program 48,828 times each second, one time for each audio sample.

## FPGA components

### Clocks

| Component | What it does, in simple words | What it gives |
|---|---|---|
| **PLL** (`pll_100`) | Changes the 50 MHz clock from the board crystal into a 100 MHz clock. | Gives the core two times the speed: 2,048 work steps for each audio sample. |
| **Sample generator** | Gives a signal every 2,048 clock cycles. | Sets the audio rate: exactly 48,828 samples each second. |

### The DSP core

| Component | What it does, in simple words | What it gives |
|---|---|---|
| **Microcode** | Memory with the program instructions (up to 2,048). | You can change the effect without a change to the hardware: load a different program. |
| **Sequencer** | Reads the instructions and tells each part what to do. It starts an instruction before the previous one ends. It waits only if it needs a result that is not ready yet (ADR 0014, Spanish). | It is the "conductor" of the core. Thus, the programs use 1.6 times fewer cycles. |
| **Register bank** | 64 cells that keep numbers: inputs, outputs, potentiometers and program variables. | It is the "workbench" of each effect. |
| **Multiplier** (DSP block) | Multiplies two numbers in one step. | Almost all audio operations are multiplications: volume, filters, mixes. |
| **ALU** | Adds, compares and saturates (prevents overflow of the sound). | Combines the results and keeps them in the accumulator. |
| **Accumulator (ACC)** | A 48-bit register that adds the products. | High precision: it prevents rounding noise in long tails. |
| **Delay memory** (BSRAM) | Keeps the audio of the last ~0.9 s, like a tape loop. It has groups of blocks, and each group has its own copy of the address. With `RDAA` and `WRAA`, 32,768 words work as a fixed tape: the recorded audio does not move away. | It is the base of all reverbs and delays: you hear the past of the sound. The groups give timing margin on the real chip. The fixed part makes the looper and the granular possible. |
| **LFO ×4** | Slow oscillators (sine, random, ramp). | They move the read positions in the memory: chorus, reverb modulation and the pitch shift of the shimmer. |
| **Hermite ROM** | Fixed table of 256 × 4 coefficients. | Lets the core read the memory "between samples" without noise: smooth modulation. |
| **Soft curve** | A cubic saturation, without hard edges. | Limits the sound in a musical way (`CLIP`) and gives shape to the sine LFO. |

### Input, output and tests

| Component | What it does, in simple words | What it gives |
|---|---|---|
| **UART TX / RX** | Serial port to the PC, through the USB of the board. | Lets you talk to the FPGA: request tests and receive results. |
| **Program loader** | Copies a program from a fixed memory into the microcode at startup. | In the test tops, it loads the plate, the looper or the program of `make hil`. |
| **Capture and CRC-32** (tests only) | Records 4,096 samples at real speed and sends them with a check code. | Shows that the hardware sounds **exactly** the same as the PC model. |
| **Trace** (tests only) | Records which instruction runs and which value it puts in the accumulator. | If the chip fails, it tells you the instruction. Then you know which part to repair. |
| **Frequency meter** (tests only) | Counts the cycles of one clock during one second of a different clock. | It confirmed that the PLL and the sample rate are exact. |

### The microSD (Phase 08, in progress)

| Component | What it does, in simple words | What it gives |
|---|---|---|
| **SD controller** (`sd_spi`) | Talks to the card through SPI: it starts the card and reads blocks of 512 bytes. It does not write to the card. | Gives access to the program library without a file system, which is expensive and fragile. |
| **Bank loader** (`cargador`, `carga_sd`) | Reads a slot of the card two times. The first time, it only checks. The second time, it writes the program into the core. | A damaged program does not load. If the first read fails, the core keeps the previous program. |
| **SD test** (`prueba_sd`, tests only) | Loads slots when the PC requests them, and tells the PC what it read. | Checks that the card gives the same data as the model. The test with the real card is not done yet. |

### Chip primitives (physical parts of the GW5A)

| Primitive | Quantity used | Function |
|---|---|---|
| BSRAM (18 Kbit blocks) | 48 of 56 in the core | delay memory and microcode |
| DSP (MULTALU27X18) | 2 of 28 | the multiplier |
| PLLA | 1 of 6 | the 100 MHz clock |
| LUT4 and flip-flops | ~54 % and ~31 % (test top `hil_nucleo`) | all the logic, and the copies that give clock margin |

## Software tools

`make install` (pip) installs all the tools. All of them are free software.

| Tool | Version | License | What it does |
|---|---|---|---|
| Yosys (YoWASP) | 0.69 | ISC | Translates the Verilog into logic gates (synthesis). |
| nextpnr-himbaechel-gowin (YoWASP) | 0.11.1 | ISC | Places and connects those gates in the chip. |
| apicula | 0.32 | MIT | Makes the GW5A bitstream. |
| openFPGALoader | 1.1.1 | Apache-2.0 | Loads the bitstream into the board through USB. |
| verilator | 5.48 | LGPL-3.0 or Artistic-2.0 | Simulates the Verilog. We use it only as a tool; we do not copy its code (ADR 0002). |
| cocotb | 2.1 | BSD-3-Clause | Writes the simulation tests in Python. |
| pyserial | 3.5 | BSD-3-Clause | Talks to the UART of the board. |
| soundfile | 0.12 | BSD-3-Clause | Writes the demos in Ogg Vorbis. It uses libsndfile (LGPL-2.1) as a library, and we do not copy its code (ADR 0002). Optional: `pip install -e '.[demos]'`. |
| Python + numpy | 3.12+ / 2.x | PSF / BSD | The bit-exact model, which is the reference for all the system (ADR 0003). |

The minimum versions are in `pyproject.toml`. The traps of each tool are in `fails.en.md` and `rtl/AGENTS.md` (Spanish).
