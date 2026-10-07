// SPDX-License-Identifier: MIT
//
// Prueba del PLL (Fase 03). Cuenta los ciclos de 100 MHz durante un segundo del
// cristal de 50 MHz y envía cada segundo "P <bloqueado><cuenta>\r\n" por la UART.
// Lo esperado: bloqueado = 1 y cuenta = 100 000 000 ± 100 (0x05F5E100).
`default_nettype none

module prueba_pll #(
    parameter integer F_RELOJ = 50_000_000,
    parameter integer BAUDIOS = 115_200
) (
    input  wire clk,      // 50 MHz (E2)
    input  wire rst_n,
    output wire uart_tx
);
    /* verilator lint_off PROCASSINIT */
    reg [3:0] arranque = 4'd0;
    /* verilator lint_on PROCASSINIT */
    wire rst = ~arranque[3] | ~rst_n;
    always @(posedge clk) if (!arranque[3]) arranque <= arranque + 1'b1;

    wire clk_100, bloqueado;
    pll_100 u_pll (.clk_50(clk), .clk_100(clk_100), .bloqueado(bloqueado));

    wire [31:0] cuenta;
    wire        nueva;
    medidor_frecuencia #(.VENTANA(F_RELOJ)) u_med (
        .clk_ref(clk), .rst_ref(rst), .clk_medido(clk_100), .cuenta(cuenta), .nueva(nueva)
    );

    // El PLL está en otro dominio: `bloqueado` se sincroniza antes de usarlo.
    (* ASYNC_REG = "TRUE" *) reg [1:0] bloq_s;
    always @(posedge clk) bloq_s <= {bloq_s[0], bloqueado};

    /* verilator lint_off UNUSEDSIGNAL */
    wire ocupado;   // un informe por segundo: nunca se solapan
    /* verilator lint_on UNUSEDSIGNAL */
    linea_hex #(.DIGITOS(9), .DIVISOR(F_RELOJ / BAUDIOS)) u_linea (
        .clk(clk), .rst(rst), .inicio(nueva), .etiqueta("P"),
        .valor({3'b000, bloq_s[1], cuenta}), .ocupado(ocupado), .tx(uart_tx)
    );
endmodule

`default_nettype wire
