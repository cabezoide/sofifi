# ADR 0001 — La compuerta vive en el repositorio: `ci_local.sh` + pre-push versionado

- **Estado:** Aceptado · 2026-10-07
- **Revisión prevista:** cuando el repositorio tenga CI remota gratuita suficiente para la síntesis, o protección de rama.

## Contexto

El repositorio es privado en GitHub (plan gratuito): no hay protección de rama y los minutos de Actions son limitados. Además, la síntesis FPGA necesita herramientas (Gowin EDA, apicula) que no todo el mundo tiene instaladas. Sin una compuerta que viaje con el repositorio, la disciplina de `docs/SPEC_RAIZ.md` queda en buenas intenciones.

## Opciones evaluadas

1. GitHub Actions como única compuerta.
2. `scripts/ci_local.sh` + hook `pre-push` versionado, instalado con `core.hooksPath`.
3. Las dos cosas.

## Decisión

Opción 2. `scripts/ci_local.sh` es **la única definición** de qué trabajo es duro y cuál es blando. El hook delega con `--no-soft` y no tiene lista propia; lo comprueba `scripts/check_docs.py`.

Trabajos del día 0:

| Clase | Trabajos |
|---|---|
| Duros | `tech-debt`, `secrets`, `licenses`, `adr-gate`, `docs`, `i18n`, `model`, `ratchets` |
| Blandos | `rtl-lint` (verilator), `shell-lint` (shellcheck) |
| De release | síntesis con informe de recursos; aún no existe y `make release-check` falla a propósito |

## Consecuencias

- Cada push paga el coste de los trabajos duros. Se mide en `.ci_timing.log`, que no se versiona.
- Hay tres escapes, todos con nombre: `git push --no-verify`, `PREPUSH_SKIP=1` y `ADR_GATE_ACK=1`.

## Alternativas descartadas

- **Solo Actions:** sin protección de rama no bloquea nada, y la síntesis no cabe en el plan gratuito.
