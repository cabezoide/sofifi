// SPDX-License-Identifier: MIT
//
// hil_nucleo con la ROM que escribe `sofifi rom` en build/programa_hil.v: un
// programa o una cadena cualquiera en la placa. Mismo protocolo y mismo
// estímulo. `make hil HIL=NOMBRE` genera la ROM, sintetiza, carga y compara
// con el modelo (scripts/hil_nucleo.py --programa NOMBRE).
//
// No está en tops.txt: su ROM no está en el repositorio. La simulación
// (sim/top/hil_nucleo_test.py) la genera con una cadena.
`default_nettype none

module hil_programa (
    input  wire clk,
    input  wire rst_n,
    input  wire uart_rx,
    output wire uart_tx
);
    hil_nucleo #(.PROGRAMA("hil")) u_hil (
        .clk(clk), .rst_n(rst_n), .uart_rx(uart_rx), .uart_tx(uart_tx)
    );
endmodule

`default_nettype wire
