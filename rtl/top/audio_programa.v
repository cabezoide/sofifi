// SPDX-License-Identifier: MIT
//
// audio_sd con la ROM que escribe `sofifi rom` en build/programa_hil.v:
// cualquier programa o cadena suena en la placa. `make audio AUDIO=NOMBRE`
// genera la ROM, sintetiza y carga.
//
// No está en tops.txt: su ROM no está en el repositorio.
`default_nettype none

module audio_programa (
    input  wire clk,
    input  wire rst_n,
    output wire uart_tx,
    output wire sd_cs_n,
    output wire sd_sck,
    output wire sd_mosi,
    input  wire sd_miso,
    output wire audio
);
    audio_sd #(.PROGRAMA("hil")) u_audio (
        .clk(clk), .rst_n(rst_n), .uart_tx(uart_tx), .sd_cs_n(sd_cs_n),
        .sd_sck(sd_sck), .sd_mosi(sd_mosi), .sd_miso(sd_miso), .audio(audio)
    );
endmodule

`default_nettype wire
