// SPDX-License-Identifier: MIT
//
// Copia un programa desde una ROM (rtl/top/programa_*.v, generada por
// `sofifi tablas`) al microcódigo del núcleo por su puerto de programa. Empieza
// al salir del reset y tarda `instrucciones` + 1 ciclos; después `cargado` vale 1.
// Mientras tanto el núcleo debe estar en reset.
//
// La palabra de la ROM se registra (`prog_dato`) y se escribe un ciclo después,
// en `prog_dir`: la ROM en LUT y la entrada de la BSRAM en el mismo ciclo eran el
// camino crítico (fails.md, F-11).
`default_nettype none

module carga_programa (
    input  wire        clk,
    input  wire        rst,
    input  wire [11:0] instrucciones,
    output reg  [10:0] dir,          // dirección de la ROM
    input  wire [53:0] palabra,      // palabra de la ROM en `dir`
    output reg         prog_we,
    output reg  [10:0] prog_dir,
    output reg  [53:0] prog_dato,
    output reg         cargado
);
    reg leyendo;
    always @(posedge clk) begin
        prog_we <= 1'b0;
        if (rst) begin
            dir <= 11'd0; leyendo <= 1'b1; cargado <= 1'b0;
        end else if (leyendo) begin
            prog_we   <= 1'b1;
            prog_dir  <= dir;
            prog_dato <= palabra;
            if ({1'b0, dir} == instrucciones - 1'b1) leyendo <= 1'b0;
            else dir <= dir + 1'b1;
        end else begin
            cargado <= 1'b1;   // la última escritura ocurre en este ciclo
        end
    end
endmodule

`default_nettype wire
