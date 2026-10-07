// SPDX-License-Identifier: MIT
//
// Memoria de un puerto de escritura y uno de lectura hecha con bloques
// bsram_bloque (1K × 18, salida registrada dentro del bloque). Sustituye a
// bsram_dp donde la salida va a lógica a 100 MHz (fails.md, F-11).
//
//   - PALABRAS ≥ 1 024 y se redondea a múltiplos de 1 024; ANCHO, a múltiplos
//     de 18.
//   - La lectura tarda 3 ciclos: dirección en t, `dato_r` en t+3 (2 del bloque
//     y 1 del multiplexor entre bloques, que también se registra).
//   - Una escritura presentada en t se hace en el flanco final de t.
`default_nettype none

module bsram_pipe #(
    parameter integer PALABRAS = 1024,
    parameter integer ANCHO    = 18
) (
    input  wire                        clk,
    input  wire                        we,
    input  wire [$clog2(PALABRAS)-1:0] dir_w,
    input  wire [ANCHO-1:0]            dato_w,
    input  wire [$clog2(PALABRAS)-1:0] dir_r,
    output reg  [ANCHO-1:0]            dato_r
);
    localparam integer NF  = (PALABRAS + 1023) / 1024;   // bloques en profundidad
    localparam integer NC  = (ANCHO + 17) / 18;          // bloques en anchura
    localparam integer AB  = (NF > 1) ? $clog2(NF) : 1;  // bits de bloque

    wire [AB-1:0] fila_w = (NF > 1) ? AB'(dir_w >> 10) : {AB{1'b0}};
    wire [AB-1:0] fila_r = (NF > 1) ? AB'(dir_r >> 10) : {AB{1'b0}};
    wire [18*NC-1:0] ancho_w = {{(18*NC-ANCHO){1'b0}}, dato_w};

    // La fila leída viaja 2 ciclos junto al dato que sale de los bloques.
    reg [AB-1:0] fila_1, fila_2;
    always @(posedge clk) begin
        fila_1 <= fila_r;
        fila_2 <= fila_1;
    end

    wire [18*NC-1:0] salidas [0:NF-1];
    genvar f, c;
    generate
        for (f = 0; f < NF; f = f + 1) begin : g_fila
            for (c = 0; c < NC; c = c + 1) begin : g_columna
                bsram_bloque u_bloque (
                    .clk(clk), .we(we && fila_w == AB'(f)),
                    .dir_w(dir_w[9:0]), .dato_w(ancho_w[18*c +: 18]),
                    .dir_r(dir_r[9:0]), .dato_r(salidas[f][18*c +: 18])
                );
            end
        end
    endgenerate

    always @(posedge clk) dato_r <= salidas[fila_2][ANCHO-1:0];
endmodule

`default_nettype wire
