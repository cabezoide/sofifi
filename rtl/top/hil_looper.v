// SPDX-License-Identifier: MIT
//
// hil_nucleo con el looper (Fase 07): prueba RDAA y WRAA en la placa. Mismo
// protocolo y mismo estímulo; scripts/hil_nucleo.py --programa looper lo
// compara con el modelo.
`default_nettype none

module hil_looper (
    input  wire clk,
    input  wire rst_n,
    input  wire uart_rx,
    output wire uart_tx
);
    hil_nucleo #(.PROGRAMA("looper")) u_hil (
        .clk(clk), .rst_n(rst_n), .uart_rx(uart_rx), .uart_tx(uart_tx)
    );
endmodule

`default_nettype wire
