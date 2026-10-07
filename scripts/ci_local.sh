#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# LA compuerta local (ADR 0001). Única definición de qué trabajo es duro y cuál
# blando: el hook pre-push delega aquí con --no-soft y no mantiene lista propia.
#
# Uso:
#   scripts/ci_local.sh                 # todos los trabajos
#   scripts/ci_local.sh --no-soft       # solo los duros (lo que corre el hook)
#   scripts/ci_local.sh model docs      # solo los trabajos nombrados
#   scripts/ci_local.sh --list          # lista trabajos y su clase
#   scripts/ci_local.sh synth           # los de clase release solo corren si se nombran
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 2

PY="${PY:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PY" ]]; then
  echo "ERROR: no existe $PY. Ejecuta 'make install' primero." >&2
  exit 2
fi

# trabajo:clase  (clase = dura | blanda | release). El orden es el de ejecución.
JOBS=(
  "tech-debt:dura"
  "secrets:dura"
  "licenses:dura"
  "adr-gate:dura"
  "docs:dura"
  "i18n:dura"
  "model:dura"
  "rtl-lint:dura"
  "sim:dura"
  "optimizacion:dura"
  "ratchets:dura"
  "shell-lint:blanda"
  "synth:release"
)

# Tope de procesos para lo que lanza herramientas EDA: el 2026-10-07 un enlace
# verilator -> verilator-cli se relanzó en bucle y tumbó la máquina por OOM.
TOPE_PROCESOS=4096

# El verilator de pip, sin su envoltorio `verilator-cli` (que busca `verilator`
# en PATH y puede encontrarse a sí mismo).
verilator_real() {
  local raiz
  raiz="$("$PY" -c 'import pathlib, verilator; print(pathlib.Path(verilator.__file__).parent)' 2>/dev/null)" \
    || { echo "falta el paquete verilator: ejecuta 'make install'." >&2; return 1; }
  VERILATOR_ROOT="$raiz" "$raiz/bin/verilator" "$@"
}

job_class() {
  local j
  for j in "${JOBS[@]}"; do
    [[ "${j%%:*}" == "$1" ]] && { echo "${j##*:}"; return 0; }
  done
  return 1
}

run_job() {
  case "$1" in
    tech-debt)  scripts/check_tech_debt.sh ;;
    secrets)    scripts/check_secrets_hygiene.sh ;;
    licenses)   "$PY" scripts/check_licenses.py ;;
    adr-gate)   scripts/check_adr_gate.sh ;;
    docs)       "$PY" scripts/check_docs.py ;;
    i18n)       "$PY" scripts/check_i18n.py ;;
    model)
      "$PY" -m ruff check model scripts \
        && "$PY" -m ruff format --check model scripts \
        && "$PY" -m mypy \
        && "$PY" -m pytest
      ;;
    ratchets)   "$PY" scripts/check_ratchets.py ;;
    rtl-lint)
      local files
      files="$(git ls-files 'rtl/*.v' 'rtl/*.sv' 2>/dev/null)"
      if [[ -z "$files" ]]; then
        echo "rtl-lint: no hay fuentes RTL todavía (nada que comprobar)."
        return 0
      fi
      # shellcheck disable=SC2086
      (ulimit -u "$TOPE_PROCESOS"; verilator_real --lint-only -Wall $files)
      ;;
    sim)
      (ulimit -u "$TOPE_PROCESOS"; "$PY" -m pytest sim --no-cov -p no:cacheprovider)
      ;;
    optimizacion)
      (ulimit -u "$TOPE_PROCESOS"; "$PY" scripts/check_optimizacion.py)
      ;;
    synth)
      local linea
      while read -r -a linea; do
        [[ ${#linea[@]} -eq 0 || "${linea[0]}" == \#* ]] && continue
        (ulimit -u "$TOPE_PROCESOS"; scripts/fpga.sh synth "${linea[@]:1}") || return 1
      done < rtl/top/tops.txt
      ;;
    shell-lint)
      if ! command -v shellcheck >/dev/null; then
        echo "shell-lint NO CORRIÓ: falta shellcheck."
        return 3
      fi
      shellcheck scripts/*.sh scripts/hooks/*
      ;;
    *) echo "trabajo desconocido: $1" >&2; return 2 ;;
  esac
}

NO_SOFT=0
SELECTED=()
for arg in "$@"; do
  case "$arg" in
    --no-soft) NO_SOFT=1 ;;
    --list) for j in "${JOBS[@]}"; do echo "${j%%:*} (${j##*:})"; done; exit 0 ;;
    -h|--help) sed -n '2,14p' "$0"; exit 0 ;;
    *) job_class "$arg" >/dev/null || { echo "trabajo desconocido: $arg" >&2; exit 2; }
       SELECTED+=("$arg") ;;
  esac
done
if [[ ${#SELECTED[@]} -eq 0 ]]; then
  for j in "${JOBS[@]}"; do
    [[ "${j##*:}" == "release" ]] || SELECTED+=("${j%%:*}")
  done
fi

START=$(date +%s)
FAILED_HARD=()
WARNED=()
for job in "${SELECTED[@]}"; do
  cls="$(job_class "$job")"
  if [[ $NO_SOFT -eq 1 && "$cls" == "blanda" ]]; then
    continue
  fi
  echo "━━━ [$cls] $job"
  t0=$(date +%s)
  run_job "$job"
  rc=$?
  dt=$(( $(date +%s) - t0 ))
  if [[ $rc -eq 0 ]]; then
    echo "    OK ($dt s)"
  elif [[ "$cls" != "blanda" ]]; then
    echo "    FALLO ($dt s)"
    FAILED_HARD+=("$job")
  else
    echo "    WARN ($dt s): compuerta blanda, no bloquea"
    WARNED+=("$job")
  fi
done
TOTAL=$(( $(date +%s) - START ))

# La compuerta se cronometra a sí misma (SPEC_RAIZ §2.2); fichero no versionado.
echo "$(date -Iseconds) total=${TOTAL}s no_soft=${NO_SOFT} jobs=${SELECTED[*]}" >> .ci_timing.log

echo "━━━ Resumen: ${TOTAL}s"
[[ ${#WARNED[@]} -gt 0 ]] && echo "WARN (blandas): ${WARNED[*]}"
if [[ ${#FAILED_HARD[@]} -gt 0 ]]; then
  echo "ROJO (duras): ${FAILED_HARD[*]}"
  echo "Dos salidas: arreglarlo, o mover el listón con su motivo (ADR o registro)."
  exit 1
fi
echo "VERDE"
