// SPDX-License-Identifier: MIT
//
// Conversión de formato del núcleo (ADR 0008), equivalente bit a bit a la
// función del mismo nombre de model/sofifi/domain/aritmetica.py.
// Suma de hasta 50 bit → ACC de 48 bit, saturando.
`default_nettype none

module saturar_acc (
    input  wire signed [49:0] valor,
    output wire signed [47:0] acc
);
    assign acc = (valor > 50'sh7FFFFFFFFFFF)  ? 48'sh7FFFFFFFFFFF :
                 (valor < -50'sh800000000000) ? 48'sh800000000000 : valor[47:0];
endmodule

`default_nettype wire
