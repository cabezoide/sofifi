# AGENTS.md — mapa en frío

Se lee en menos de cinco minutos. La compuerta `docs` (`scripts/check_docs.py`)
comprueba que toda ruta, objetivo de `make` y ADR citados aquí existen.

## Qué es esto

SOFIFI es un pedal de guitarra ambient sobre una FPGA Sipeed Tang Primer 25K. El DSP corre
en un núcleo microcodificado tipo FV-1 (ADR 0006). Un modelo Python bit-exact es
el oráculo del RTL (ADR 0003). Todo el audio vive en BSRAM, porque no hay SDRAM
(ADR 0004). Se trabaja a fs = 48 828 Hz (ADR 0005).

## Arranque

`make install`, `make hooks`, `make ci`. Para iterar más rápido:
`scripts/ci_local.sh model`, o `scripts/ci_local.sh --list` para ver los trabajos.

## Dónde vive cada cosa

| Ruta | Qué |
|---|---|
| `docs/SPEC_RAIZ.md` | disciplina de flujo, documentación y pruebas. **Manda.** |
| `docs/investigacion/INVESTIGACION.md` | investigación de partida: pedales, algoritmos, open source, placa |
| `docs/adr/README.md` | índice de decisiones. Leerlo antes de proponer un cambio estructural |
| `docs/fases/` | spec por fase + control `docs/fases/estado_fases.csv` |
| `docs/terceros.yaml` | origen y licencia de todo código ajeno estudiado o portado |
| `docs/EXTENDING.md` | cómo añadir un efecto, un módulo RTL o una compuerta |
| `model/sofifi/` | modelo de referencia, por capas (ver `model/AGENTS.md`) |
| `demo_examples/` | WAV de demostración (guitarra sintética + plate, shimmer, freeze); se regeneran con `scripts/generar_demos.py` |
| `programas/` | programas del núcleo en ensamblador (`.sasm`): plate, shimmer, freeze |
| `rtl/` | Verilog sintetizable (ver `rtl/AGENTS.md`) |
| `sim/` | testbenches cocotb que comparan RTL con modelo (ver `sim/AGENTS.md`) |
| `scripts/ci_local.sh` | LA compuerta; el hook `scripts/hooks/pre-push` delega en ella |

## Invariantes

1. **Ciclo:** rama → código → `make ci` en verde → commit → push (el hook revalida)
   → PR → merge.
2. **Decisión estructural = ADR en el mismo PR.** Lo vigila `scripts/check_adr_gate.sh`
   con las sentinelas de `docs/adr/sentinelas.txt`.
3. **Modelo bit-exact antes que RTL.** Ningún bloque DSP entra en `rtl/` sin su
   modelo y su testbench de comparación muestra a muestra.
4. **Todo fichero fuente lleva `SPDX-License-Identifier`**, y lo ajeno se declara en
   `docs/terceros.yaml`.
5. **Una fase planificada no entra en el control**; entra al cerrarse.

## Qué no tocar

- `docs/SPEC_RAIZ.md`: si una regla cambia en este proyecto, se cambia allí *y se
  dice por qué* (cierre de la propia spec).
- No copiar a `model/` ni a `rtl/` código GPL, LGPL o CERN-OHL-S, aunque esté en la
  investigación. Se estudia, no se porta (ADR 0002).
- No añadir una segunda lista de trabajos en el hook (P8).

## Trampas conocidas

- **fs no es 48 000 Hz, sino 48 828,125 Hz.** Las longitudes de delay de los papers
  (Dattorro a 29 761 Hz) hay que reescalarlas a esta frecuencia, no a 48 kHz.
- **La microSD tiene picos de escritura de hasta 250 ms.** No sirve de memoria de
  audio en tiempo real (ADR 0004).
- **Los PRs apilados no llegan solos a `main`.** GitHub solo reapunta la base si se borra la rama al fusionar. Hay que fusionar con `--delete-branch` y comprobar con `gh pr view N --json baseRefName` que la base es `main`. `gh pr edit --base` falla (Projects classic); se usa `gh api -X PATCH repos/cabezoide/sofifi/pulls/N -f base=main` (ADR 0001).
- **Las demos se regeneran, no se editan.** Si cambia un programa, cambia su huella en `model/tests/programas_test.py` y hay que volver a correr `scripts/generar_demos.py`.
- **El ADC interno del GW5A acepta 0–1 V**, no 0–3,3 V, y no está confirmado qué
  pines llegan al Dock.
