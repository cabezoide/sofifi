// SPDX-License-Identifier: MIT
//
// Registro de ANCHO bit que Yosys no fusiona con otro igual. Sirve para
// repartir una señal de gran fan-out en copias, cada una cerca de sus destinos
// (fails.md, F-15). Yosys fusiona registros iguales aunque lleven `keep` en el
// `reg`; con `keep` en la instancia de la primitiva DFF del GW5A, no.
`default_nettype none

module registro_copia #(
    parameter integer ANCHO = 1
) (
    input  wire             clk,
    input  wire [ANCHO-1:0] d,
    output wire [ANCHO-1:0] q
);
`ifdef SIMULACION
    reg [ANCHO-1:0] r;
    always @(posedge clk) r <= d;
    assign q = r;
`else
    genvar i;
    generate
        for (i = 0; i < ANCHO; i = i + 1) begin : g_bit
            (* keep *) DFF u_dff (.D(d[i]), .CLK(clk), .Q(q[i]));
        end
    endgenerate
`endif
endmodule

`default_nettype wire
