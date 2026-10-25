// SPDX-License-Identifier: MIT
//
// Salida de audio de 1 bit (ADR 0015). Equivale a Salida1Bit de
// model/sofifi/domain/salida_1bit.py.
//
//   muestra S.23 ─► recorte ─► cic_interp ─► sigma_delta ─► un pin
//     cada 2 048 ciclos        32·fs         100 MHz        1 bit
//
// El recorte a ±13/16 de escala plena es un requisito de seguridad: un programa
// de la microSD puede saturar a ±1, y con la entrada a escala plena el
// modulador sale de su zona lineal (ADR 0015, SECURITY.md).
//
// El flujo del RTL va 6 ciclos de 100 MHz por detrás del flujo del modelo. Ese
// retardo sale de la segmentación, que deja una sola suma por ciclo:
//
//   ciclo 0: recorte            ciclo 3: d2
//   ciclo 1: tick del CIC       ciclo 4: integra1
//   ciclo 2: d1                 ciclo 5: integra2 y primer paso del modulador
//   ciclo 6: el pin lleva el bit 0 del modelo
//
// El modulador no arranca hasta que `alto` vale: si no, su estado al llegar la
// primera muestra no sería el del modelo tras el reset. El testbench compara el
// flujo desplazado esos 6 ciclos (sim/salida/salida_1bit_test.py, LATENCIA).
`default_nettype none

module salida_1bit #(
    parameter DATO_BITS = 24,
    parameter DATO_FRAC = 23,
    parameter ALTO_BITS = 27
) (
    input  wire                        clk,
    input  wire                        rst,
    input  wire                        tick,     // muestra nueva, cada 2 048 ciclos
    input  wire signed [DATO_BITS-1:0] muestra,  // S.23
    output wire                        bit_salida
);
    // 13/16 de escala plena, el límite estable del modulador (ADR 0015).
    localparam signed [DATO_BITS-1:0] LIMITE = (13 << DATO_FRAC) / 16;

    reg signed [DATO_BITS-1:0] recortada;
    reg                        tick_cic;

    wire alta = muestra > LIMITE;
    wire baja = muestra < -LIMITE;

    always @(posedge clk) begin
        if (rst) begin
            recortada <= {DATO_BITS{1'b0}};
            tick_cic  <= 1'b0;
        end else begin
            tick_cic <= tick;
            if (tick) recortada <= alta ? LIMITE : (baja ? -LIMITE : muestra);
        end
    end

    wire signed [ALTO_BITS-1:0] alto;
    wire                        valido;

    cic_interp interpolador (
        .clk     (clk),
        .rst     (rst),
        .tick    (tick_cic),
        .muestra (recortada),
        .valido  (valido),
        .alto    (alto)
    );

    sigma_delta #(
        .ALTO_BITS (ALTO_BITS),
        .DATO_FRAC (DATO_FRAC)
    ) modulador (
        .clk        (clk),
        .rst        (rst),
        .habilita   (valido),
        .alto       (alto),
        .bit_salida (bit_salida)
    );
endmodule

`default_nettype wire
