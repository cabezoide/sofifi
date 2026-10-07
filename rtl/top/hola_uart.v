// SPDX-License-Identifier: MIT
//
// Primer bitstream (Fase 02): envía "SOFIFI xxxxxxxx\r\n" una vez por segundo por
// la UART del depurador BL616 (115 200 8N1), con un contador en hexadecimal.
// Sirve para demostrar la cadena EDA abierta de extremo a extremo.
`default_nettype none

module hola_uart (
    input  wire clk,      // 50 MHz (E2)
    input  wire rst_n,    // botón de la Dock, activo en bajo
    output wire uart_tx
);
    localparam integer F_RELOJ = 50_000_000;

    // Reset síncrono a partir del botón y de un contador de arranque.
    // La FPGA carga los valores iniciales al configurarse: es el reset de arranque.
    /* verilator lint_off PROCASSINIT */
    reg [3:0] arranque = 4'd0;
    /* verilator lint_on PROCASSINIT */
    wire rst = ~arranque[3] | ~rst_n;
    always @(posedge clk) if (!arranque[3]) arranque <= arranque + 1'b1;

    reg [25:0] segundo;
    reg [31:0] contador;
    reg [4:0]  idx;          // carácter en curso; 17 = en reposo
    reg        enviando;
    wire       listo;
    reg  [7:0] caracter;

    // Se elige primero el nibble y se convierte una sola vez: con una conversión
    // por nibble, yosys sintetizaba 16 sumadores en paralelo (Fase 02).
    reg  [3:0] nibble;
    reg  [7:0] digito;
    always @(*) begin
        case (idx[2:0] - 3'd7)  // idx 7..14 → nibble 0 (el más alto) .. 7
            3'd0:    nibble = contador[31:28];
            3'd1:    nibble = contador[27:24];
            3'd2:    nibble = contador[23:20];
            3'd3:    nibble = contador[19:16];
            3'd4:    nibble = contador[15:12];
            3'd5:    nibble = contador[11:8];
            3'd6:    nibble = contador[7:4];
            default: nibble = contador[3:0];
        endcase
        case (nibble)
            4'h0: digito = "0";  4'h1: digito = "1";  4'h2: digito = "2";  4'h3: digito = "3";
            4'h4: digito = "4";  4'h5: digito = "5";  4'h6: digito = "6";  4'h7: digito = "7";
            4'h8: digito = "8";  4'h9: digito = "9";  4'hA: digito = "A";  4'hB: digito = "B";
            4'hC: digito = "C";  4'hD: digito = "D";  4'hE: digito = "E";  default: digito = "F";
        endcase
    end

    always @(*) begin
        case (idx)
            5'd0:  caracter = "S";
            5'd1:  caracter = "O";
            5'd2:  caracter = "F";
            5'd3:  caracter = "I";
            5'd4:  caracter = "F";
            5'd5:  caracter = "I";
            5'd6:  caracter = " ";
            5'd7, 5'd8, 5'd9, 5'd10, 5'd11, 5'd12, 5'd13, 5'd14: caracter = digito;
            5'd15: caracter = 8'h0D;
            default: caracter = 8'h0A;
        endcase
    end

    always @(posedge clk) begin
        if (rst) begin
            segundo  <= 26'd0;
            contador <= 32'd0;
            idx      <= 5'd0;
            enviando <= 1'b0;
        end else begin
            if (segundo == 26'(F_RELOJ - 1)) begin
                segundo  <= 26'd0;
                enviando <= 1'b1;
                idx      <= 5'd0;
            end else begin
                segundo <= segundo + 1'b1;
            end
            if (enviando && listo) begin
                if (idx == 5'd16) begin
                    enviando <= 1'b0;
                    contador <= contador + 1'b1;
                end
                idx <= idx + 1'b1;
            end
        end
    end

    uart_tx #(.DIVISOR(F_RELOJ / 115_200)) u_tx (
        .clk(clk), .rst(rst), .dato(caracter), .valido(enviando), .listo(listo), .tx(uart_tx)
    );
endmodule

`default_nettype wire
