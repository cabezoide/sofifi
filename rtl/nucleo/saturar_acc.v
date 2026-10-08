// SPDX-License-Identifier: MIT
//
// Conversión de formato del núcleo (ADR 0008), equivalente bit a bit a la
// función del mismo nombre de model/sofifi/domain/aritmetica.py.
// Suma de hasta 50 bit → ACC de 48 bit, saturando.
//
// El valor cabe en 48 bit si sus tres bits altos son iguales (extensión de
// signo). Mirar esos tres bits sustituye a dos comparaciones de 50 bit: cada
// una era otra cadena de acarreo detrás de la suma, en el bucle del ACC del
// núcleo segmentado (ADR 0014).
`default_nettype none

module saturar_acc (
    input  wire signed [49:0] valor,
    output wire signed [47:0] acc
);
    wire cabe = (valor[49:47] == 3'b000) || (valor[49:47] == 3'b111);
    assign acc = cabe ? valor[47:0] : (valor[49] ? 48'sh800000000000 : 48'sh7FFFFFFFFFFF);
endmodule

`default_nettype wire
