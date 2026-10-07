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
// Dos etapas (REGISTRADA = 1 en el núcleo): la 1 elige los operandos y la 2
// hace una sola operación (suma o máximo) y satura. En una etapa, la ALU daba
// 157 MHz con una colocación y 80 con otra (fails.md, F-11). Con REGISTRADA = 0
// es combinacional: así la prueba contra el modelo no necesita reloj.
`default_nettype none

module alu #(
    parameter integer REGISTRADA = 1
) (
    input  wire               clk,
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
    localparam [5:0] RDA = 6'd1,  WRA = 6'd2,   WRAP = 6'd3,
                     RDAX = 6'd4, WRAX = 6'd5, RDFX = 6'd6,  MAXX = 6'd7,
                     MULX = 6'd8, SOF = 6'd9,  CHO = 6'd12,
                     LDAX = 6'd13, CLR = 6'd14, ABSA = 6'd15;   // NOP (0) y SKP (11): ACC igual

    // Todos los productos útiles caben en 49 bit (24 × 24 con signo).
    wire signed [49:0] p50   = p[49:0];
    wire signed [49:0] acc50 = {{2{acc[47]}}, acc};
    wire signed [49:0] lr16  = {{10{lr[23]}}, lr, 16'd0};
    wire signed [49:0] r16   = {{10{r[23]}}, r, 16'd0};
    wire signed [49:0] d24   = {{8{addr[17]}}, addr, 24'd0};

    // ── Etapa 1: operandos y modo ────────────────────────────────────────
    // MAXX compara |ACC| con |R·C|; ABSA pasa |ACC| (|x| + 0); el resto suma.
    reg signed [49:0] x_a, x_b;
    reg               maximo;
    always @(*) begin
        x_a = acc50;   // NOP, SKP: ACC + 0
        x_b = 50'sd0;
        maximo = 1'b0;
        case (op)
            RDA, RDAX, CHO: x_b = p50;
            WRA, WRAX:      begin x_a = 50'sd0; x_b = p50; end
            WRAP:           begin x_a = lr16;   x_b = p50; end
            RDFX:           begin x_a = r16;    x_b = p50; end
            SOF:            begin x_a = d24;    x_b = p50; end
            MULX:           begin x_a = 50'sd0; x_b = p50 >>> 7; end
            LDAX:           x_a = r16;
            CLR:            x_a = 50'sd0;
            MAXX:           begin
                x_a = acc50[49] ? -acc50 : acc50;
                x_b = p50[49] ? -p50 : p50;
                maximo = 1'b1;
            end
            ABSA:           x_a = acc50[49] ? -acc50 : acc50;
            default:        ;
        endcase
    end

    // Registro entre etapas (REGISTRADA = 1) o paso directo (0, para la prueba).
    reg signed [49:0] r_a, r_b;
    reg               r_max;
    always @(posedge clk) begin
        r_a <= x_a; r_b <= x_b; r_max <= maximo;
    end
    wire signed [49:0] e_a   = (REGISTRADA != 0) ? r_a : x_a;
    wire signed [49:0] e_b   = (REGISTRADA != 0) ? r_b : x_b;
    wire               e_max = (REGISTRADA != 0) ? r_max : maximo;

    // ── Etapa 2: una operación y la saturación ───────────────────────────
    wire signed [49:0] s = e_max ? ((e_a > e_b) ? e_a : e_b) : (e_a + e_b);
    saturar_acc u_sat (.valor(s), .acc(acc_sig));
endmodule

`default_nettype wire
