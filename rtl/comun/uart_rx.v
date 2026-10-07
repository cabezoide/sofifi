// SPDX-License-Identifier: MIT
//
// UART de recepción 8N1. Sincroniza `rx` (2 etapas), detecta el bit de start y
// muestrea cada bit en su centro. `valido` da un pulso de un ciclo con `dato`.
// Un byte con el bit de stop a 0 se descarta (error de trama).
// DIVISOR = f_reloj / baudios.
`default_nettype none

module uart_rx #(
    parameter integer DIVISOR = 868   // 100 MHz / 115 200
) (
    input  wire       clk,
    input  wire       rst,
    input  wire       rx,
    output reg  [7:0] dato,
    output reg        valido
);
    localparam integer ANCHO = $clog2(DIVISOR);

    (* ASYNC_REG = "TRUE" *) reg [1:0] rx_s;
    always @(posedge clk) rx_s <= {rx_s[0], rx};
    wire linea = rx_s[1];

    reg [ANCHO-1:0] cuenta;
    reg [3:0]       bit_idx;   // 0 = reposo; 1 = start; 2..9 = datos; 10 = stop
    reg [7:0]       registro;

    always @(posedge clk) begin
        valido <= 1'b0;
        if (rst) begin
            bit_idx <= 4'd0;
            cuenta  <= {ANCHO{1'b0}};
        end else if (bit_idx == 4'd0) begin
            if (!linea) begin                       // flanco de start
                bit_idx <= 4'd1;
                cuenta  <= ANCHO'(DIVISOR / 2);     // ir al centro del bit
            end
        end else if (cuenta != {ANCHO{1'b0}}) begin
            cuenta <= cuenta - 1'b1;
        end else begin
            cuenta <= ANCHO'(DIVISOR - 1);
            case (bit_idx)
                4'd1:  bit_idx <= linea ? 4'd0 : 4'd2;   // start falso: reposo
                4'd10: begin
                    if (linea) begin dato <= registro; valido <= 1'b1; end
                    bit_idx <= 4'd0;
                end
                default: begin
                    registro <= {linea, registro[7:1]};
                    bit_idx  <= bit_idx + 1'b1;
                end
            endcase
        end
    end
endmodule

`default_nettype wire
