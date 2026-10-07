// SPDX-License-Identifier: MIT
//
// Paso final de cada instrucción: combina el producto `p` del multiplicador con
// el ACC y los operandos, y satura a 48 bit. Equivale a los manejadores de
// model/sofifi/domain/nucleo.py si el secuenciador pone en el multiplicador:
//
//   RDA, CHO        p = M[a]·C  (en CHO, el valor interpolado y con ventana)
//   RDAX, MAXX      p = R·C
//   WRA, WRAX, WRAP p = a24·C
//   RDFX            p = (a24 − R)·C
//   MULX            p = a24·R
//   SOF             p = a24·C
//
// CLIP no pasa por aquí: el núcleo calcula la curva suave con curva_fin y la
// registra antes de escribirla en el ACC (camino crítico a 100 MHz).
//
// Los desplazamientos a la derecha son aritméticos: el floor del modelo.
`default_nettype none

module alu (
    input  wire        [5:0]  op,
    input  wire signed [47:0] acc,
    /* verilator lint_off UNUSEDSIGNAL */
    input  wire signed [62:0] p,      // solo se usan 50 bit: el mayor producto es 24 × 24
    /* verilator lint_on UNUSEDSIGNAL */
    input  wire signed [23:0] lr,
    input  wire signed [23:0] r,
    input  wire        [17:0] addr,   // D de SOF en S2.15
    output wire signed [47:0] acc_sig
);
    localparam [5:0] NOP = 6'd0, RDA = 6'd1,  WRA = 6'd2,   WRAP = 6'd3,
                     RDAX = 6'd4, WRAX = 6'd5, RDFX = 6'd6,  MAXX = 6'd7,
                     MULX = 6'd8, SOF = 6'd9,  SKP = 6'd11, CHO = 6'd12,
                     LDAX = 6'd13, ABSA = 6'd15;   // CLR (14): rama por defecto, 0 + 0

    // Todos los productos útiles caben en 49 bit (24 × 24 con signo).
    wire signed [49:0] p50   = p[49:0];
    wire signed [49:0] acc50 = {{2{acc[47]}}, acc};
    wire signed [49:0] abs_acc = acc50[49] ? -acc50 : acc50;
    wire signed [49:0] abs_p   = p50[49] ? -p50 : p50;
    wire signed [49:0] lr16  = {{10{lr[23]}}, lr, 16'd0};
    wire signed [49:0] r16   = {{10{r[23]}}, r, 16'd0};
    wire signed [49:0] d24   = {{8{addr[17]}}, addr, 24'd0};

    // Un solo sumador: se eligen primero los sumandos y se suma una vez
    // (segunda vuelta, ADR 0010). MAXX, ABSA y CLIP usan sus propias rutas.
    reg signed [49:0] sum_a, sum_b, s;
    always @(*) begin
        sum_a = 50'sd0;
        sum_b = 50'sd0;
        case (op)
            RDA, RDAX, CHO: begin sum_a = acc50; sum_b = p50; end
            WRA, WRAX:      sum_b = p50;
            WRAP:           begin sum_a = lr16; sum_b = p50; end
            RDFX:           begin sum_a = r16;  sum_b = p50; end
            SOF:            begin sum_a = d24;  sum_b = p50; end
            MULX:           sum_b = p50 >>> 7;
            LDAX:           sum_a = r16;
            default:        ;
        endcase
        case (op)
            MAXX:    s = (abs_acc > abs_p) ? abs_acc : abs_p;
            ABSA:    s = abs_acc;
            NOP, SKP: s = acc50;
            default: s = sum_a + sum_b;   // CLR: 0 + 0
        endcase
    end

    saturar_acc u_sat (.valor(s), .acc(acc_sig));
endmodule

`default_nettype wire
