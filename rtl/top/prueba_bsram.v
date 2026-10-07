// SPDX-License-Identifier: MIT
//
// Prueba de la BSRAM (Fase 03), a 100 MHz, con el tamaño real de la memoria de
// retardo del núcleo: 43 008 palabras de 18 bit (42 bloques). Cada vuelta tiene
// tres pasadas sobre todas las direcciones:
//
//   A. Escribe patrón(d, s) en d y lee d-1: el dato recién escrito debe estar.
//   B. Escribe patrón(d, ~s) en d y lee d en el mismo ciclo: debe salir el dato
//      ANTERIOR, patrón(d, s), como en el modelo (bsram_dp.v).
//   C. Lee todas las direcciones: debe salir patrón(d, ~s).
//
// patrón(d, s) = d ^ s, con s distinta en cada vuelta. Cada VUELTAS vueltas envía
// "B <errA><errB><nuevosB><errC><vuelta>\r\n", 5 campos de 4 dígitos. Los errores
// se acumulan entre informes y saturan en FFFF. nuevosB cuenta las colisiones que
// devolvieron el dato NUEVO.
//
// Un informe por vuelta saturaría la UART (unos 19 kB/s), y a pleno caudal el
// puente del BL616 se cuelga si el PC deja de leer (Fase 03).
`default_nettype none

module prueba_bsram #(
    parameter integer F_RELOJ  = 100_000_000,
    parameter integer BAUDIOS  = 115_200,
    parameter integer PALABRAS = 43_008,
    parameter integer VUELTAS  = 64       // vueltas por informe (2^n)
) (
    input  wire clk,      // 50 MHz (E2)
    input  wire rst_n,
    output wire uart_tx
);
    localparam integer AD = $clog2(PALABRAS);

    wire clk_100, bloqueado;
    pll_100 u_pll (.clk_50(clk), .clk_100(clk_100), .bloqueado(bloqueado));

    // Reset síncrono en el dominio de 100 MHz: al configurar la FPGA (contador
    // de arranque) y mientras el PLL no esté bloqueado o se pulse el botón.
    (* ASYNC_REG = "TRUE" *) reg [2:0] rst_s;
    /* verilator lint_off PROCASSINIT */
    reg [3:0] arranque = 4'd0;
    /* verilator lint_on PROCASSINIT */
    always @(posedge clk_100) begin
        rst_s <= {rst_s[1:0], ~(bloqueado & rst_n)};
        if (!arranque[3]) arranque <= arranque + 1'b1;
    end
    wire rst = rst_s[2] | ~arranque[3];

    reg  [1:0]    pasada;     // 0 = A, 1 = B, 2 = C, 3 = informe
    reg  [AD-1:0] dir;
    reg  [17:0]   semilla;
    reg  [15:0]   vuelta;
    wire [17:0]   dir18 = {{(18-AD){1'b0}}, dir};

    reg           we;
    reg  [AD-1:0] dir_w, dir_r;
    reg  [17:0]   dato_w;
    wire [17:0]   dato_r;
    bsram_dp #(.PALABRAS(PALABRAS), .ANCHO(18)) u_mem (
        .clk(clk_100), .we(we), .dir_w(dir_w), .dato_w(dato_w),
        .dir_r(dir_r), .dato_r(dato_r)
    );

    // Lo que debe salir de cada lectura. Las direcciones se registran en un ciclo
    // y la memoria entrega el dato en el siguiente: lo esperado espera 2 ciclos.
    reg        comprobar, comprobar_2;
    reg [1:0]  pasada_c, pasada_2;
    reg [17:0] esperado, nuevo, esperado_2, nuevo_2;
    reg [15:0] err_a, err_b, nuevos_b, err_c;

    reg  inicio;
    wire ocupado;

    always @(posedge clk_100) begin
        we          <= 1'b0;
        comprobar   <= 1'b0;
        inicio      <= 1'b0;
        comprobar_2 <= comprobar;
        pasada_2    <= pasada_c;
        esperado_2  <= esperado;
        nuevo_2     <= nuevo;
        if (rst) begin
            pasada <= 2'd0; dir <= {AD{1'b0}};
            semilla <= 18'h2A5A5; vuelta <= 16'd0;
            err_a <= 16'd0; err_b <= 16'd0; nuevos_b <= 16'd0; err_c <= 16'd0;
        end else begin
            if (comprobar_2 && dato_r != esperado_2) begin
                case (pasada_2)
                    2'd0: if (~&err_a) err_a <= err_a + 1'b1;
                    2'd1: begin
                        if (~&err_b) err_b <= err_b + 1'b1;
                        if (dato_r == nuevo_2 && ~&nuevos_b) nuevos_b <= nuevos_b + 1'b1;
                    end
                    default: if (~&err_c) err_c <= err_c + 1'b1;
                endcase
            end
            if (pasada != 2'd3) begin
                pasada_c <= pasada;
                case (pasada)
                    2'd0: begin
                        we <= 1'b1; dir_w <= dir; dato_w <= dir18 ^ semilla;
                        dir_r <= dir - 1'b1;
                        esperado <= (dir18 - 1'b1) ^ semilla;
                        comprobar <= (dir != {AD{1'b0}});
                    end
                    2'd1: begin
                        we <= 1'b1; dir_w <= dir; dato_w <= dir18 ^ ~semilla;
                        dir_r <= dir;
                        esperado <= dir18 ^ semilla;
                        nuevo <= dir18 ^ ~semilla;
                        comprobar <= 1'b1;
                    end
                    default: begin
                        dir_r <= dir;
                        esperado <= dir18 ^ ~semilla;
                        comprobar <= 1'b1;
                    end
                endcase
                if (dir == AD'(PALABRAS - 1)) begin
                    dir <= {AD{1'b0}};
                    pasada <= pasada + 1'b1;
                end else begin
                    dir <= dir + 1'b1;
                end
            end else if (comprobar || comprobar_2) begin
                // Esperar a que terminen las últimas comprobaciones de la pasada C.
            end else if (vuelta[$clog2(VUELTAS)-1:0] != '1) begin
                vuelta <= vuelta + 1'b1;
                semilla <= {semilla[16:0], semilla[17] ^ semilla[10]};
                pasada <= 2'd0;
            end else if (!ocupado && !inicio) begin
                inicio <= 1'b1;
            end else if (inicio) begin
                // El informe ya se capturó: errores a cero y otra vuelta.
                err_a <= 16'd0; err_b <= 16'd0; nuevos_b <= 16'd0; err_c <= 16'd0;
                vuelta <= vuelta + 1'b1;
                semilla <= {semilla[16:0], semilla[17] ^ semilla[10]};
                pasada <= 2'd0;
            end
        end
    end

    linea_hex #(.DIGITOS(20), .DIVISOR(F_RELOJ / BAUDIOS)) u_linea (
        .clk(clk_100), .rst(rst), .inicio(inicio), .etiqueta("B"),
        .valor({err_a, err_b, nuevos_b, err_c, vuelta}), .ocupado(ocupado), .tx(uart_tx)
    );
endmodule

`default_nettype wire
