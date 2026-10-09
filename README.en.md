<!-- i18n: fuente=README.md sha=0f404692c52a estado=al_dia -->
# SOFIFI — Soundscapes On FPGA: Integrated Filters & Impulses

*In Spanish: Sintetizador de Ondas y Filtros Inmersivos en FPGA Integrada.*

**Languages:** [Español](README.md) (source) · English · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

![SOFIFI: the logo and the pedal face, with the OLED, six knobs and two footswitches](docs/img/en/portada.png)

SOFIFI is an open-source ambient guitar pedal. It runs on a **Sipeed Tang
Primer 25K** FPGA (Gowin GW5A-LV25). Each effect is a text program that a
custom DSP core executes.

**Version:** `0.7` (the version is the last closed phase; see `docs/fases/estado_fases.csv`).

## Status

| Item | Status |
|---|---|
| Library | **86 programs and 1,032 presets** in 8 families (Phase 07) |
| Two effects at the same time | **24 chains**: 18 fit today and 6 wait for the SDRAM (`presets/cadenas.toml`, ADR 0013) |
| Match with the model, in simulation | all 86 programs and the 18 chains that fit give in the RTL the same bits as the model |
| Match with the model, on the board | 50 of 50: 41 programs and 9 chains, with the Phase 07 core (MED-16, 2026-10-08) |
| Core | in-order pipeline (ADR 0014, Spanish): it uses 1.6 times fewer cycles; no errors on the board at 125 MHz (3 of 3) and at 133.3 MHz (2 of 2); it runs at 100 MHz |
| In progress | **Phase 08, microSD:** the bank, the SD controller and the `prueba_sd` top work in simulation. The test with the real card is not done yet (`docs/microsd.md`) |
| Audio with a guitar | **not yet**: the I2S codec is missing (Phase 11) |

## Listen to the effects without hardware

1. Listen to the demos in `demo_examples/`. They are a synthetic guitar (an
   Em9 arpeggio) through each program, in Ogg Vorbis.
2. Process your own WAV with a preset:

```bash
.venv/bin/sofifi presets hall                      # lists the presets of one program
.venv/bin/sofifi render programas/hall.sasm guitar.wav out/hall.wav --preset "Catedral" --cola 6
.venv/bin/sofifi render programas/shimmer.sasm guitar.wav out/sh.wav --pot pot0=0.7 --pot pot3=0.6 --cola 6
.venv/bin/sofifi render programas/freeze.sasm guitar.wav out/fz.wav --preset "Congelar suave" --freeze 1.5:8 --cola 8
```

- `--preset` takes the knob values from `presets/banco.toml`. A later `--pot` changes one of them.
- `--freeze START:END` holds the footswitch between two times, in seconds.
- `--cola` adds seconds of silence at the end, so that you hear the tail.
- The input WAV can be 16, 24 or 32-bit, at any sample rate. The model
  resamples it to 48,828 Hz.

| Family | Programs |
|---|---|
| Reverb (26) | plate, plate_vivo, hall, blackhole, cloud, bloom, spring, chorale, resonador, gated, reverb_inversa, infinite, freeze, freeze_givens, shimmer, shimmer_quinta, shimmer_energia, shimmer_grave, shimmer_escondido, ensemble, marea, shoegaze, sostenido, dinamica, baldosa, semilla |
| Delay (21) | delay, cinta, bbd, pingpong, lluvia, ducking, reverse, bruma, tambor, oscilador, enjambre, probabilidad, dados, aureo, estelar, lata, deriva, eco_casero, dos_ecos, frenada, compas |
| Modulation (11) | chorus, flanger, phaser, tremolo, vibrato, slicer, armonico, desplazador, dimension, orilla, vibe |
| Pitch (8) | octava, armonizador, doblador, escalera, arcoiris, acople, arpegio, espiral |
| Dynamics (6) | compresor, puerta, swell, violin, arco, swell_ritmico |
| Looper (6) | looper, erosion, mosaico, relevo, resbalon, tartamudeo |
| Texture (5) | saturacion, lofi, ringmod, granular, viento |
| Filter (3) | autowah, filtro, ancho |

`docs/programas.en.md` tells what each program does, which knobs it has and
what it costs. `sofifi catalogo` generates it. The program and preset names
are in Spanish.

## How it works

- **Microcoded DSP core**, in the style of the Spin FV-1 and extended: up to
  2,048 instructions per sample, a 48-bit accumulator and cubic interpolation
  (ADR 0006). A new effect is a `.sasm` file; the RTL does not change.
- **All the audio in the FPGA BSRAM:** 43,008 words, approximately 0.88 s. The
  microSD card keeps presets and recordings. It cannot be the delay memory,
  because its write peaks are up to 250 ms (ADR 0004).
- **Looper and granular:** a region of 32,768 words (0.67 s) with absolute
  addresses. The circular pointer does not move it. `RDAA` and `WRAA` read and
  write it (ADR 0009). The SDRAM will give longer loops.
- **fs = 48,828 Hz:** a 100 MHz clock gives exactly 2,048 cycles per sample (ADR 0005).
- **Bit-exact reference model in Python.** The RTL must give the same bits as
  the model, sample by sample (ADR 0003).
- **Real cost:** the core is an in-order pipeline (ADR 0014, Spanish). An
  instruction waits only if it reads a result that is not ready yet, for
  example the ACC. A program uses 185 to 1,620 of the 2,048 cycles. `sofifi asm`
  gives the cycles of a program.

![Why choose SOFIFI? You can read it, change it and check it bit by bit; against the FV-1 it wins on instructions and sample rate, and it does not play with a guitar yet](docs/img/en/porque.png)

The full infographics are in `docs/infografias/`. The 2026 state of the art and
the roadmap are in `docs/investigacion/ESTADO_DEL_ARTE_2026.md` (Spanish).

## Getting started

1. Create the environment with the tools for the model, the gate and the FPGA:
   `make install`.
2. Install the pre-push hook of the repository: `make hooks`.
3. Run the full local gate: `make ci`.

`docs/SPEC_RAIZ.md` defines the work discipline. `AGENTS.md` is the map to
resume the project from zero. Both are in Spanish.

### EDA toolchain

`make install` installs with pip the full open toolchain: Yosys and
nextpnr-himbaechel-gowin (YoWASP), apicula, openFPGALoader, verilator and cocotb.

```bash
make sim           # cocotb testbenches of the RTL
make prog          # synthesizes hola_uart and loads it into the SRAM of the Tang Primer 25K
make uart          # reads the debugger UART (/dev/ttyUSB1) and requires "SOFIFI"
make esquematicos  # generates again the PDF schematics of the RTL
make hil HIL=hall  # loads a program or a chain into the board and compares it with the model
```

To program the board without sudo, you need the udev rule of the BL616
debugger (`0403:6010`, group `plugdev`). Install it one time, with the
instructions in `scripts/udev/99-tang-primer-25k.rules`.

### Optional tools

| Tool | Use |
|---|---|
| `shellcheck` | lint of the scripts (soft gate) |
| Node.js and chrome-headless-shell | schematics (`make esquematicos`) and infographic captures |

If a tool is missing, the gate says it (`NO CORRIÓ`, "did not run"). It does not give a false green.

## Hardware

| Part | Status |
|---|---|
| Tang Primer 25K + Dock | available |
| 64 GB microSD card and Sipeed PMOD TF module | available; the card test on the board is not done yet (Phase 08) |
| I2S codec (PCM1808 + PCM5102A or Digilent Pmod I2S2) | **missing** (Phase 11) |
| MCP3208 + potentiometers | missing (Phase 09; the Dock buttons are the footswitches) |
| 128×64 SSD1306 OLED | missing (Phase 10) |
| Guitar input buffer | missing (temporary: any pedal with a buffer) |
| Sipeed SDRAM module | future (for a long looper and a long granular engine) |

The phases that need missing hardware come last (09 to 12). Up to Phase 08,
the board and the microSD card are sufficient.

![The 13 phases: 8 closed, the next one and the ones that wait for hardware](docs/img/en/ruta.png)

## Documentation

| Document | Contents |
|---|---|
| `docs/programas.en.md` | the 86 programs: what they do, knobs, presets and cost |
| `presets/banco.toml` | the 1,032 presets |
| `docs/arquitectura_fpga.en.md` | the FPGA architecture and how it changes in each phase |
| `schematics/` | a PDF schematic of each RTL module, generated from the Verilog |
| `presets/cadenas.toml` | the 24 chains of two programs |
| `docs/microsd.md` | how to write the program bank to the microSD and test it on the board (Spanish) |
| `docs/EXTENDING.en.md` | how to add a program, a preset, a chain, an instruction, an RTL module or a gate |
| `BOM.en.md` | hardware shopping list, with links |
| `SBOM.en.md` | what each FPGA component does and which tools build it |
| `fails.en.md` | the failures found: symptom, cause, resolution and lesson |

## Scripts

The scripts in `scripts/` build, test and measure the project. The guide
[docs/scripts.md](docs/scripts.md) tells what each script does, when to use it
and which options it has.

## Languages

- Spanish is the source.
- The public and technical documentation has translations into English,
  Simplified Chinese and Japanese: this README, the infographics, the catalog,
  the demo and schematic guides, the architecture, `EXTENDING`, `BOM`, `SBOM`
  and `fails`.
- Each translation has a stamp with the fingerprint of the version that it
  translates. `scripts/check_i18n.py` stops a translation that says it is up to
  date when it is not (ADR 0007).
- The ADRs, the phase specs, the research and the maps for agents are in Spanish only.

## License

MIT (see `LICENSE`). Third-party code is ported only if it has a permissive
license, and each source is declared in `docs/terceros.yaml` (ADR 0002).
