// SPDX-License-Identifier: MIT
//
// Último paso de curva_suave (model/sofifi/domain/aritmetica.py):
//
//   y = sat24((3x − x3) >> 1),   con x3 = p >> 23 y p = x2·x, x2 = (x·x) >> 23.
//
// Los dos productos los hace el multiplicador del núcleo y 3x llega ya calculado
// (`tres_x`), para que aquí quede una sola resta: es un camino crítico a 100 MHz.
// Lo usan CLIP y el LFO SIN dentro de CHO (nucleo.v).
`default_nettype none

module curva_fin (
    input  wire signed [25:0] tres_x,   // 3·x
    /* verilator lint_off UNUSEDSIGNAL */
    input  wire signed [62:0] p,      // x2·x cabe en 48 bit
    /* verilator lint_on UNUSEDSIGNAL */
    output wire signed [23:0] y
);
    // Una selección de bits es sin signo: se pasa por un cable con signo para
    // que >>> sea aritmético (el floor del modelo).
    wire signed [49:0] p50    = p[49:0];
    wire signed [49:0] x3     = p50 >>> 23;
    // Una concatenación es sin signo: pasa por un cable con signo antes de >>>.
    wire signed [49:0] t3     = {{24{tres_x[25]}}, tres_x};
    wire signed [49:0] medio  = (t3 - x3) >>> 1;
    assign y = (medio > 50'sd8388607)  ? 24'sh7FFFFF :
               (medio < -50'sd8388608) ? 24'sh800000 : medio[23:0];
endmodule

`default_nettype wire
