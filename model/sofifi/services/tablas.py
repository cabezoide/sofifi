# SPDX-License-Identifier: MIT
"""Genera las tablas del RTL a partir del modelo: lo generado coincide con su generador.

El RTL no calcula la tabla Hermite: la lee de ``rtl/nucleo/tabla_hermite.v``,
que escribe ``sofifi tablas``. ``model/tests/tablas_test.py`` exige que el
fichero del repositorio sea idéntico a lo que produce esta función.
"""

from __future__ import annotations

from sofifi.domain.aritmetica import COEF_BITS
from sofifi.domain.interpolacion import FRACCIONES, tabla_hermite

RUTA_TABLA_HERMITE = "rtl/nucleo/tabla_hermite.v"


def verilog_tabla_hermite() -> str:
    """ROM de 256 × 4 coeficientes S1.16, con salida registrada (1 ciclo)."""
    mascara = (1 << COEF_BITS) - 1
    lineas = [
        "// SPDX-License-Identifier: MIT",
        "//",
        "// GENERADO por `sofifi tablas` desde model/sofifi/domain/interpolacion.py.",
        "// No se edita a mano: model/tests/tablas_test.py compara este fichero con su",
        "// generador. Coeficientes Hermite S1.16 para la fracción frac/256:",
        "// coefs = {c0, c1, c2, c3}, y = c0·x[-1] + c1·x0 + c2·x1 + c3·x2.",
        "`default_nettype none",
        "",
        "module tabla_hermite (",
        "    input  wire        clk,",
        "    input  wire [7:0]  frac,",
        "    output reg  [71:0] coefs",
        ");",
        "    always @(posedge clk) begin",
        "        case (frac)",
    ]
    for f, cs in enumerate(tabla_hermite()):
        palabra = 0
        for c in cs:
            palabra = (palabra << COEF_BITS) | (c & mascara)
        etiqueta = "default" if f == FRACCIONES - 1 else f"8'd{f}"
        lineas.append(f"            {etiqueta}: coefs <= 72'h{palabra:018x};")
    lineas += ["        endcase", "    end", "endmodule", "", "`default_nettype wire", ""]
    return "\n".join(lineas)
