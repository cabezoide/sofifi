// SPDX-License-Identifier: MIT
//
// Reloj de muestra del núcleo (ADR 0005): un pulso `tick` cada 2 048 ciclos de
// 100 MHz, es decir 48 828,125 Hz exactos. Con `activo` a 0 se para y se pone a
// cero, para que la primera muestra llegue 2 048 ciclos después de activarlo.
`default_nettype none

module generador_muestra (
    input  wire clk,
    input  wire activo,
    output reg  tick
);
    reg [10:0] fase;
    always @(posedge clk) begin
        tick <= 1'b0;
        if (!activo) fase <= 11'd0;
        else begin
            fase <= fase + 1'b1;
            tick <= (fase == 11'd2047);
        end
    end
endmodule

`default_nettype wire
