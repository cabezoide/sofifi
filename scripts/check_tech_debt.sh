#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# Deuda cero (SPEC_RAIZ §3.7): un comentario que EMPIEZA por un marcador de
# deuda es rojo. La palabra en medio de la prosa no cuenta.
# Cuándo: trabajo duro `tech-debt` de scripts/ci_local.sh (pre-push y make ci).
# Revisa .py, .sh, Verilog, YAML, .cst, .sdc, .sasm, el Makefile y los hooks.
# Uso: scripts/check_tech_debt.sh   (sin opciones; no escribe nada)
# Salida: 0 sin marcadores; 1 si hay alguno.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

MARKERS='(TODO|FIXME|HACK|XXX)'
# Comentarios: # (py, sh, yaml, make), // (verilog), /* (verilog), -- (vhdl), ; (sasm).
PATTERN="^[[:space:]]*(#|//|/\*|\*|--|;)[[:space:]]*${MARKERS}\b"

mapfile -t FILES < <(git ls-files --cached --others --exclude-standard \
  -- '*.py' '*.sh' '*.v' '*.sv' '*.vh' '*.svh' '*.yaml' '*.yml' '*.cst' '*.sdc' \
     '*.sasm' 'Makefile' 'scripts/hooks/*' \
  | grep -v '^scripts/check_tech_debt.sh$' \
  | while read -r f; do [[ -f "$f" ]] && echo "$f"; done)

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "tech-debt: sin ficheros que revisar."
  exit 0
fi

if grep -nEH "$PATTERN" "${FILES[@]}"; then
  echo "tech-debt: marcador de deuda al inicio de un comentario." >&2
  echo "Salidas: resolverlo, o convertirlo en un issue y quitar el marcador." >&2
  exit 1
fi
echo "tech-debt: ${#FILES[@]} ficheros sin marcadores de deuda."
