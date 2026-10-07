#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# adr-gate (SPEC_RAIZ §3.1): si el diff toca una sentinela estructural
# (docs/adr/sentinelas.txt) y no toca ningún ADR, rojo.
# Escape consciente: ADR_GATE_ACK=1 ("revisé y ninguna decisión cambia").
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

SENTINELS_FILE="docs/adr/sentinelas.txt"
mapfile -t SENTINELS < <(grep -vE '^[[:space:]]*(#|$)' "$SENTINELS_FILE")

# Base del diff: lo que aún no está en el remoto, o todo si no hay remoto.
if git rev-parse --verify -q '@{upstream}' >/dev/null; then
  BASE="$(git merge-base HEAD '@{upstream}')"
elif git rev-parse --verify -q origin/main >/dev/null; then
  BASE="$(git merge-base HEAD origin/main)"
else
  BASE="$(git hash-object -t tree /dev/null)"   # árbol vacío: primer push
fi

# Cambios commiteados desde la base + cambios en el árbol de trabajo.
mapfile -t CHANGED < <( { git diff --name-only "$BASE" HEAD 2>/dev/null || true
                          git diff --name-only HEAD 2>/dev/null || true
                          git ls-files --others --exclude-standard; } | sort -u)

touched=()
for f in "${CHANGED[@]}"; do
  for s in "${SENTINELS[@]}"; do
    # shellcheck disable=SC2053
    [[ "$f" == $s ]] && touched+=("$f")
  done
done

if [[ ${#touched[@]} -eq 0 ]]; then
  echo "adr-gate: ninguna sentinela tocada."
  exit 0
fi

for f in "${CHANGED[@]}"; do
  if [[ "$f" =~ ^docs/adr/[0-9]{4}-.*\.md$ ]]; then
    echo "adr-gate: sentinelas tocadas (${touched[*]}) con ADR en el diff ($f)."
    exit 0
  fi
done

if [[ "${ADR_GATE_ACK:-0}" == "1" ]]; then
  echo "adr-gate: ADR_GATE_ACK=1 → aceptado sin ADR: ${touched[*]}"
  exit 0
fi
echo "adr-gate: el diff toca sentinelas estructurales sin tocar ningún ADR:" >&2
printf '  %s\n' "${touched[@]}" >&2
echo "Salidas: actualizar/crear el ADR en este cambio, o ADR_GATE_ACK=1 si ninguna decisión cambia." >&2
exit 1
