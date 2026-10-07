#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# Cadena EDA abierta para la Tang Primer 25K (Fase 02):
#   scripts/fpga.sh synth TOP.v [más .v]   → build/<top>.fs + build/<top>_recursos.json
#   scripts/fpga.sh prog  build/<top>.fs   → carga en SRAM (se pierde al apagar)
# Herramientas: yowasp-yosys, yowasp-nextpnr-himbaechel-gowin, gowin_pack, openfpgaloader.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$ROOT/.venv/bin"
CST="${CST:-$ROOT/rtl/top/primer25k.cst}"
FREQ_MHZ="${FREQ_MHZ:-100}"   # reloj del sistema (ADR 0005); nextpnr no deduce la salida del PLL

orden="${1:-}"; shift || true
case "$orden" in
  synth)
    [[ $# -ge 1 ]] || { echo "uso: $0 synth TOP.v [más .v]" >&2; exit 2; }
    nombre="$(basename "$1" .v)"
    fuentes=()
    for f in "$@"; do fuentes+=("$(realpath "$f")"); done
    mkdir -p "$ROOT/build"
    cd "$ROOT/build"
    "$BIN/yowasp-yosys" -q -l "$nombre.yosys.log" \
      -p "read_verilog -sv ${fuentes[*]}; synth_gowin -top $nombre -family gw5a -nolutram ${SYNTH_OPCIONES:-} -json $nombre.synth.json"
    "$BIN/yowasp-nextpnr-himbaechel-gowin" -q -l "$nombre.pnr.log" \
      --json "$nombre.synth.json" --write "$nombre.pnr.json" --top "$nombre" \
      --device GW5A-LV25MG121NES --vopt cst="$CST" --vopt sspi_as_gpio \
      --freq "$FREQ_MHZ" --report "$nombre.informe.json"
    "$BIN/gowin_pack" --sspi_as_gpio --cpu_as_gpio -d GW5A-25A -o "$nombre.fs" "$nombre.pnr.json"
    "$ROOT/.venv/bin/python" "$ROOT/scripts/informe_recursos.py" "$nombre.informe.json" > "${nombre}_recursos.json"
    cat "${nombre}_recursos.json"
    ;;
  prog)
    [[ $# -eq 1 ]] || { echo "uso: $0 prog build/<top>.fs" >&2; exit 2; }
    "$BIN/openfpgaloader-cli" -b tangprimer25k "$1"
    ;;
  *)
    sed -n '4,8p' "$0"; exit 2 ;;
esac
