// SPDX-License-Identifier: MIT
//
// Multiplicador con signo de 27 × 36 bit, con latencia de 3 ciclos: registra
// las entradas, el producto (PREG) y la salida. Son dos bloques DSP en cadena:
// sin PREG, el producto no llegaba a 133 MHz en el silicio (fails.md, F-15). Es el único multiplicador del núcleo: cubre
// dato × coeficiente (24 × 18) y dato × dato (24 × 24, para MULX, CLIP y la
// ventana de CHO). Envuelve el bloque DSP del GW5A (rtl/AGENTS.md).
//
// Yosys no infiere bloques DSP para la familia gw5a: se instancia MULT27X36,
// que ocupa 2 de los 28 bloques MULTALU27X18 (Fase 03).
`default_nettype none

module mult_27x36 (
    input  wire               clk,
    input  wire signed [26:0] a,
    input  wire signed [35:0] b,
    output wire signed [62:0] p
);
`ifdef SIMULACION
    reg signed [26:0] a_r;
    reg signed [35:0] b_r;
    reg signed [62:0] prod_r, p_r;
    always @(posedge clk) begin
        a_r    <= a;
        b_r    <= b;
        prod_r <= a_r * b_r;
        p_r    <= prod_r;
    end
    assign p = p_r;
`else
    MULT27X36 #(
        .AREG_CLK("CLK0"), .BREG_CLK("CLK0"), .PREG_CLK("CLK0"), .OREG_CLK("CLK0")
    ) u_mult (
        .DOUT(p), .A(a), .B(b), .D(26'd0),
        .CLK({1'b0, clk}), .CE(2'b01), .RESET(2'b00),
        .PSEL(1'b0), .PADDSUB(1'b0)
    );
`endif
endmodule

`default_nettype wire
