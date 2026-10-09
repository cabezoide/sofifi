// SPDX-License-Identifier: MIT
//
// Carga de programas desde la microSD (Fase 08): sd_spi.v + cargador.v. Los
// pines van a la tarjeta y el resto, al puerto de programa del núcleo. Ver los
// dos módulos para el protocolo y las comprobaciones.
`default_nettype none

module carga_sd #(
    parameter integer DIV_LENTO       = 125,
    parameter integer DIV_RAPIDO      = 4,
    parameter integer INTENTOS_ACMD41 = 4000,
    parameter integer ESPERA_TOKEN    = 65535
) (
    input  wire        clk,
    input  wire        rst,
    input  wire        cargar,
    input  wire [9:0]  ranura,
    output wire        sd_listo,
    output wire        sd_error,
    output wire [3:0]  sd_codigo,
    output wire        ocupado,
    output wire        hecho,
    output wire        fallo,
    output wire [3:0]  motivo,
    // Tarjeta
    output wire        sd_cs_n,
    output wire        sd_sck,
    output wire        sd_mosi,
    input  wire        sd_miso,
    // Núcleo
    output wire        nucleo_rst,
    output wire        prog_we,
    output wire [10:0] prog_dir,
    output wire [53:0] prog_dato,
    output wire [11:0] cfg_instrucciones,
    output wire [15:0] cfg_palabras,
    output wire [7:0]  cfg_lfo_tipos,
    output wire [59:0] cfg_lfo_excursiones,
    output wire        cfg_absoluta
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
    cargador u_cargador (
        .clk(clk), .rst(rst), .cargar(cargar), .ranura(ranura), .ocupado(ocupado),
        .hecho(hecho), .fallo(fallo), .motivo(motivo), .sd_leer(leer), .sd_bloque(bloque),
        .sd_ocupado(sd_ocupado), .sd_error(sd_error), .sd_dato(dato), .sd_dato_v(dato_v),
        .sd_fin(fin), .nucleo_rst(nucleo_rst), .prog_we(prog_we), .prog_dir(prog_dir),
        .prog_dato(prog_dato), .cfg_instrucciones(cfg_instrucciones),
        .cfg_palabras(cfg_palabras), .cfg_lfo_tipos(cfg_lfo_tipos),
        .cfg_lfo_excursiones(cfg_lfo_excursiones), .cfg_absoluta(cfg_absoluta)
    );
endmodule

`default_nettype wire
