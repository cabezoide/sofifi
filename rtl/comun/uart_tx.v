// SPDX-License-Identifier: MIT
//
// UART de transmisión 8N1. Envía `dato` cuando `valido` y `listo` coinciden en
// un flanco de reloj (handshake valido/listo). DIVISOR = f_reloj / baudios.
`default_nettype none

module uart_tx #(
    parameter integer DIVISOR = 434  // 50 MHz / 115 200
) (
    input  wire       clk,
    input  wire       rst,
    input  wire [7:0] dato,
    input  wire       valido,
    output wire       listo,
    output reg        tx
);
    localparam integer ANCHO = $clog2(DIVISOR);

    reg [ANCHO-1:0] cuenta;
    reg [3:0]       bit_idx;   // 0 = reposo; 1..10 = start, 8 datos, stop
    reg [9:0]       trama;

    assign listo = (bit_idx == 4'd0);

    always @(posedge clk) begin
        if (rst) begin
            tx      <= 1'b1;
            bit_idx <= 4'd0;
            cuenta  <= {ANCHO{1'b0}};
            trama   <= 10'h3FF;
        end else if (bit_idx == 4'd0) begin
            tx <= 1'b1;
            if (valido) begin
                trama   <= {1'b1, dato, 1'b0};
                bit_idx <= 4'd1;
                cuenta  <= {ANCHO{1'b0}};
            end
        end else begin
            tx <= trama[0];
            if (cuenta == ANCHO'(DIVISOR - 1)) begin
                cuenta  <= {ANCHO{1'b0}};
                trama   <= {1'b1, trama[9:1]};
                bit_idx <= (bit_idx == 4'd10) ? 4'd0 : bit_idx + 4'd1;
            end else begin
                cuenta <= cuenta + 1'b1;
            end
        end
    end
endmodule

`default_nettype wire
