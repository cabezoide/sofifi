// SPDX-License-Identifier: MIT
//
// Multiplicador con signo de 27 × 18 bit, con latencia de 2 ciclos: registra
// las entradas y la salida. Envuelve el bloque DSP del GW5A (rtl/AGENTS.md).
//
// Yosys no infiere bloques DSP para la familia gw5a, así que se instancia
// MULT27X36. Ocupa 2 de los 28 bloques MULTALU27X18 (Fase 03).
// Con SIMULACION definido se usa el modelo de comportamiento equivalente.
`default_nettype none

module mult_27x18 (
    input  wire               clk,
    input  wire               ce,
    input  wire signed [26:0] a,
    input  wire signed [17:0] b,
    output wire signed [44:0] p
);
`ifdef SIMULACION
    reg signed [26:0] a_r;
    reg signed [17:0] b_r;
    reg signed [44:0] p_r;
    always @(posedge clk) begin
        if (ce) begin
            a_r <= a;
            b_r <= b;
            p_r <= a_r * b_r;
        end
    end
    assign p = p_r;
`else
    wire [62:0] dout;
    MULT27X36 #(
        .AREG_CLK("CLK0"), .BREG_CLK("CLK0"), .OREG_CLK("CLK0")
    ) u_mult (
        .DOUT(dout), .A(a), .B({{18{b[17]}}, b}), .D(26'd0),
        .CLK({1'b0, clk}), .CE({1'b0, ce}), .RESET(2'b00),
        .PSEL(1'b0), .PADDSUB(1'b0)
    );
    assign p = dout[44:0];
`endif
endmodule

`default_nettype wire
