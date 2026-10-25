// SPDX-License-Identifier: MIT
//
// El pedal suena en la placa sin el códec (Fase 13, ADR 0015):
//
//   microSD ─► lee_pista ─► núcleo ─► salida_1bit ─► un pin ─► filtro RC ─► amplificador
//
// La fuente es una pista de audio de la tarjeta (`sofifi pista`), porque el
// pedal no tiene entrada analógica hasta la Fase 11. La salida es un flujo de
// 1 bit a 100 MHz; el filtro RC de dos polos está en docs/audio_1bit.md.
//
// El núcleo no arranca hasta que la pista tiene su primera muestra
// (`preparado`). Así, la muestra 0 del núcleo es la muestra 0 de la pista y el
// RTL se puede comparar con el modelo (ADR 0003, sim/top/audio_sd_test.py).
//
// Cada 4 096 muestras (unas 12 veces por segundo) envía
// "E <estado><dac_l>\r\n" por la UART. A ese caudal el puente del BL616 no se
// cuelga (Fase 03). El estado lleva, de bit alto a bajo:
//
//   [23:13] cero · [12] sd_listo · [11] listo · [10] preparado · [9] vacio
//   [8] error · [7:5] motivo del error de la pista · [4] sd_error
//   [3:0] código de error de sd_spi
//
// PROGRAMA elige la ROM: "plate" (por defecto) o "hil" (top audio_programa, con
// la ROM que escribe `sofifi rom`; `make audio AUDIO=NOMBRE`).
//
// Pines de la tarjeta: la revisión v2 del PMOD TF en J6 (ADR 0004). Con un
// módulo v1 la tarjeta no arranca, y el estado lo dice: `sd_error` con el
// código 1 (CMD0).
`default_nettype none

module audio_sd #(
    parameter integer F_RELOJ      = 100_000_000,
    parameter integer BAUDIOS      = 115_200,
    parameter integer PALABRAS_MAX = 43_008,  // 42 bloques: la memoria completa
    parameter integer DIV_LENTO    = 125,
    parameter integer DIV_RAPIDO   = 4,
    parameter [47:0]  PROGRAMA     = "plate"
) (
    input  wire clk,      // 50 MHz (E2)
    input  wire rst_n,
    output wire uart_tx,
    // microSD (PMOD TF v2 en J6)
    output wire sd_cs_n,
    output wire sd_sck,
    output wire sd_mosi,
    input  wire sd_miso,
    // Audio de 1 bit
    output wire audio
);
    localparam integer DIVISOR = F_RELOJ / BAUDIOS;

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

    // ── Programa ──────────────────────────────────────────────────────────
    wire [53:0] palabra;
    wire [11:0] instrucciones;
    wire [15:0] palabras;
    wire [7:0]  lfo_tipos;
    wire [59:0] lfo_excursiones;
    wire        absoluta;
    wire [10:0] dir, prog_dir;
    wire [53:0] prog_dato;
    wire        prog_we, cargado;
    generate if (PROGRAMA == "hil") begin : g_hil
        programa_hil u_prog (
            .dir(dir), .palabra(palabra), .instrucciones(instrucciones),
            .palabras(palabras), .lfo_tipos(lfo_tipos), .lfo_excursiones(lfo_excursiones),
            .absoluta(absoluta)
        );
    end else begin : g_plate
        programa_plate u_prog (
            .dir(dir), .palabra(palabra), .instrucciones(instrucciones),
            .palabras(palabras), .lfo_tipos(lfo_tipos), .lfo_excursiones(lfo_excursiones),
            .absoluta(absoluta)
        );
    end endgenerate
    carga_programa u_carga (
        .clk(clk_100), .rst(rst), .instrucciones(instrucciones),
        .dir(dir), .palabra(palabra), .prog_we(prog_we), .prog_dir(prog_dir),
        .prog_dato(prog_dato), .cargado(cargado)
    );

    // ── Pista de la microSD ───────────────────────────────────────────────
    wire               tick;
    wire signed [23:0] entrada;
    wire               pista_vacio, pista_listo, pista_preparada, pista_error;
    wire [2:0]         pista_motivo;
    wire               sd_listo, sd_error;
    wire [3:0]         sd_codigo;

    lee_pista #(
        .DIV_LENTO(DIV_LENTO), .DIV_RAPIDO(DIV_RAPIDO)
    ) u_pista (
        .clk(clk_100), .rst(rst), .tick(tick), .muestra(entrada),
        .vacio(pista_vacio), .listo(pista_listo), .preparado(pista_preparada),
        .error(pista_error), .motivo(pista_motivo), .sd_listo(sd_listo),
        .sd_error(sd_error), .sd_codigo(sd_codigo), .sd_cs_n(sd_cs_n),
        .sd_sck(sd_sck), .sd_mosi(sd_mosi), .sd_miso(sd_miso)
    );

    // ── Una muestra cada 2 048 ciclos, cuando hay audio ───────────────────
    generador_muestra u_gen (
        .clk(clk_100), .activo(cargado && pista_preparada), .tick(tick)
    );

    // ── Núcleo ────────────────────────────────────────────────────────────
    wire signed [23:0] dac_l;
    wire               fin;
    /* verilator lint_off UNUSEDSIGNAL */
    wire signed [23:0] dac_r;   // la salida de 1 bit es mono (ADR 0015)
    wire               ocupado;
    wire [15:0]        ciclos;
    wire [11:0]        traza_pc;
    wire signed [47:0] traza_acc;
    /* verilator lint_on UNUSEDSIGNAL */
    nucleo #(.PALABRAS_MAX(PALABRAS_MAX)) u_nucleo (
        .clk(clk_100), .rst(rst | ~cargado),
        .prog_we(prog_we), .prog_dir(prog_dir), .prog_dato(prog_dato),
        .cfg_instrucciones(instrucciones), .cfg_palabras(palabras),
        .cfg_lfo_tipos(lfo_tipos), .cfg_lfo_excursiones(lfo_excursiones),
        .cfg_absoluta(absoluta),
        .tick(tick), .adc_l(entrada), .adc_r(entrada),
        .pots({6{24'sh400000}}), .sw(24'sd0),
        .dac_l(dac_l), .dac_r(dac_r), .fin(fin), .ocupado(ocupado), .ciclos(ciclos),
        .traza_pc(traza_pc), .traza_acc(traza_acc)
    );

    // ── Salida de 1 bit ───────────────────────────────────────────────────
    salida_1bit u_salida (
        .clk(clk_100), .rst(rst), .tick(tick), .muestra(dac_l), .bit_salida(audio)
    );

    // ── Informe por la UART cada 4 096 muestras ──────────────────────────
    wire [23:0] estado = {11'd0, sd_listo, pista_listo, pista_preparada, pista_vacio,
                          pista_error, pista_motivo, sd_error, sd_codigo};
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
    linea_hex #(.DIGITOS(12), .DIVISOR(DIVISOR)) u_linea (
        .clk(clk_100), .rst(rst), .inicio(inicio), .etiqueta("E"),
        .valor({estado, dac_l}), .ocupado(ocupado_uart), .tx(uart_tx)
    );
endmodule

`default_nettype wire
