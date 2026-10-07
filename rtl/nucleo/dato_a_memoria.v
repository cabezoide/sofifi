// SPDX-License-Identifier: MIT
//
// Conversión de formato del núcleo (ADR 0008), equivalente bit a bit a la
// función del mismo nombre de model/sofifi/domain/aritmetica.py.
// Dato S.23 → palabra S.17 de la memoria de retardo: redondea 6 bit y satura
// a 18 bit. El modelo devuelve la palabra alineada a dato (<< 6).
`default_nettype none

module dato_a_memoria (
    input  wire signed [23:0] dato,
    output wire signed [17:0] palabra
);
    // Los 6 bit bajos de la suma se descartan: son el redondeo.
    /* verilator lint_off UNUSEDSIGNAL */
    wire signed [24:0] suma = {dato[23], dato} + 25'sd32;
    /* verilator lint_on UNUSEDSIGNAL */
    wire signed [18:0] desplazado = suma[24:6];
    assign palabra = (desplazado > 19'sd131071)  ? 18'sh1FFFF :
                     (desplazado < -19'sd131072) ? 18'sh20000 : desplazado[17:0];
endmodule

`default_nettype wire
