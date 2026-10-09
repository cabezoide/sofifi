#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# Apunta git a los hooks versionados (ADR 0001), para que viajen con el repo.
# Cuándo: una vez, después de clonar (make hooks).
# Uso: scripts/install_hooks.sh
# Escribe core.hooksPath = scripts/hooks en .git/config y marca los scripts
# como ejecutables. Salida: 0 bien.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
chmod +x "$ROOT"/scripts/hooks/* "$ROOT"/scripts/*.sh
git -C "$ROOT" config core.hooksPath scripts/hooks
echo "core.hooksPath = scripts/hooks"
