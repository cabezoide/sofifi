#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# Higiene de secretos (SPEC_RAIZ §8.2) sobre lo que git VERSIONA de verdad
# (índice + no ignorados), no sobre el disco.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

mapfile -t FILES < <(git ls-files --cached --others --exclude-standard \
  | while read -r f; do [[ -f "$f" ]] && echo "$f"; done)
RC=0

# 1. Ficheros que no deben versionarse nunca.
for f in "${FILES[@]}"; do
  case "$f" in
    *.example) ;;
    .env|.env.*|*/.env|*/.env.*|*.pem|*.key|*.p12|*.pfx|id_rsa*|*.sqlite|*.sqlite3|*.db)
      echo "secrets: fichero prohibido en el repo: $f"; RC=1 ;;
  esac
done

# 2. Patrones de credencial real. Se excluye este propio script.
PATTERNS=(
  'AKIA[0-9A-Z]{16}'
  'ghp_[A-Za-z0-9]{36}'
  'github_pat_[A-Za-z0-9_]{40,}'
  'sk-[A-Za-z0-9_-]{32,}'
  'xox[baprs]-[A-Za-z0-9-]{10,}'
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'
)
TEXT_FILES=()
for f in "${FILES[@]}"; do
  [[ "$f" == "scripts/check_secrets_hygiene.sh" ]] && continue
  grep -Iq . "$f" 2>/dev/null && TEXT_FILES+=("$f")
done
if [[ ${#TEXT_FILES[@]} -gt 0 ]]; then
  for p in "${PATTERNS[@]}"; do
    if grep -nEH -e "$p" "${TEXT_FILES[@]}"; then
      echo "secrets: patrón de credencial: $p"; RC=1
    fi
  done
fi

# 3. Binarios grandes (bitstreams, WAV de pruebas) no se versionan: van a releases.
#    Excepción acotada (ADR 0001, actualización 2026-10-07): las demos de
#    demo_examples/ (Ogg Vorbis), regenerables con scripts/generar_demos.py,
#    hasta 4 MiB por fichero. Sin límite total desde la Fase 06 (ADR 0001).
DEMO_MAX=$((4 * 1048576))
for f in "${FILES[@]}"; do
  size=$(stat -c %s "$f")
  if [[ "$f" == demo_examples/*.ogg ]]; then
    if (( size > DEMO_MAX )); then
      echo "secrets: demo de más de 4 MiB: $f ($size bytes)"; RC=1
    fi
  elif (( size > 1048576 )); then
    echo "secrets: fichero de más de 1 MiB versionado: $f ($size bytes)"; RC=1
  fi
done

[[ $RC -eq 0 ]] && echo "secrets: ${#FILES[@]} ficheros limpios."
exit $RC
