<!-- i18n: fuente=README.md sha=6f681132315c estado=al_dia -->
# SOFIFI — Soundscapes On FPGA: Integrated Filters & Impulses

*In Spanish: Sintetizador de Ondas y Filtros Inmersivos en FPGA Integrada.*

**Languages:** [Español](README.md) (source) · English · [简体中文](README.zh-CN.md)

SOFIFI is an ambient guitar pedal (reverbs, shimmer, tape delays, freeze, granular)
implemented on a **Sipeed Tang Primer 25K** FPGA (Gowin GW5A-LV25).

**Version:** `0.3` (the version is the last closed phase; see `docs/fases/estado_fases.csv`).

> Status: **core primitives verified on the board** (Phase 03). The 27×18 DSP
> block, the 42 BSRAM blocks and the 100 MHz PLL work with the free toolchain.
> The bit-exact model lets you hear the plate, shimmer and freeze programs on a
> PC. There is no DSP core in RTL yet.
> The initial research is in `docs/investigacion/INVESTIGACION.md` (Spanish).

## Listening to the effects (no hardware needed)

```bash
.venv/bin/sofifi render programas/plate.sasm guitar.wav out/plate.wav --pot pot0=0.6 --pot pot2=0.4 --cola 4
.venv/bin/sofifi render programas/shimmer.sasm guitar.wav out/shimmer.wav --pot pot0=0.7 --pot pot2=0.5 --pot pot3=0.6 --cola 6
.venv/bin/sofifi render programas/freeze.sasm guitar.wav out/freeze.wav --pot pot2=0.5 --freeze 1.5:8 --cola 8
```

| Program | pot0 | pot1 | pot2 | pot3 | footswitch |
|---|---|---|---|---|---|
| `programas/plate.sasm` | decay | damping | mix | — | — |
| `programas/shimmer.sasm` | decay | damping | mix | shimmer | — |
| `programas/freeze.sasm` | decay | damping | mix | — | `--freeze START:END` (seconds) |

`demo_examples/` contains pre-rendered demos: a synthetic guitar (an Em9
arpeggio) run through the three programs. They are regenerated with
`scripts/generar_demos.py`.

The input WAV may be 16, 24 or 32-bit at any sample rate; it is resampled to
48,828 Hz. `sofifi asm` generates the microcode (`.hex` + `.json`). (`--cola` is
the tail length in seconds.)

## What will be built

- **A microcoded DSP core** in the style of the Spin FV-1, extended: 2,048
  instructions per sample, 48-bit accumulator and cubic interpolation (ADR 0006).
  Effects are *programs*, not RTL modules.
- **All audio in BSRAM** (about 0.9–1.4 s of delay lines). The microSD stores
  presets and recordings, but it cannot be used as delay memory (ADR 0004).
- **fs = 48,828 Hz**, with a 100 MHz system clock: exactly 2,048 cycles per sample
  (ADR 0005).
- **A bit-exact reference model in Python**, which is the oracle the RTL is
  validated against (ADR 0003).

## Getting started

```bash
make install    # creates .venv with the model and gate tooling
make hooks      # installs the versioned pre-push hook
make ci         # full local gate
```

The working discipline is in `docs/SPEC_RAIZ.md`; the cold-start map is in
`AGENTS.md` (both in Spanish).

### EDA toolchain (Phase 02)

`make install` installs the whole open toolchain through pip: Yosys and
nextpnr-himbaechel-gowin (YoWASP), apicula, openFPGALoader, verilator and cocotb.

```bash
make sim        # cocotb testbenches for the RTL
make prog       # synthesizes hola_uart and loads it into the Tang Primer 25K SRAM
make uart       # reads the debugger UART (/dev/ttyUSB1) and requires "SOFIFI"
```

Programming without sudo needs the udev rule for the BL616 debugger
(`0403:6010`, group `plugdev`); install it once following
`scripts/udev/99-tang-primer-25k.rules`.

### Optional tools (soft gates)

- `shellcheck`: script lint.

If a tool is missing, the gate says so (`WARN … NO CORRIÓ`); it does not fake a green.

## Hardware

| Part | Status |
|---|---|
| Tang Primer 25K + Dock | available |
| 64 GB microSD (PMOD TF) | available |
| I2S codec (PCM1808 + PCM5102A or Digilent Pmod I2S2) | **missing** (Phase 11) |
| MCP3208 + potentiometers | missing (Phase 09; the Dock buttons act as footswitches) |
| 128×64 SSD1306 OLED | missing (Phase 10) |
| Guitar input buffer | missing (temporary: any buffered pedal) |
| Sipeed SDRAM module | future (enables long looper and granular) |

Phases that need missing hardware are at the end of the plan (09 to 12), so up
to Phase 08 the board and the microSD are enough.

## Languages

Spanish is the canonical source. Translations carry a seal with the fingerprint
of the version they translate, and `scripts/check_i18n.py` prevents a translation
from claiming to be up to date when it is not (ADR 0007). ADRs, phase specs and
agent maps are only in Spanish.

## License

MIT (see `LICENSE`). Only third-party code with a permissive license is ported,
and every origin is declared in `docs/terceros.yaml` (ADR 0002).
