// SPDX-License-Identifier: MIT
//
// Conversión de formato del núcleo (ADR 0008), equivalente bit a bit a la
// función del mismo nombre de model/sofifi/domain/aritmetica.py.
// ACC S8.39 → dato S.23: suma 2^15, desplaza 16 (floor) y satura a 24 bit.
`default_nettype none

module acc_a_dato (
    input  wire signed [47:0] acc,
    output wire signed [23:0] dato
);
    // acc + 2^15 cabe en 49 bit; el desplazamiento aritmético es el floor.
    // Los 16 bit bajos de la suma se descartan: son el redondeo.
    /* verilator lint_off UNUSEDSIGNAL */
    wire signed [48:0] suma = {acc[47], acc} + 49'sd32768;
    /* verilator lint_on UNUSEDSIGNAL */
    wire signed [32:0] desplazado = suma[48:16];
    assign dato = (desplazado > 33'sd8388607)  ? 24'sh7FFFFF :
                  (desplazado < -33'sd8388608) ? 24'sh800000 : desplazado[23:0];
endmodule

`default_nettype wire
