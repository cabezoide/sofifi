#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# Cadena EDA abierta para la Tang Primer 25K (Fase 02):
#   scripts/fpga.sh synth TOP.v [más .v]   → build/<top>.fs + build/<top>_recursos.json
#   scripts/fpga.sh prog  build/<top>.fs   → carga en SRAM (se pierde al apagar)
# Lo llaman make synth, make prog, make hil y scripts/check_optimizacion.py.
# Herramientas (make install): yowasp-yosys, yowasp-nextpnr-himbaechel-gowin,
# gowin_pack y openfpgaloader. prog necesita la placa por USB (scripts/udev/).
# Variables: CST (restricciones), FREQ_MHZ (reloj; 100), SYNTH_OPCIONES (yosys)
# y SEMILLAS_PNR (semillas de reintento de nextpnr; "2 3 4", F-33).
# synth deja también en build/ <top>.yosys.log, <top>.pnr.log y <top>.informe.json.
# Salida: 0 bien; distinta de 0 si una herramienta falla o ninguna semilla
# cierra el reloj; 2 si el uso es incorrecto.
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
    # La colocación de nextpnr depende de la semilla: el mismo netlist da de
    # 95 a 112 MHz (F-33). Si solo falla el reloj, se prueba la semilla siguiente.
    cerrado=""
    for semilla in "" ${SEMILLAS_PNR:-2 3 4}; do
      if "$BIN/yowasp-nextpnr-himbaechel-gowin" -q -l "$nombre.pnr.log" \
        --json "$nombre.synth.json" --write "$nombre.pnr.json" --top "$nombre" \
        --device GW5A-LV25MG121NES --vopt cst="$CST" --vopt sspi_as_gpio \
        --freq "$FREQ_MHZ" --report "$nombre.informe.json" ${semilla:+--seed "$semilla"}; then
        cerrado=1
        [[ -z "$semilla" ]] || echo "$nombre: el reloj cierra con la semilla $semilla de nextpnr"
        break
      fi
      grep -q "FAIL at" "$nombre.pnr.log" || exit 1   # otro error: no se reintenta
    done
    [[ -n "$cerrado" ]] || { echo "$nombre: ninguna semilla de nextpnr cierra el reloj" >&2; exit 1; }
    "$BIN/gowin_pack" --sspi_as_gpio --cpu_as_gpio -d GW5A-25A -o "$nombre.fs" "$nombre.pnr.json"
    "$ROOT/.venv/bin/python" "$ROOT/scripts/informe_recursos.py" "$nombre.informe.json" > "${nombre}_recursos.json"
    cat "${nombre}_recursos.json"
    ;;
  prog)
    [[ $# -eq 1 ]] || { echo "uso: $0 prog build/<top>.fs" >&2; exit 2; }
    "$BIN/openfpgaloader-cli" -b tangprimer25k "$1"
    ;;
  *)
    sed -n '4,14p' "$0"; exit 2 ;;
esac
