// SPDX-License-Identifier: MIT
//
// Interpolador CIC de Hogenauer, S = 2 y R = 32 (ADR 0015). Equivale a
// InterpoladorCIC de model/sofifi/domain/salida_1bit.py.
//
// Dos peines a fs y dos integradores a 32·fs, sin multiplicadores. La ganancia
// es R^(S-1) = 32, porque el relleno de ceros divide por R; por eso la salida
// sale desplazada 5 bit.
//
// Reparto por ciclos, contando desde el `tick` de la muestra (2 048 ciclos):
//
//   ciclo 0        : d1 <= muestra - peine1
//   ciclo 1        : d2 <= d1 - peine2
//   ciclo 2        : integra1 <= integra1 + d2   (los demás pasos suman 0)
//   ciclo 3 + 64·k : integra2 <= integra2 + integra1,  k = 0 .. 31
//
// Cada ciclo hace una sola suma: el camino crítico es un sumador de 32 bit
// (rtl/AGENTS.md, F-10). El último paso cae en el ciclo 1 987 de 2 048.
//
// Los integradores son modulares, como en el modelo. Los valores reales caben
// en 30 bit, así que nunca envuelven.
//
// `alto` vale durante 64 ciclos y lleva un retardo fijo frente al modelo. El
// retardo es uniforme: el testbench compara el flujo desplazado (LATENCIA de
// salida_1bit.v).
//
// Origen del algoritmo: U. Meyer-Baese, «Digital Signal Processing with Field
// Programmable Gate Arrays», 3.ª ed., §5.3. Estudiado, no portado (ADR 0002).
`default_nettype none

module cic_interp #(
    parameter GANANCIA = 5,  // log2(R^(S-1))
    parameter CIC_BITS = 32
) (
    input  wire                                clk,
    input  wire                                rst,
    input  wire                                tick,     // muestra nueva
    input  wire signed [23:0]                  muestra,  // S.23, ya recortada
    output reg                                 valido,   // `alto` ya tiene un valor
    output wire signed [CIC_BITS-GANANCIA-1:0] alto      // a 32·fs
);
    localparam CUENTA_BITS = 11;  // 2 048 ciclos por muestra

    reg signed [23:0] peine1;  // x[n-1]
    reg signed [24:0] peine2;  // d1[n-1]
    reg signed [24:0] d1;
    reg signed [25:0] d2;

    reg [CIC_BITS-1:0] integra1;
    reg [CIC_BITS-1:0] integra2;

    reg [CUENTA_BITS-1:0] fase;    // ciclos desde el tick; 1 en el ciclo 1
    reg                   activo;  // hubo un tick desde el reset

    // Solo importan los 6 bits bajos: un paso cada 64 ciclos.
    wire [5:0] desde = fase[5:0] - 6'd3;
    wire paso    = activo && desde == 6'd0;  // ciclo 3 + 64·k
    wire inicial = activo && fase == {{(CUENTA_BITS-2){1'b0}}, 2'd2};

    wire [CIC_BITS-1:0] d2_ancho = {{(CIC_BITS-26){d2[25]}}, d2};

    always @(posedge clk) begin
        if (rst) begin
            peine1   <= 24'sd0;
            peine2   <= 25'sd0;
            d1       <= 25'sd0;
            d2       <= 26'sd0;
            integra1 <= {CIC_BITS{1'b0}};
            integra2 <= {CIC_BITS{1'b0}};
            fase     <= {CUENTA_BITS{1'b0}};
            activo   <= 1'b0;
            valido   <= 1'b0;
        end else begin
            if (tick) begin
                d1     <= {muestra[23], muestra} - {peine1[23], peine1};
                peine1 <= muestra;
                fase   <= {{(CUENTA_BITS-1){1'b0}}, 1'b1};
                activo <= 1'b1;
            end else begin
                fase <= fase + {{(CUENTA_BITS-1){1'b0}}, 1'b1};
            end

            if (activo && fase == {{(CUENTA_BITS-1){1'b0}}, 1'b1}) begin
                d2     <= {d1[24], d1} - {peine2[24], peine2};
                peine2 <= d1;
            end

            if (inicial) integra1 <= integra1 + d2_ancho;
            if (paso) begin
                integra2 <= integra2 + integra1;
                valido   <= 1'b1;
            end
        end
    end

    assign alto = integra2[CIC_BITS-1:GANANCIA];
endmodule

`default_nettype wire
