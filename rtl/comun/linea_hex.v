// SPDX-License-Identifier: MIT
//
// Envía por la UART una línea "<etiqueta> <valor en hexadecimal>\r\n".
// Un pulso en `inicio` con `ocupado` a 0 captura `etiqueta` y `valor`.
// Mientras envía, `ocupado` está a 1. El banco de pruebas de la Fase 03 lo usa
// para que el PC compruebe cada resultado.
`default_nettype none

module linea_hex #(
    parameter integer DIGITOS = 8,    // dígitos hexadecimales del valor
    parameter integer DIVISOR = 868   // f_reloj / baudios (100 MHz / 115 200)
) (
    input  wire                 clk,
    input  wire                 rst,
    input  wire                 inicio,
    input  wire [7:0]           etiqueta,
    input  wire [4*DIGITOS-1:0] valor,
    output wire                 ocupado,
    output wire                 tx
);
    // Caracteres de la línea: etiqueta, espacio, DIGITOS dígitos, CR y LF.
    localparam integer TOTAL = DIGITOS + 4;
    localparam integer ANCHO = $clog2(TOTAL + 1);

    reg [7:0]           etiqueta_r;
    reg [4*DIGITOS-1:0] valor_r;
    reg [ANCHO-1:0]     idx;        // carácter en curso; TOTAL = en reposo
    reg [7:0]           caracter;
    wire                listo;

    assign ocupado = (idx != ANCHO'(TOTAL));

    // El dígito idx-2 es el nibble más alto que queda: se desplaza `valor_r`.
    wire [3:0] nibble = valor_r[4*DIGITOS-1 -: 4];
    wire [7:0] digito = (nibble < 4'd10) ? (8'h30 | {4'h0, nibble}) : (8'h37 + {4'h0, nibble});

    always @(*) begin
        if (idx == {ANCHO{1'b0}})          caracter = etiqueta_r;
        else if (idx == ANCHO'(1))         caracter = 8'h20;
        else if (idx == ANCHO'(TOTAL - 2)) caracter = 8'h0D;
        else if (idx == ANCHO'(TOTAL - 1)) caracter = 8'h0A;
        else                               caracter = digito;
    end

    always @(posedge clk) begin
        if (rst) begin
            idx <= ANCHO'(TOTAL);
        end else if (!ocupado) begin
            if (inicio) begin
                etiqueta_r <= etiqueta;
                valor_r    <= valor;
                idx        <= {ANCHO{1'b0}};
            end
        end else if (listo) begin
            // El carácter en curso entra en la UART en este flanco.
            if (idx >= ANCHO'(2) && idx < ANCHO'(TOTAL - 2))
                valor_r <= {valor_r[4*DIGITOS-5:0], 4'h0};
            idx <= idx + 1'b1;
        end
    end

    uart_tx #(.DIVISOR(DIVISOR)) u_tx (
        .clk(clk), .rst(rst), .dato(caracter), .valido(ocupado), .listo(listo), .tx(tx)
    );
endmodule

`default_nettype wire
