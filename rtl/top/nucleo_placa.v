// SPDX-License-Identifier: MIT
//
// El núcleo en la placa (Fase 04): PLL de 100 MHz, una muestra cada 2 048 ciclos
// (48 828,125 Hz, ADR 0005) y el plate cargado desde ROM por el puerto de
// programa, como hará la microSD (Fase 08).
//
// La entrada es ruido de un LFSR a -24 dB. Cada 4 096 muestras (unas 12 veces por
// segundo) envía "N <dac_l><dac_r>\r\n" por la UART; a ese caudal el puente del
// BL616 no se cuelga (Fase 03). Es una prueba de humo: la comparación bit a bit
// con el modelo es la de la Fase 05.
`default_nettype none

module nucleo_placa #(
    parameter integer F_RELOJ = 100_000_000,
    parameter integer BAUDIOS = 115_200
) (
    input  wire clk,      // 50 MHz (E2)
    input  wire rst_n,
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

    // ── Carga del programa ────────────────────────────────────────────────
    wire [53:0] palabra;
    wire [11:0] instrucciones;
    wire [15:0] palabras;
    wire [7:0]  lfo_tipos;
    wire [59:0] lfo_excursiones;
    wire [10:0] dir, prog_dir;
    wire [53:0] prog_dato;
    wire        prog_we, cargado;
    programa_plate u_prog (
        .dir(dir), .palabra(palabra), .instrucciones(instrucciones),
        .palabras(palabras), .lfo_tipos(lfo_tipos), .lfo_excursiones(lfo_excursiones)
    );
    carga_programa u_carga (
        .clk(clk_100), .rst(rst), .instrucciones(instrucciones),
        .dir(dir), .palabra(palabra), .prog_we(prog_we), .prog_dir(prog_dir),
        .prog_dato(prog_dato), .cargado(cargado)
    );

    // ── Una muestra cada 2 048 ciclos ─────────────────────────────────────
    wire tick;
    generador_muestra u_gen (.clk(clk_100), .activo(cargado), .tick(tick));

    // Ruido de un LFSR de 32 bit (el del modelo), a -24 dB.
    reg [31:0] ruido;
    always @(posedge clk_100)
        if (rst) ruido <= 32'hACE1ACE1;
        else if (tick) ruido <= ruido[0] ? ((ruido >> 1) ^ 32'hD0000001) : (ruido >> 1);
    wire signed [23:0] entrada = {{4{ruido[23]}}, ruido[23:4]};

    // ── Núcleo ────────────────────────────────────────────────────────────
    wire signed [23:0] dac_l, dac_r;
    wire               fin;
    /* verilator lint_off UNUSEDSIGNAL */
    wire               ocupado;
    wire [15:0]        ciclos;
    /* verilator lint_on UNUSEDSIGNAL */
    nucleo u_nucleo (
        .clk(clk_100), .rst(rst | ~cargado),
        .prog_we(prog_we), .prog_dir(prog_dir), .prog_dato(prog_dato),
        .cfg_instrucciones(instrucciones), .cfg_palabras(palabras),
        .cfg_lfo_tipos(lfo_tipos), .cfg_lfo_excursiones(lfo_excursiones),
        .tick(tick), .adc_l(entrada), .adc_r(-entrada),
        .pots({6{24'sh400000}}), .sw(24'sd0),
        .dac_l(dac_l), .dac_r(dac_r), .fin(fin), .ocupado(ocupado), .ciclos(ciclos)
    );

    // ── Informe por la UART cada 4 096 muestras ──────────────────────────
    reg [11:0] muestras;
    reg        inicio;
    wire       ocupado_uart;
    always @(posedge clk_100) begin
        inicio <= 1'b0;
        if (rst) muestras <= 12'd0;
        else if (fin) begin
            muestras <= muestras + 1'b1;
            if (muestras == 12'd0 && !ocupado_uart) inicio <= 1'b1;
        end
    end
    linea_hex #(.DIGITOS(12), .DIVISOR(F_RELOJ / BAUDIOS)) u_linea (
        .clk(clk_100), .rst(rst), .inicio(inicio), .etiqueta("N"),
        .valor({dac_l, dac_r}), .ocupado(ocupado_uart), .tx(uart_tx)
    );
endmodule

`default_nettype wire
