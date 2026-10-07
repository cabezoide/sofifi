// SPDX-License-Identifier: MIT
//
// Memoria de doble puerto: un puerto de escritura y uno de lectura, en el mismo
// reloj. La lectura tarda 1 ciclo. Si las dos direcciones coinciden en el mismo
// ciclo, la lectura devuelve el dato ANTERIOR a la escritura.
//
// Yosys la infiere como bloques DPX9B del GW5A (1 024 × 18 por bloque).
`default_nettype none

module bsram_dp #(
    parameter integer PALABRAS = 1024,
    parameter integer ANCHO    = 18
) (
    input  wire                        clk,
    input  wire                        we,
    input  wire [$clog2(PALABRAS)-1:0] dir_w,
    input  wire [ANCHO-1:0]            dato_w,
    input  wire [$clog2(PALABRAS)-1:0] dir_r,
    output reg  [ANCHO-1:0]            dato_r
);
    reg [ANCHO-1:0] mem [0:PALABRAS-1];

    always @(posedge clk) begin
        if (we) mem[dir_w] <= dato_w;
        dato_r <= mem[dir_r];
    end
endmodule

`default_nettype wire
