// SPDX-License-Identifier: MIT
//
// GENERADO por `sofifi tablas` desde programas/looper.sasm.
// No se edita a mano: model/tests/tablas_test.py compara este fichero con su
// generador. 85 instrucciones, 85 ciclos del modelo,
// 1 palabras de memoria.
`default_nettype none

module programa_looper (
    input  wire [10:0] dir,
    output reg  [53:0] palabra,
    output wire [11:0] instrucciones,
    output wire [15:0] palabras,
    output wire [7:0]  lfo_tipos,
    output wire [59:0] lfo_excursiones,
    output wire        absoluta
);
    assign instrucciones   = 12'd85;
    assign palabras        = 16'd1;
    assign lfo_tipos       = 8'h00;
    assign lfo_excursiones = 60'h000000000000000;
    assign absoluta        = 1'b1;
    always @(*) begin
        // En lógica: en BSRAM (SPX9) daba violaciones de hold (Fase 04).
        (* rom_style = "logic" *)
        case (dir)
            11'd0: palabra = 54'h0b001000000002;
            11'd1: palabra = 54'h09000000000001;
            11'd2: palabra = 54'h050c0000000000;
            11'd3: palabra = 54'h04800200000000;
            11'd4: palabra = 54'h04840200000000;
            11'd5: palabra = 54'h05000000000000;
            11'd6: palabra = 54'h040c0200000000;
            11'd7: palabra = 54'h05100000000000;
            11'd8: palabra = 54'h04940400000000;
            11'd9: palabra = 54'h0900040003d555;
            11'd10: palabra = 54'h0b00800000000a;
            11'd11: palabra = 54'h0900040003d555;
            11'd12: palabra = 54'h0b008000000005;
            11'd13: palabra = 54'h0e000000000000;
            11'd14: palabra = 54'h040c0400000000;
            11'd15: palabra = 54'h040c0400000000;
            11'd16: palabra = 54'h05100000000000;
            11'd17: palabra = 54'h0b002000000003;
            11'd18: palabra = 54'h0e000000000000;
            11'd19: palabra = 54'h040c0400000000;
            11'd20: palabra = 54'h05100000000000;
            11'd21: palabra = 54'h0e000000000000;
            11'd22: palabra = 54'h04980400000000;
            11'd23: palabra = 54'h0900040003c000;
            11'd24: palabra = 54'h0b008000000003;
            11'd25: palabra = 54'h0e000000000000;
            11'd26: palabra = 54'h04100c00000000;
            11'd27: palabra = 54'h05100000000000;
            11'd28: palabra = 54'h0e000000000000;
            11'd29: palabra = 54'h04080400000000;
            11'd30: palabra = 54'h0b002000000017;
            11'd31: palabra = 54'h0e000000000000;
            11'd32: palabra = 54'h10040400000000;
            11'd33: palabra = 54'h05140000000000;
            11'd34: palabra = 54'h04c80400000000;
            11'd35: palabra = 54'h0b002000000005;
            11'd36: palabra = 54'h0e000000000000;
            11'd37: palabra = 54'h049c0400000000;
            11'd38: palabra = 54'h08140000000000;
            11'd39: palabra = 54'h04000400000000;
            11'd40: palabra = 54'h11040000000000;
            11'd41: palabra = 54'h0e000000000000;
            11'd42: palabra = 54'h04040400000000;
            11'd43: palabra = 54'h04100400000000;
            11'd44: palabra = 54'h05040400000000;
            11'd45: palabra = 54'h04080c00000000;
            11'd46: palabra = 54'h0b008000000001;
            11'd47: palabra = 54'h05040000000000;
            11'd48: palabra = 54'h0e000000000000;
            11'd49: palabra = 54'h04040400000000;
            11'd50: palabra = 54'h0b004000000019;
            11'd51: palabra = 54'h04080400000000;
            11'd52: palabra = 54'h05040000000000;
            11'd53: palabra = 54'h0b002000000016;
            11'd54: palabra = 54'h0e000000000000;
            11'd55: palabra = 54'h04c80400000000;
            11'd56: palabra = 54'h0b00200000000a;
            11'd57: palabra = 54'h0e000000000000;
            11'd58: palabra = 54'h04000400000000;
            11'd59: palabra = 54'h11040000000000;
            11'd60: palabra = 54'h04040400000000;
            11'd61: palabra = 54'h040c0400000000;
            11'd62: palabra = 54'h05040400000000;
            11'd63: palabra = 54'h09000400038001;
            11'd64: palabra = 54'h0b004000000005;
            11'd65: palabra = 54'h0e000000000000;
            11'd66: palabra = 54'h0b002000000007;
            11'd67: palabra = 54'h0e000000000000;
            11'd68: palabra = 54'h04040400000000;
            11'd69: palabra = 54'h0b002000000004;
            11'd70: palabra = 54'h0e000000000000;
            11'd71: palabra = 54'h04040400000000;
            11'd72: palabra = 54'h05080000000000;
            11'd73: palabra = 54'h05040000000000;
            11'd74: palabra = 54'h0e000000000000;
            11'd75: palabra = 54'h05140000000000;
            11'd76: palabra = 54'h0e000000000000;
            11'd77: palabra = 54'h04140400000000;
            11'd78: palabra = 54'h08900000000000;
            11'd79: palabra = 54'h04800400000000;
            11'd80: palabra = 54'h05880000000000;
            11'd81: palabra = 54'h04140400000000;
            11'd82: palabra = 54'h08900000000000;
            11'd83: palabra = 54'h04840400000000;
            11'd84: palabra = 54'h058c0000000000;
            default: palabra = 54'h0;
        endcase
    end
endmodule

`default_nettype wire
