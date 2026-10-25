// SPDX-License-Identifier: MIT
//
// Lectura de la pista de audio de la microSD (Fase 13): sd_spi.v +
// lector_pista.v. Los pines van a la tarjeta y la muestra, al núcleo. Ver los
// dos módulos para el protocolo y las comprobaciones.
`default_nettype none

module lee_pista #(
    parameter integer DIV_LENTO       = 125,
    parameter integer DIV_RAPIDO      = 4,
    parameter integer INTENTOS_ACMD41 = 4000,
    parameter integer ESPERA_TOKEN    = 65535,
    parameter integer MUESTRAS_COLA   = 1024
) (
    input  wire               clk,
    input  wire               rst,
    input  wire               tick,
    output wire signed [23:0] muestra,
    output wire               vacio,
    output wire               listo,
    output wire               preparado,
    output wire               error,
    output wire [2:0]         motivo,
    output wire               sd_listo,
    output wire               sd_error,
    output wire [3:0]         sd_codigo,
    // Tarjeta
    output wire               sd_cs_n,
    output wire               sd_sck,
    output wire               sd_mosi,
    input  wire               sd_miso
);
    wire        leer, sd_ocupado, dato_v, fin;
    wire [31:0] bloque;
    wire [7:0]  dato;

    sd_spi #(
        .DIV_LENTO(DIV_LENTO), .DIV_RAPIDO(DIV_RAPIDO),
        .INTENTOS_ACMD41(INTENTOS_ACMD41), .ESPERA_TOKEN(ESPERA_TOKEN)
    ) u_sd (
        .clk(clk), .rst(rst), .leer(leer), .bloque(bloque), .listo(sd_listo),
        .ocupado(sd_ocupado), .error(sd_error), .codigo(sd_codigo), .dato(dato),
        .dato_v(dato_v), .fin(fin), .sd_cs_n(sd_cs_n), .sd_sck(sd_sck),
        .sd_mosi(sd_mosi), .sd_miso(sd_miso)
    );

    lector_pista #(
        .MUESTRAS_COLA(MUESTRAS_COLA)
    ) u_lector (
        .clk(clk), .rst(rst), .tick(tick), .muestra(muestra), .vacio(vacio),
        .listo(listo), .preparado(preparado), .error(error), .motivo(motivo), .sd_leer(leer),
        .sd_bloque(bloque), .sd_listo(sd_listo), .sd_ocupado(sd_ocupado),
        .sd_error(sd_error), .sd_dato(dato), .sd_dato_v(dato_v), .sd_fin(fin)
    );
endmodule

`default_nettype wire
