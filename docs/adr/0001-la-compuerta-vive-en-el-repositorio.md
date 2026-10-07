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

## Actualización 2026-10-07 (demos de audio versionadas)

La persona propietaria pide versionar las demos de audio en `demo_examples/`. La regla de `scripts/check_secrets_hygiene.sh` («ningún fichero de más de 1 MiB: los binarios van a releases») se mueve, con motivo, solo para esa carpeta: hasta 4 MiB por WAV y 16 MiB en total.

Las demos no son binarios huérfanos: `scripts/generar_demos.py` las regenera byte a byte, porque el núcleo es bit-exact y la guitarra sintética tiene semilla fija.

Si `demo_examples/` necesita superar los 16 MiB, las demos pasan a assets de release en lugar de subir el techo.

## Actualización 2026-10-07 (PRs apilados)

Con PRs apilados, GitHub solo reapunta la base del siguiente si se borra la rama base al fusionar. En la Fase 01, los PRs #2, #3 y #4 se fusionaron en sus ramas base y no en `main`, y hubo que llevarlos con el #5.

Desde ahora se cumplen tres reglas:
- se fusiona con `--delete-branch`;
- antes de fusionar se comprueba que la base sea `main`;
- `gh pr edit --base` falla por la deprecación de Projects classic, así que la base se cambia con `gh api -X PATCH repos/<dueño>/<repo>/pulls/N -f base=main`.
