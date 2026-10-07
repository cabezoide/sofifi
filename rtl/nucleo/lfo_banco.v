// SPDX-License-Identifier: MIT
//
// Los 4 LFO del núcleo (ADR 0008). Equivale a model/sofifi/domain/lfo.py:
//
//   - fase de 24 bit; cada muestra avanza `rate` (dato S.23 como entero);
//   - RND: en cada vuelta de fase, 24 pasos del LFSR Galois (0xD0000001) fijan un
//     objetivo nuevo; la salida lo persigue cada muestra con >> 6;
//   - triángulo, ventana y fase con media vuelta, combinacionales para el LFO
//     elegido con `sel`. Los productos (curva suave, depth, excursión) los hace
//     el multiplicador del núcleo durante el CHO.
//
// `avanzar` empieza la actualización; `listo` da un pulso 26 ciclos después.
// Los 24 pasos del LFSR van de uno en uno para no alargar el camino crítico.
`default_nettype none

module lfo_banco (
    input  wire               clk,
    input  wire               rst,
    input  wire [7:0]         tipos,      // 2 bit por LFO: 0 SIN, 1 RND, 2 RAMP
    input  wire               avanzar,
    input  wire [95:0]        rates,      // 24 bit por LFO, con signo
    output reg                listo,
    input  wire [1:0]         sel,
    input  wire               media,
    output wire [23:0]        fase_sel,   // con media vuelta si `media`
    output wire signed [23:0] tri_sel,    // triangulo(fase), sin media vuelta
    output wire signed [23:0] ven_sel,    // ventana(fase con media vuelta si `media`)
    output wire signed [23:0] actual_sel  // salida RND
);
    localparam [1:0] RND = 2'd1;
    localparam [31:0] MASCARA = 32'hD0000001;
    localparam [31:0] SEMILLA = 32'hACE1ACE1;

    reg [23:0]        fase    [0:3];
    reg [31:0]        lfsr    [0:3];
    reg signed [23:0] objetivo[0:3];
    reg signed [23:0] actual  [0:3];
    reg [3:0]         vuelta;
    reg [4:0]         paso;      // 0 = parado; 1..24 = pasos del LFSR; 25 = cierre
    integer n;

    function automatic [31:0] lfsr_paso(input [31:0] e);
        lfsr_paso = e[0] ? ((e >> 1) ^ MASCARA) : (e >> 1);
    endfunction

    always @(posedge clk) begin
        listo <= 1'b0;
        if (rst) begin
            paso <= 5'd0;
            vuelta <= 4'd0;
            for (n = 0; n < 4; n = n + 1) begin
                fase[n] <= 24'd0; lfsr[n] <= SEMILLA;
                objetivo[n] <= 24'sd0; actual[n] <= 24'sd0;
            end
        end else if (avanzar) begin
            for (n = 0; n < 4; n = n + 1) begin : avance
                reg signed [25:0] nueva;
                nueva = $signed({2'b00, fase[n]}) + {{2{rates[24*n+23]}}, rates[24*n +: 24]};
                fase[n]   <= nueva[23:0];
                vuelta[n] <= (nueva < 26'sd0 || nueva >= 26'sd16777216) && tipos[2*n +: 2] == RND;
            end
            paso <= 5'd1;
        end else if (paso >= 5'd1 && paso <= 5'd24) begin
            for (n = 0; n < 4; n = n + 1)
                if (vuelta[n]) lfsr[n] <= lfsr_paso(lfsr[n]);
            paso <= paso + 1'b1;
        end else if (paso == 5'd25) begin
            for (n = 0; n < 4; n = n + 1) begin : cierre
                reg signed [23:0] obj;
                reg signed [24:0] dif;   // objetivo − actual necesita 25 bit
                obj = vuelta[n] ? $signed({~lfsr[n][23], lfsr[n][22:0]}) : objetivo[n];
                dif = {obj[23], obj} - {actual[n][23], actual[n]};
                objetivo[n] <= obj;
                if (tipos[2*n +: 2] == RND)
                    actual[n] <= actual[n] + 24'(dif >>> 6);
            end
            paso  <= 5'd0;
            listo <= 1'b1;
        end
    end

    // ── Formas del LFO elegido ──────────────────────────────────────────
    wire [23:0] f  = fase[sel];
    wire [23:0] fm = media ? f + 24'h800000 : f;   // módulo 2^24
    assign fase_sel   = fm;
    assign actual_sel = actual[sel];

    // triangulo(fase): 0 en 0, +1 (saturado) en un cuarto, -1 en tres cuartos.
    reg signed [25:0] t;
    always @(*) begin
        if (f < 24'h400000)      t = $signed({2'b00, f}) <<< 1;
        else if (f < 24'hC00000) t = (26'sd8388608 - $signed({2'b00, f})) <<< 1;
        else                     t = ($signed({2'b00, f}) - 26'sd16777216) <<< 1;
    end
    assign tri_sel = (t > 26'sd8388607) ? 24'sh7FFFFF : t[23:0];

    // ventana(fase) = min(1, 1 − |2·fase − 2^24| / 2) = 2^23 − |fase − 2^23|,
    // saturada: 0 en fase 0, 1 (saturado) a media fase.
    wire signed [24:0] desde_medio = $signed({1'b0, fm}) - 25'sd8388608;
    wire signed [24:0] distancia   = desde_medio[24] ? -desde_medio : desde_medio;
    wire signed [25:0] v           = 26'sd8388608 - {distancia[24], distancia};
    assign ven_sel = (v > 26'sd8388607) ? 24'sh7FFFFF : v[23:0];
endmodule

`default_nettype wire
