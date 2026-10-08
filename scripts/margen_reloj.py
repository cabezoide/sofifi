# SPDX-License-Identifier: MIT
"""Mide en la placa el margen de reloj real del núcleo (ADR 0011, fails.md F-11).

nextpnr es optimista con el GW5A: un diseño que da 132 MHz en su análisis
fallaba a 100 en el silicio. Este script cambia **solo** el divisor del PLL en el
JSON ya rutado (la colocación y el rutado no cambian), vuelve a empaquetar,
carga el bitstream y repite la captura de scripts/hil_nucleo.py a esa
frecuencia. La UART se escala con el reloj.

Uso::

    make synth TOP=hil_nucleo
    .venv/bin/python scripts/margen_reloj.py                 # 100 y 114,3 MHz, 3 veces
    .venv/bin/python scripts/margen_reloj.py --divisores 8 7 6 --repeticiones 1
    .venv/bin/python scripts/margen_reloj.py --traza   # si falla, qué instrucción

Divisor del PLL → frecuencia, con el VCO de 800 MHz (``--mdiv 16``): 8 → 100 MHz,
7 → 114,3 MHz, 6 → 133,3 MHz. Para puntos intermedios se cambia también el
multiplicador del VCO: con ``--mdiv 20`` (1 000 MHz), 9 → 111,1 MHz, 8 → 125 MHz.
Al terminar carga prueba_pll, que envía poco: el puente del BL616 se cuelga si
se reprograma con la FPGA enviando a caudal alto (F-02).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from hil_nucleo import N_CAPTURA, capturar, comprobar, comprobar_traza

RAIZ = Path(__file__).resolve().parent.parent
BIN = RAIZ / ".venv" / "bin"
FCLKIN_MHZ = 50


def bitstream_con_divisor(base: str, divisor: int, mdiv: int = 16) -> Path:
    datos = json.loads((RAIZ / "build" / f"{base}.pnr.json").read_text(encoding="utf-8"))
    for modulo in datos["modules"].values():
        for celda in modulo["cells"].values():
            if celda["type"] == "PLLA":
                celda["parameters"]["ODIV0_SEL"] = format(divisor, "032b")
                celda["parameters"]["MDIV_SEL"] = format(mdiv, "032b")
    salida = RAIZ / "build" / "exp" / f"{base}_mdiv{mdiv}_odiv{divisor}"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.with_suffix(".pnr.json").write_text(json.dumps(datos), encoding="utf-8")
    subprocess.run(
        [
            str(BIN / "gowin_pack"),
            "--sspi_as_gpio",
            "--cpu_as_gpio",
            "-d",
            "GW5A-25A",
            "-o",
            str(salida.with_suffix(".fs")),
            str(salida.with_suffix(".pnr.json")),
        ],
        check=True,
        capture_output=True,
    )
    return salida.with_suffix(".fs")


def cargar(fs: Path) -> None:
    subprocess.run(
        [str(BIN / "openfpgaloader-cli"), "-b", "tangprimer25k", str(fs)],
        check=True,
        capture_output=True,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="hil_nucleo", help="top ya rutado en build/")
    ap.add_argument("--programa", default="plate", help="el de la ROM del top: plate o looper")
    ap.add_argument("--divisores", type=int, nargs="+", default=[8, 7])
    ap.add_argument("--mdiv", type=int, default=16, help="VCO = 50 MHz × MDIV")
    ap.add_argument("--repeticiones", type=int, default=3)
    ap.add_argument("--puerto", default="/dev/ttyUSB1")
    ap.add_argument(
        "--traza", action="store_true", help="si falla, localiza la primera instrucción mal"
    )
    args = ap.parse_args(argv)
    todo_bien_a_100 = True
    try:
        for divisor in args.divisores:
            mhz = FCLKIN_MHZ * args.mdiv / divisor
            fs = bitstream_con_divisor(args.base, divisor, args.mdiv)
            correctas = 0
            for _ in range(args.repeticiones):
                cargar(fs)
                baudios = round(115_200 * mhz / 100)
                r = comprobar(capturar(args.puerto, 40, baudios=baudios), N_CAPTURA, args.programa)
                correctas += r.correcto and r.muestras == N_CAPTURA
                if args.traza and r.primera_muestra is not None:
                    k0 = max(0, r.primera_muestra - 1)
                    orden = b"T" + k0.to_bytes(2, "big")
                    lineas = capturar(args.puerto, 40, orden, baudios)
                    print(f"  {r.primera_diferencia}")
                    diferencia = comprobar_traza(lineas, k0, args.programa)
                    print(f"  traza desde la muestra {k0}: {diferencia}")
            print(f"{mhz:6.1f} MHz: {correctas} de {args.repeticiones} capturas iguales al modelo")
            if mhz == 100 and correctas != args.repeticiones:
                todo_bien_a_100 = False
    finally:
        cargar(RAIZ / "build" / "prueba_pll.fs")
    return 0 if todo_bien_a_100 else 1


if __name__ == "__main__":
    sys.exit(main())
