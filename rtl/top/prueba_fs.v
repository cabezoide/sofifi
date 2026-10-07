// SPDX-License-Identifier: MIT
//
// Prueba del reloj de muestra y de la recepción UART (Fase 05), a 100 MHz:
//
//   - cuenta los ticks de muestra durante 100 000 000 ciclos del PLL (1 s, porque
//     el PLL va exacto respecto al cristal, MED-08) y envía "S <8 hex>\r\n";
//     lo esperado es 48 828 o 48 829 (48 828,125 Hz);
//   - cada byte recibido por la UART se devuelve como "R <8 hex>\r\n". Solo hay
//     un eco pendiente: los bytes deben llegar con más de ~1,1 ms entre ellos.
`default_nettype none

module prueba_fs #(
    parameter integer F_RELOJ = 100_000_000,
    parameter integer BAUDIOS = 115_200
) (
    input  wire clk,      // 50 MHz (E2)
    input  wire rst_n,
    input  wire uart_rx,
    output wire uart_tx
);
    wire clk_100, bloqueado;
    pll_100 u_pll (.clk_50(clk), .clk_100(clk_100), .bloqueado(bloqueado));

    (* ASYNC_REG = "TRUE" *) reg [2:0] rst_s;
    /* verilator lint_off PROCASSINIT */
    reg [3:0] arranque = 4'd0;
    /* verilator lint_on PROCASSINIT */
    always @(posedge clk_100) begin
        rst_s <= {rst_s[1:0], ~(bloqueado & rst_n)};
        if (!arranque[3]) arranque <= arranque + 1'b1;
    end
    wire rst = rst_s[2] | ~arranque[3];

    wire tick;
    generador_muestra u_gen (.clk(clk_100), .activo(~rst), .tick(tick));

    // Ticks en una ventana de F_RELOJ ciclos.
    localparam integer AV = $clog2(F_RELOJ);
    reg [AV-1:0] ventana;
    reg [31:0]   ticks, medida;
    reg          nueva;
    always @(posedge clk_100) begin
        nueva <= 1'b0;
        if (rst) begin
            ventana <= {AV{1'b0}}; ticks <= 32'd0; medida <= 32'd0;
        end else if (ventana == AV'(F_RELOJ - 1)) begin
            ventana <= {AV{1'b0}};
            medida  <= ticks + {31'd0, tick};
            ticks   <= 32'd0;
            nueva   <= 1'b1;
        end else begin
            ventana <= ventana + 1'b1;
            ticks   <= ticks + {31'd0, tick};
        end
    end

    // Eco de lo recibido y medida: una sola UART de salida, con prioridad al eco.
    wire [7:0] recibido;
    wire       recibido_ok;
    uart_rx #(.DIVISOR(F_RELOJ / BAUDIOS)) u_rx (
        .clk(clk_100), .rst(rst), .rx(uart_rx), .dato(recibido), .valido(recibido_ok)
    );
    reg [7:0]  eco;
    reg        eco_pend, medida_pend;
    reg        inicio;
    reg [7:0]  etiqueta;
    reg [31:0] valor;
    wire       ocupado;
    always @(posedge clk_100) begin
        inicio <= 1'b0;
        if (rst) begin
            eco_pend <= 1'b0; medida_pend <= 1'b0;
        end else begin
            if (recibido_ok) begin eco <= recibido; eco_pend <= 1'b1; end
            if (nueva) medida_pend <= 1'b1;
            if (!ocupado && !inicio) begin
                if (eco_pend) begin
                    etiqueta <= "R"; valor <= {24'd0, eco}; inicio <= 1'b1; eco_pend <= 1'b0;
                end else if (medida_pend) begin
                    etiqueta <= "S"; valor <= medida; inicio <= 1'b1; medida_pend <= 1'b0;
                end
            end
        end
    end
    linea_hex #(.DIGITOS(8), .DIVISOR(F_RELOJ / BAUDIOS)) u_linea (
        .clk(clk_100), .rst(rst), .inicio(inicio), .etiqueta(etiqueta),
        .valor(valor), .ocupado(ocupado), .tx(uart_tx)
    );
endmodule

`default_nettype wire
