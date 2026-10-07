# ADR 0002 — El copyleft se estudia, no se copia

- **Estado:** Aceptado · 2026-10-07
- **Revisión prevista:** solo si cambia la licencia del proyecto.

## Contexto

El proyecto es MIT. La investigación (`docs/investigacion/INVESTIGACION.md`) mezcla fuentes de distinto tipo:

- **Permisivas:** Mutable Instruments, CloudSeed, dattorro-verb, DaisySP, Airwindows, Faust jpverb/greyhole.
- **Copyleft:** Surge (GPL-3), Valley (GPL-3), ChowTape (GPL-3), DaisySP-LGPL, Tiliqua y eurorack-pmod (CERN-OHL-S).

Traducir un algoritmo de C++ a Verilog **sigue siendo obra derivada**.

## Opciones evaluadas

1. Cambiar el proyecto a GPL para poder usarlo todo.
2. Mantener MIT y portar solo código permisivo.

## Decisión

Opción 2 (decisión de la persona propietaria, 2026-10-07).

- Todo origen ajeno, estudiado o portado, se declara en `docs/terceros.yaml`.
- `uso: portado` solo se admite con licencia permisiva.
- Todo fichero fuente declara su `SPDX-License-Identifier`.

Lo hace cumplir `scripts/check_licenses.py`, que es compuerta dura.

## Consecuencias

- Los algoritmos copyleft se pueden leer para entender una idea. Se reimplementan a partir del paper o de la descripción, no del código.
- Las herramientas de desarrollo (pytest, ruff, mypy) no forman parte del producto y no se declaran.

## Alternativas descartadas

- **GPL:** cerraría la puerta a reutilizar el núcleo en productos cerrados y no aporta ningún algoritmo imprescindible.
