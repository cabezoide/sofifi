// SPDX-License-Identifier: MIT
//
// GENERADO por `sofifi tablas` desde programas/plate.sasm.
// No se edita a mano: model/tests/tablas_test.py compara este fichero con su
// generador. 86 instrucciones, 92 ciclos del modelo,
// 37439 palabras de memoria.
`default_nettype none

module programa_plate (
    input  wire [10:0] dir,
    output reg  [53:0] palabra,
    output wire [11:0] instrucciones,
    output wire [15:0] palabras,
    output wire [7:0]  lfo_tipos,
    output wire [59:0] lfo_excursiones,
    output wire        absoluta
);
    assign instrucciones   = 12'd86;
    assign palabras        = 16'd37439;
    assign lfo_tipos       = 8'h00;
    assign lfo_excursiones = 60'h00000000006800d;
    assign absoluta        = 1'b0;
    always @(*) begin
        // En lógica: en BSRAM (SPX9) daba violaciones de hold (Fase 04).
        (* rom_style = "logic" *)
        case (dir)
            11'd0: palabra = 54'h0b001000000009;
            11'd1: palabra = 54'h09000000000040;
            11'd2: palabra = 54'h051c0000000000;
            11'd3: palabra = 54'h041c0015780000;
            11'd4: palabra = 54'h05a80000000000;
            11'd5: palabra = 54'h041c0010880000;
            11'd6: palabra = 54'h05b00000000000;
            11'd7: palabra = 54'h09000000007eb8;
            11'd8: palabra = 54'h05ac0400000000;
            11'd9: palabra = 54'h05b40000000000;
            11'd10: palabra = 54'h049002cccc0000;
            11'd11: palabra = 54'h09000400002000;
            11'd12: palabra = 54'h05000000000000;
            11'd13: palabra = 54'h04940d33340000;
            11'd14: palabra = 54'h09000400007fdf;
            11'd15: palabra = 54'h05040000000000;
            11'd16: palabra = 54'h04980400000000;
            11'd17: palabra = 54'h05080c00000000;
            11'd18: palabra = 54'h09000400007fdf;
            11'd19: palabra = 54'h050c0000000000;
            11'd20: palabra = 54'h04800200000000;
            11'd21: palabra = 54'h04840200000000;
            11'd22: palabra = 54'h08080000000000;
            11'd23: palabra = 54'h02000000000000;
            11'd24: palabra = 54'h010004000001e8;
            11'd25: palabra = 54'h061003ff7c0000;
            11'd26: palabra = 54'h05100400000000;
            11'd27: palabra = 54'h010003000002d2;
            11'd28: palabra = 54'h03000d000001e9;
            11'd29: palabra = 54'h01000300000383;
            11'd30: palabra = 54'h03000d000002d3;
            11'd31: palabra = 54'h010002800005f2;
            11'd32: palabra = 54'h03000d80000384;
            11'd33: palabra = 54'h010002800007b9;
            11'd34: palabra = 54'h03000d800005f3;
            11'd35: palabra = 54'h05200000000000;
            11'd36: palabra = 54'h0100040000923e;
            11'd37: palabra = 54'h08000000000000;
            11'd38: palabra = 54'h04200400000000;
            11'd39: palabra = 54'h0c000d33340bfc;
            11'd40: palabra = 54'h030002cccc07ba;
            11'd41: palabra = 54'h02000000000c1a;
            11'd42: palabra = 54'h010004000028a4;
            11'd43: palabra = 54'h04140c00000000;
            11'd44: palabra = 54'h08040000000000;
            11'd45: palabra = 54'h04140400000000;
            11'd46: palabra = 54'h05140400000000;
            11'd47: palabra = 54'h08000000000000;
            11'd48: palabra = 54'h0100020000342e;
            11'd49: palabra = 54'h03000e000028a5;
            11'd50: palabra = 54'h0200000000342f;
            11'd51: palabra = 54'h01000400004c06;
            11'd52: palabra = 54'h08000000000000;
            11'd53: palabra = 54'h04200400000000;
            11'd54: palabra = 54'h0c040d333451cc;
            11'd55: palabra = 54'h030002cccc4c07;
            11'd56: palabra = 54'h020000000051ea;
            11'd57: palabra = 54'h01000400006cf1;
            11'd58: palabra = 54'h04180c00000000;
            11'd59: palabra = 54'h08040000000000;
            11'd60: palabra = 54'h04180400000000;
            11'd61: palabra = 54'h05180400000000;
            11'd62: palabra = 54'h08000000000000;
            11'd63: palabra = 54'h01000200007df8;
            11'd64: palabra = 54'h03000e00006cf2;
            11'd65: palabra = 54'h02000000007df9;
            11'd66: palabra = 54'h04800400000000;
            11'd67: palabra = 54'h080c0000000000;
            11'd68: palabra = 54'h0100026668539e;
            11'd69: palabra = 54'h010002666864f9;
            11'd70: palabra = 54'h01000d99987935;
            11'd71: palabra = 54'h01000266688ac4;
            11'd72: palabra = 54'h01000d999818db;
            11'd73: palabra = 54'h01000d999829d8;
            11'd74: palabra = 54'h01000d99983b04;
            11'd75: palabra = 54'h05880000000000;
            11'd76: palabra = 54'h04840400000000;
            11'd77: palabra = 54'h080c0000000000;
            11'd78: palabra = 54'h01000266680e5d;
            11'd79: palabra = 54'h01000266682359;
            11'd80: palabra = 54'h01000d99983084;
            11'd81: palabra = 54'h01000266684551;
            11'd82: palabra = 54'h01000d99985f71;
            11'd83: palabra = 54'h01000d99986f18;
            11'd84: palabra = 54'h01000d99987ec0;
            11'd85: palabra = 54'h058c0000000000;
            default: palabra = 54'h0;
        endcase
    end
endmodule

`default_nettype wire
