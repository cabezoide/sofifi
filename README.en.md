<!-- i18n: fuente=README.md sha=9872a825da1b estado=al_dia -->
# ambient_guitar_pedal_fpga

**Languages:** [Español](README.md) (source) · English · [简体中文](README.zh-CN.md)

An ambient guitar pedal (reverbs, shimmer, tape delays, freeze, granular)
implemented on a **Sipeed Tang Primer 25K** FPGA (Gowin GW5A-LV25).

**Version:** `0.0` (the version is the last closed phase; see `docs/fases/estado_fases.csv`).

> Status: bootstrap kit. There is no DSP or RTL yet. The initial research
> (reference pedals, algorithms, open-source resources and board budget) is in
> `docs/investigacion/INVESTIGACION.md` (Spanish).

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

### Optional tools (soft gates)

- `verilator`: RTL lint.
- `shellcheck`: script lint.
- Gowin EDA Education (≥ 1.9.9Beta-4) or Yosys + nextpnr-himbaechel + apicula:
  synthesis. It will become a release gate.

If a tool is missing, the gate says so (`WARN … NO CORRIÓ`); it does not fake a green.

## Hardware

| Part | Status |
|---|---|
| Tang Primer 25K + Dock | available |
| 64 GB microSD (PMOD TF) | available |
| I2S codec (PCM1808 + PCM5102A or Digilent Pmod I2S2) | **missing** |
| Guitar input buffer | missing (temporary: any buffered pedal) |
| Sipeed SDRAM module | future (enables long looper and granular) |

## Languages

Spanish is the canonical source. Translations carry a seal with the fingerprint
of the version they translate, and `scripts/check_i18n.py` prevents a translation
from claiming to be up to date when it is not (ADR 0007). ADRs, phase specs and
agent maps are only in Spanish.

## License

MIT (see `LICENSE`). Only third-party code with a permissive license is ported,
and every origin is declared in `docs/terceros.yaml` (ADR 0002).
