// SPDX-License-Identifier: MIT
//
// Memoria de un puerto de escritura y uno de lectura hecha con bloques
// bsram_bloque (1K × 18, salida registrada dentro del bloque). Sustituye a
// bsram_dp donde la salida va a lógica a 100 MHz (fails.md, F-11).
//
//   - PALABRAS ≥ 1 024 y se redondea a múltiplos de 1 024; ANCHO, a múltiplos
//     de 18.
//   - Sin segmentar (GRUPO = 0, o pocos bloques): la lectura tarda 3 ciclos,
//     dirección en t y `dato_r` en t+3 (2 del bloque y 1 del multiplexor entre
//     bloques, que también se registra). Una escritura presentada en t se hace
//     en el flanco final de t.
//   - Segmentada (más de GRUPO bloques; GRUPO, potencia de 2): para memorias
//     que ocupan medio chip (fails.md, F-15). Ningún registro alimenta bloques
//     lejanos y ninguna salida de bloque cruza el chip sin registrarse:
//       1. cada grupo de GRUPO filas registra su copia de la dirección, de la
//          escritura y de la fila leída (registro_copia: Yosys no las fusiona);
//       2. cada bloque registra su propia copia desde la del grupo;
//       3. cada bloque registra su salida en la lógica de al lado;
//       4. cada grupo elige su fila en un multiplexor registrado;
//       5. un último multiplexor registrado elige el grupo.
//     La lectura tarda 7 ciclos. La escritura se hace en el flanco final de
//     t+2, así que el orden entre lecturas y escrituras no cambia.
`default_nettype none

module bsram_pipe #(
    parameter integer PALABRAS = 1024,
    parameter integer ANCHO    = 18,
    parameter integer GRUPO    = 0      // filas por grupo; 0 = sin segmentar
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
    localparam integer SEG = (GRUPO > 0 && NF > GRUPO) ? 1 : 0;

    wire [18*NC-1:0] ancho_w = {{(18*NC-ANCHO){1'b0}}, dato_w};
    wire [AB-1:0]    fila_r  = (NF > 1) ? AB'(dir_r >> 10) : {AB{1'b0}};
    wire [AB-1:0]    fila_w  = (NF > 1) ? AB'(dir_w >> 10) : {AB{1'b0}};

    genvar g, f, c;
    generate
    if (SEG == 0) begin : g_simple
        // La fila leída viaja 2 ciclos junto al dato que sale de los bloques.
        reg [AB-1:0] fila_1, fila_2;
        always @(posedge clk) begin
            fila_1 <= fila_r;
            fila_2 <= fila_1;
        end
        wire [18*NC-1:0] salidas [0:NF-1];
        for (f = 0; f < NF; f = f + 1) begin : g_fila
            for (c = 0; c < NC; c = c + 1) begin : g_columna
                bsram_bloque u_bloque (
                    .clk(clk), .we(we && fila_w == AB'(f)),
                    .dir_w(dir_w[9:0]), .dato_w(ancho_w[18*c +: 18]),
                    .dir_r(dir_r[9:0]), .dato_r(salidas[f][18*c +: 18])
                );
            end
        end
        always @(posedge clk) dato_r <= salidas[fila_2][ANCHO-1:0];
    end else begin : g_segmentada
        localparam integer G   = GRUPO;
        localparam integer NG  = (NF + G - 1) / G;
        localparam integer AL  = (G > 1) ? $clog2(G) : 1;      // bits de fila en el grupo
        localparam integer AGR = (NG > 1) ? $clog2(NG) : 1;    // bits de grupo
        localparam integer AN  = 1 + AB + 10 + 18*NC;           // we, fila, dir_w, dato

        // El grupo leído llega al multiplexor final 6 ciclos después.
        reg [AB-1:0] fila_d [1:6];
        integer i;
        always @(posedge clk) begin
            fila_d[1] <= fila_r;
            for (i = 2; i <= 6; i = i + 1) fila_d[i] <= fila_d[i-1];
        end

        wire [18*NC-1:0] de_grupo [0:NG-1];
        for (g = 0; g < NG; g = g + 1) begin : g_grupo
            // 1. Copia del grupo (t+1).
            wire [AN-1:0] esc_g;
            wire [9:0]    dr_g;
            wire [AB-1:0] fr_g;
            registro_copia #(.ANCHO(AN + 10 + AB)) u_copia (
                .clk(clk), .d({we, fila_w, dir_w[9:0], ancho_w, dir_r[9:0], fila_r}),
                .q({esc_g, dr_g, fr_g})
            );
            // La fila leída del grupo viaja hasta su multiplexor (t+5).
            reg [AB-1:0] fr_2, fr_3, fr_4, fr_5;
            always @(posedge clk) begin
                fr_2 <= fr_g;
                fr_3 <= fr_2;
                fr_4 <= fr_3;
                fr_5 <= fr_4;
            end
            wire [AL-1:0] local_f = AL'(fr_5 % AB'(G));

            wire [18*NC-1:0] salidas [0:G-1];
            for (f = 0; f < G; f = f + 1) begin : g_fila
                if (g * G + f < NF) begin : g_bloques
                    // 2. Copia del bloque (t+2): la escritura ya lleva su fila.
                    wire             we_b;
                    wire [AB-1:0]    fw_b;
                    wire [9:0]       dw_b, dr_b;
                    wire [18*NC-1:0] d_b;
                    registro_copia #(.ANCHO(AN + 10)) u_copia (
                        .clk(clk), .d({esc_g, dr_g}), .q({we_b, fw_b, dw_b, d_b, dr_b})
                    );
                    for (c = 0; c < NC; c = c + 1) begin : g_columna
                        wire [17:0] dato_b;
                        bsram_bloque u_bloque (
                            .clk(clk), .we(we_b && fw_b == AB'(g * G + f)),
                            .dir_w(dw_b), .dato_w(d_b[18*c +: 18]),
                            .dir_r(dr_b), .dato_r(dato_b)
                        );
                        // 3. Salida registrada junto al bloque (t+5).
                        reg [17:0] salida_r;
                        always @(posedge clk) salida_r <= dato_b;
                        assign salidas[f][18*c +: 18] = salida_r;
                    end
                end else begin : g_relleno
                    assign salidas[f] = {(18*NC){1'b0}};
                end
            end
            // 4. Multiplexor del grupo (t+6).
            reg [18*NC-1:0] sel_r;
            always @(posedge clk) sel_r <= salidas[local_f];
            assign de_grupo[g] = sel_r;
        end
        // 5. Multiplexor final (t+7).
        wire [AGR-1:0] grupo = AGR'(fila_d[6] / AB'(G));
        always @(posedge clk) dato_r <= de_grupo[grupo][ANCHO-1:0];
    end
    endgenerate
endmodule

`default_nettype wire
