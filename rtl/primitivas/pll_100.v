// SPDX-License-Identifier: MIT
//
// Reloj de 100 MHz desde el cristal de 50 MHz de la Tang Primer 25K.
// Envuelve el PLLA del GW5A (rtl/AGENTS.md).
//
// VCO = 50 MHz × FBDIV × MDIV / IDIV = 50 × 1 × 16 / 1 = 800 MHz.
// Salida = VCO / ODIV0 = 800 / 8 = 100 MHz.
//
// apicula 0.32 guarda en decimal los valores por defecto del PLLA ('8') y los
// lee como binario: gowin_pack falla con «invalid literal for int() with base
// 2: '8'». Por eso se fijan también los divisores de las salidas sin usar.
//
// Con SIMULACION definido, la salida es la entrada y `bloqueado` vale 1: la
// simulación no puede verificar la frecuencia. Eso lo hace la placa (Fase 03).
`default_nettype none

module pll_100 (
    input  wire clk_50,
    output wire clk_100,
    output wire bloqueado
);
`ifdef SIMULACION
    assign clk_100   = clk_50;
    assign bloqueado = 1'b1;
`else
    PLLA #(
        .FCLKIN("50"), .IDIV_SEL(1), .FBDIV_SEL(1), .MDIV_SEL(16),
        .ODIV0_SEL(8), .ODIV1_SEL(8), .ODIV2_SEL(8), .ODIV3_SEL(8),
        .ODIV4_SEL(8), .ODIV5_SEL(8), .ODIV6_SEL(8), .CLKOUT0_EN("TRUE")
    ) u_pll (
        .CLKIN(clk_50), .CLKFB(1'b0), .RESET(1'b0), .PLLPWD(1'b0),
        .RESET_I(1'b0), .RESET_O(1'b0),
        .PSSEL(3'd0), .PSDIR(1'b0), .PSPULSE(1'b0),
        .SSCPOL(1'b0), .SSCON(1'b0), .SSCMDSEL(7'd0), .SSCMDSEL_FRAC(3'd0),
        .MDCLK(1'b0), .MDOPC(2'd0), .MDAINC(1'b0), .MDWDI(8'd0),
        .MDRDO(), .LOCK(bloqueado), .CLKOUT0(clk_100),
        .CLKOUT1(), .CLKOUT2(), .CLKOUT3(), .CLKOUT4(), .CLKOUT5(), .CLKOUT6(),
        .CLKFBOUT()
    );
`endif
endmodule

`default_nettype wire
