# SPDX-License-Identifier: MIT
"""Genera las tablas del RTL a partir del modelo: lo generado coincide con su generador.

El RTL no calcula la tabla Hermite: la lee de ``rtl/nucleo/tabla_hermite.v``,
que escribe ``sofifi tablas``. ``model/tests/tablas_test.py`` exige que el
fichero del repositorio sea idéntico a lo que produce esta función.
"""

from __future__ import annotations

from sofifi.domain.aritmetica import COEF_BITS
from sofifi.domain.interpolacion import FRACCIONES, tabla_hermite
from sofifi.domain.isa import Programa, codificar
from sofifi.domain.lfo import TipoLfo

RUTA_TABLA_HERMITE = "rtl/nucleo/tabla_hermite.v"
PROGRAMAS_EN_ROM = ("plate",)
CODIGO_LFO = {TipoLfo.SIN: 0, TipoLfo.RND: 1, TipoLfo.RAMP: 2}


def ruta_programa(nombre: str) -> str:
    return f"rtl/top/programa_{nombre}.v"


def verilog_tabla_hermite() -> str:
    """ROM de 256 × 4 coeficientes S1.16, combinacional (va en LUT, no en BSRAM).

    En BSRAM daba violaciones de hold en sus direcciones (Fase 04); en LUT ocupa
    unas pocas centenas de celdas y libera 2 bloques. El núcleo registra la salida.
    """
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
        "    input  wire [7:0]  frac,",
        "    output reg  [71:0] coefs",
        ");",
        "    always @(*) begin",
        "        // En lógica: en BSRAM (SPX9) daba violaciones de hold en sus",
        "        // direcciones. El atributo va en el case, de donde Yosys saca la ROM.",
        '        (* rom_style = "logic" *)',
        "        case (frac)",
    ]
    for f, cs in enumerate(tabla_hermite()):
        palabra = 0
        for c in cs:
            palabra = (palabra << COEF_BITS) | (c & mascara)
        etiqueta = "default" if f == FRACCIONES - 1 else f"8'd{f}"
        lineas.append(f"            {etiqueta}: coefs = 72'h{palabra:018x};")
    lineas += ["        endcase", "    end", "endmodule", "", "`default_nettype wire", ""]
    return "\n".join(lineas)


def verilog_programa(programa: Programa) -> str:
    """ROM con el microcódigo de un programa y su configuración (lo que va en el .json).

    La carga un top en el núcleo por el puerto de programa, igual que hará el
    cargador de la microSD (Fase 08).
    """
    tipos = sum(CODIGO_LFO[c.tipo] << (2 * k) for k, c in enumerate(programa.lfos) if c is not None)
    excursiones = sum(c.excursion << (15 * k) for k, c in enumerate(programa.lfos) if c is not None)
    n = len(programa.instrucciones)
    lineas = [
        "// SPDX-License-Identifier: MIT",
        "//",
        f"// GENERADO por `sofifi tablas` desde programas/{programa.nombre}.sasm.",
        "// No se edita a mano: model/tests/tablas_test.py compara este fichero con su",
        f"// generador. {n} instrucciones, {programa.ciclos} ciclos del modelo,",
        f"// {programa.palabras_memoria} palabras de memoria.",
        "`default_nettype none",
        "",
        f"module programa_{programa.nombre} (",
        "    input  wire [10:0] dir,",
        "    output reg  [53:0] palabra,",
        "    output wire [11:0] instrucciones,",
        "    output wire [15:0] palabras,",
        "    output wire [7:0]  lfo_tipos,",
        "    output wire [59:0] lfo_excursiones,",
        "    output wire        absoluta",
        ");",
        f"    assign instrucciones   = 12'd{n};",
        f"    assign palabras        = 16'd{programa.palabras_memoria};",
        f"    assign lfo_tipos       = 8'h{tipos:02x};",
        f"    assign lfo_excursiones = 60'h{excursiones:015x};",
        f"    assign absoluta        = 1'b{int(programa.usa_absoluta)};",
        "    always @(*) begin",
        "        // En lógica: en BSRAM (SPX9) daba violaciones de hold (Fase 04).",
        '        (* rom_style = "logic" *)',
        "        case (dir)",
    ]
    for k, ins in enumerate(programa.instrucciones):
        lineas.append(f"            11'd{k}: palabra = 54'h{codificar(ins):014x};")
    lineas += [
        "            default: palabra = 54'h0;",
        "        endcase",
        "    end",
        "endmodule",
        "",
        "`default_nettype wire",
        "",
    ]
    return "\n".join(lineas)
