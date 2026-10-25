// SPDX-License-Identifier: MIT
//
// Modulador sigma-delta de 2.º orden con realimentación distribuida (ADR 0015).
// Equivale a ModuladorSigmaDelta de model/sofifi/domain/salida_1bit.py.
//
//   nuevo1 = integra1 + x    − K1·signo        K1 = 1
//   nuevo2 = integra2 + integra1 − K2·signo    K2 = 4
//   bit    = (nuevo2 >= 0)
//
// `signo` vale ±1 en escala plena, según el bit anterior. Los dos integradores
// usan el estado anterior, como los registros, y saturan a MOD_BITS.
//
// Dos trucos de camino crítico (rtl/AGENTS.md, F-15):
//
//  1. K1·signo = ±2^23 y K2·signo = ±2^25 solo cambian los bits altos. La resta
//     se hace en un campo de 7 o 5 bit, no en los 30.
//  2. Las dos opciones del signo se calculan en paralelo y el bit elige.
//
// Así cada salida sale de un sumador corto y uno de 30 bit, no de tres en
// serie. La saturación mira los tres bits altos (ADR 0014).
//
// La entrada se recorta antes (salida_1bit.v): con la entrada a escala plena el
// segundo integrador satura y el modulador sale de su zona lineal (ADR 0015).
`default_nettype none

module sigma_delta #(
    parameter ALTO_BITS = 27,
    parameter MOD_BITS  = 28,
    parameter DATO_FRAC = 23  // 1,0 en S.23
) (
    input  wire                       clk,
    input  wire                       rst,
    input  wire                       habilita,  // hay un valor válido en `alto`
    input  wire signed [ALTO_BITS-1:0] alto,     // entrada, a 100 MHz
    output reg                        bit_salida
);
    localparam ANCHO = MOD_BITS + 2;  // dos bits de guarda para saturar
    localparam signed [MOD_BITS-1:0] MAXIMO = {1'b0, {(MOD_BITS-1){1'b1}}};
    localparam signed [MOD_BITS-1:0] MINIMO = {1'b1, {(MOD_BITS-1){1'b0}}};

    reg signed [MOD_BITS-1:0] integra1;
    reg signed [MOD_BITS-1:0] integra2;

    wire signed [ANCHO-1:0] integra1_ancho = {{(ANCHO-MOD_BITS){integra1[MOD_BITS-1]}}, integra1};
    wire signed [ANCHO-1:0] integra2_ancho = {{(ANCHO-MOD_BITS){integra2[MOD_BITS-1]}}, integra2};
    wire signed [ANCHO-1:0] alto_ancho = {{(ANCHO-ALTO_BITS){alto[ALTO_BITS-1]}}, alto};

    // x ∓ 2^23 y integra1 ∓ 2^25: solo cambian los bits por encima de la coma.
    localparam CAMPO1 = ANCHO - DATO_FRAC;        // 7 bit
    localparam CAMPO2 = ANCHO - DATO_FRAC - 2;    // 5 bit: K2 = 4 = 2^2
    wire [CAMPO1-1:0] alto_campo = alto_ancho[ANCHO-1:DATO_FRAC];
    wire [CAMPO2-1:0] uno_campo = integra1_ancho[ANCHO-1:DATO_FRAC+2];

    wire signed [ANCHO-1:0] menos_k1 = {alto_campo - {{(CAMPO1-1){1'b0}}, 1'b1},
                                        alto_ancho[DATO_FRAC-1:0]};
    wire signed [ANCHO-1:0] mas_k1 = {alto_campo + {{(CAMPO1-1){1'b0}}, 1'b1},
                                      alto_ancho[DATO_FRAC-1:0]};
    wire signed [ANCHO-1:0] menos_k2 = {uno_campo - {{(CAMPO2-1){1'b0}}, 1'b1},
                                        integra1_ancho[DATO_FRAC+1:0]};
    wire signed [ANCHO-1:0] mas_k2 = {uno_campo + {{(CAMPO2-1){1'b0}}, 1'b1},
                                      integra1_ancho[DATO_FRAC+1:0]};

    wire signed [ANCHO-1:0] suma1 = integra1_ancho + (bit_salida ? menos_k1 : mas_k1);
    wire signed [ANCHO-1:0] suma2 = integra2_ancho + (bit_salida ? menos_k2 : mas_k2);

    function automatic signed [MOD_BITS-1:0] saturar(input signed [ANCHO-1:0] suma);
        if (suma[ANCHO-1] != suma[ANCHO-2] || suma[ANCHO-1] != suma[ANCHO-3])
            saturar = suma[ANCHO-1] ? MINIMO : MAXIMO;
        else
            saturar = suma[MOD_BITS-1:0];
    endfunction

    wire signed [MOD_BITS-1:0] nuevo1 = saturar(suma1);
    wire signed [MOD_BITS-1:0] nuevo2 = saturar(suma2);

    always @(posedge clk) begin
        if (rst) begin
            integra1   <= {MOD_BITS{1'b0}};
            integra2   <= {MOD_BITS{1'b0}};
            bit_salida <= 1'b1;  // tras el reset, el pin vale 1 (igual al modelo)
        end else if (habilita) begin
            integra1   <= nuevo1;
            integra2   <= nuevo2;
            bit_salida <= ~nuevo2[MOD_BITS-1];
        end
    end
endmodule

`default_nettype wire
