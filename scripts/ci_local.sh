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
#   scripts/ci_local.sh optimizacion    # los de clase release solo corren si se nombran
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
  "ratchets:dura"
  "shell-lint:blanda"
  "optimizacion:release"
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
        && "$PY" -m pytest -n auto   # en paralelo: cada programa añade segundos (ADR 0001)
      ;;
    ratchets)   "$PY" scripts/check_ratchets.py ;;
    rtl-lint)
      local files
      # Un lint por top (rtl/top/tops.txt): varios tops juntos darían MULTITOP.
      # SIMULACION elige el modelo de comportamiento de las primitivas Gowin;
      # la rama de síntesis la comprueba el trabajo `optimizacion`.
      local linea fallos=0
      while read -r -a linea; do
        [[ ${#linea[@]} -eq 0 || "${linea[0]}" == \#* ]] && continue
        (ulimit -u "$TOPE_PROCESOS"
         verilator_real --lint-only -Wall -DSIMULACION --top-module "${linea[0]}" "${linea[@]:1}") \
          || fallos=1
      done < rtl/top/tops.txt
      # Además, cada módulo por separado: los del núcleo aún no están en ningún top.
      local modulos f
      modulos="$(git ls-files 'rtl/comun/*.v' 'rtl/primitivas/*.v' 'rtl/nucleo/*.v')"
      for f in $modulos; do
        # shellcheck disable=SC2086
        (ulimit -u "$TOPE_PROCESOS"
         verilator_real --lint-only -Wall -DSIMULACION --top-module "$(basename "$f" .v)" $modulos) \
          || fallos=1
      done
      return "$fallos"
      ;;
    sim)
      # 4 procesos: cada uno compila su núcleo; con 8 tarda más (ADR 0001).
      (ulimit -u "$TOPE_PROCESOS"; "$PY" -m pytest sim -n 4 --no-cov -p no:cacheprovider)
      ;;
    optimizacion)
      (ulimit -u "$TOPE_PROCESOS"; "$PY" scripts/check_optimizacion.py)
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
