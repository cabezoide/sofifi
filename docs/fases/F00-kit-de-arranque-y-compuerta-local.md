# Fase 00 — Kit de arranque y compuerta local

## Objetivo

Que el repositorio exista con la disciplina de `docs/SPEC_RAIZ.md` **antes** de la primera línea de producto: compuerta local, hook, mapas, ADRs y registros.

## Origen

La investigación inicial (`docs/investigacion/INVESTIGACION.md`) y la decisión de publicar el proyecto en GitHub, en un repositorio privado y bajo licencia MIT.

## Diagnóstico

- **Ya existe y se reutiliza:** la spec-raíz (§11, kit de arranque) y la investigación.
- **Falta:** todo lo demás. Además, la spec-raíz está escrita para un backend web con frontend, y aquí hay modelo Python, RTL y testbenches.

## El hallazgo que decide el diseño

La arquitectura hexagonal y los contratos de capas de §5 sí aplican, pero **al modelo de referencia**, no al RTL. El modelo es el oráculo del hardware (ADR 0003): si sus capas se mezclan, el oráculo se vuelve imposible de probar en seco. El frontend de §6 no aplica, porque no hay interfaz web.

## Diseño

- Compuerta en `scripts/ci_local.sh`:
  - **Duras:** `tech-debt`, `secrets`, `licenses`, `adr-gate`, `docs`, `i18n`, `model`, `ratchets`.
  - **Blandas:** `rtl-lint`, `shell-lint`.
- Contratos de capas del modelo en `model/tests/arquitectura_test.py`.
- ADRs 0001 a 0007.
- Registros YAML de ratchets, promesas, madurez y mediciones.
- README trilingüe con sello (ADR 0007).

## Plan de PRs

No hay rama base, así que es un único commit inicial en `main`. A partir de aquí, todo va por PR.

## Criterios de aceptación

- `make ci` en verde, con las compuertas blandas declarando si no corrieron.
- La compuerta `docs` verifica que los mapas citan rutas existentes.

## Lo que NO entra

DSP, RTL, testbenches, síntesis, CI remota y compuerta de release.
