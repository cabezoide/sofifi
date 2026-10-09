// SPDX-License-Identifier: MIT
//
// Prueba de la microSD en la placa (Fase 08): arranca la tarjeta del Sipeed
// PMOD TF en el conector J6 del Dock y carga ranuras del banco de `sofifi banco`.
// scripts/prueba_sd.py compara lo cargado con el modelo.
//
// El PMOD TF tiene dos revisiones con CS y SCK en pines distintos (MOSI = G7 y
// MISO = H8 en las dos). El top prueba primero la v2 y, si la tarjeta no
// arranca, la v1. Los pines de la revisión que no se usa quedan en alta
// impedancia: en modo SPI son DAT1 y DAT2 de la tarjeta, que no se usan.
//
//   revisión | CS | SCK
//   v2       | F5 | H5
//   v1       | G5 | G8
//
// Órdenes por la UART (115 200 baudios), y respuestas "<letra> <8 hex>\r\n":
//   'S'               → "M <revisión: 1 o 2, 0 sin tarjeta>", "E <código de sd_spi>"
//   'L' + 2 bytes (k) → carga la ranura k. Si vale: "I <instrucciones>",
//                       "P <palabras>", "X <CRC-32 del microcódigo escrito>".
//                       Si no: "F <motivo del cargador>".
// El CRC-32 (el de zlib) va sobre cada palabra de 54 bit en 7 bytes big-endian.
// Solo envía cuando el PC lo pide (puente del BL616, F-02).
`default_nettype none

module prueba_sd #(
    parameter integer F_RELOJ = 100_000_000,
    parameter integer BAUDIOS = 115_200
) (
    input  wire clk,      // 50 MHz (E2)
    input  wire rst_n,
    input  wire uart_rx,
    output wire uart_tx,
    // PMOD TF en J6
    inout  wire sd_f5,    // v2: CS
    inout  wire sd_h5,    // v2: SCK
    inout  wire sd_g5,    // v1: CS
    inout  wire sd_g8,    // v1: SCK
    output wire sd_mosi,  // G7
    input  wire sd_miso   // H8
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

    // Solo la revisión elegida maneja sus pines; la otra queda en alta impedancia.
    wire v1, cs_n, sck;
    assign sd_f5 = !v1 ? cs_n : 1'bz;
    assign sd_h5 = !v1 ? sck  : 1'bz;
    assign sd_g5 =  v1 ? cs_n : 1'bz;
    assign sd_g8 =  v1 ? sck  : 1'bz;
    prueba_sd_logica #(.F_RELOJ(F_RELOJ), .BAUDIOS(BAUDIOS)) u_logica (
        .clk(clk_100), .rst(rst), .uart_rx(uart_rx), .uart_tx(uart_tx),
        .v1(v1), .sd_cs_n(cs_n), .sd_sck(sck), .sd_mosi(sd_mosi), .sd_miso(sd_miso)
    );
endmodule

`default_nettype wire
