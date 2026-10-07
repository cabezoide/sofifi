// SPDX-License-Identifier: MIT
//
// Prueba del bloque DSP (Fase 03), a 100 MHz. Multiplica pares (a, b) con signo
// de 27 × 18 bit y envía cada resultado como "D <a><b><p>\r\n": a en 7 dígitos,
// b en 5 y p en 12, todos con extensión de signo. El PC comprueba p = a·b.
// Cada vuelta empieza con 25 casos extremos (0, 1, -1, máximo y mínimo de cada
// operando) y sigue con 1 024 pares pseudoaleatorios de un xorshift de 64 bit.
// Así el PC ve los casos extremos aunque empiece a leer a mitad.
//
// Entre línea y línea hay una pausa (PAUSA ciclos, unas 50 líneas por segundo).
// A pleno caudal, el puente UART del BL616 se cuelga si el PC deja de leer
// (Fase 03): hay que reconectar el USB para recuperarlo.
`default_nettype none

module prueba_dsp #(
    parameter integer F_RELOJ = 100_000_000,   // reloj del núcleo, desde el PLL
    parameter integer BAUDIOS = 115_200,
    parameter integer PAUSA   = 2_000_000   // ciclos entre líneas: 20 ms a 100 MHz
) (
    input  wire clk,      // 50 MHz (E2)
    input  wire rst_n,
    output wire uart_tx
);
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

    reg  signed [26:0] a;
    reg  signed [17:0] b;
    wire signed [44:0] p;
    mult_27x18 u_mult (.clk(clk_100), .ce(1'b1), .a(a), .b(b), .p(p));

    // Casos extremos: índice i de 0 a 24, a = A[i / 5] y b = B[i % 5].
    reg [2:0] ia, ib;
    reg       extremos;
    reg [9:0] aleatorios;   // pares aleatorios enviados en esta vuelta
    reg [26:0] a_ext;
    reg [17:0] b_ext;
    always @(*) begin
        case (ia)
            3'd0: a_ext = 27'h0000000;  3'd1: a_ext = 27'h0000001;
            3'd2: a_ext = 27'h7FFFFFF;  3'd3: a_ext = 27'h3FFFFFF;
            default: a_ext = 27'h4000000;
        endcase
        case (ib)
            3'd0: b_ext = 18'h00000;  3'd1: b_ext = 18'h00001;
            3'd2: b_ext = 18'h3FFFF;  3'd3: b_ext = 18'h1FFFF;
            default: b_ext = 18'h20000;
        endcase
    end

    reg [63:0] azar;
    wire [63:0] azar_1 = azar ^ (azar << 13);
    wire [63:0] azar_2 = azar_1 ^ (azar_1 >> 7);
    wire [63:0] azar_3 = azar_2 ^ (azar_2 << 17);

    reg  [1:0] espera;       // ciclos desde que a y b cambian (latencia 2)
    reg  [$clog2(PAUSA+1)-1:0] pausa;
    reg        inicio;
    wire       ocupado;

    always @(posedge clk_100) begin
        inicio <= 1'b0;
        if (rst) begin
            ia <= 3'd0; ib <= 3'd0; extremos <= 1'b1; aleatorios <= 10'd0;
            azar <= 64'h9E3779B97F4A7C15;
            a <= 27'sd0; b <= 18'sd0; espera <= 2'd0; pausa <= '0;
        end else if (pausa != '0) begin
            pausa <= pausa - 1'b1;
        end else if (espera != 2'd3) begin
            if (espera == 2'd0) begin
                a <= extremos ? a_ext : azar[26:0];
                b <= extremos ? b_ext : azar[49:32];
            end
            espera <= espera + 1'b1;
        end else if (!ocupado && !inicio) begin
            // p ya corresponde a (a, b): se envía y se prepara el siguiente par.
            inicio <= 1'b1;
            espera <= 2'd0;
            pausa  <= ($clog2(PAUSA+1))'(PAUSA);
            if (extremos) begin
                if (ib == 3'd4) begin
                    ib <= 3'd0;
                    if (ia == 3'd4) begin
                        extremos <= 1'b0;
                        ia <= 3'd0;
                    end else begin
                        ia <= ia + 1'b1;
                    end
                end else begin
                    ib <= ib + 1'b1;
                end
            end else begin
                azar <= azar_3;
                aleatorios <= aleatorios + 1'b1;
                if (aleatorios == 10'd1023) extremos <= 1'b1;
            end
        end
    end

    // Se captura (a, b, p) en el flanco del inicio, antes de cambiar a y b.
    reg [95:0] valor;
    always @(posedge clk_100)
        if (espera == 2'd3 && !ocupado && !inicio)
            valor <= {{1{a[26]}}, a, {2{b[17]}}, b, {3{p[44]}}, p};

    linea_hex #(.DIGITOS(24), .DIVISOR(F_RELOJ / BAUDIOS)) u_linea (
        .clk(clk_100), .rst(rst), .inicio(inicio), .etiqueta("D"),
        .valor(valor), .ocupado(ocupado), .tx(uart_tx)
    );
endmodule

`default_nettype wire
