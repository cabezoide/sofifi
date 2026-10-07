// SPDX-License-Identifier: MIT
//
// Núcleo DSP microcodificado de SOFIFI (ADR 0006, ADR 0009). Equivale bit a bit a
// model/sofifi/domain/nucleo.py (ADR 0003). Por muestra (`tick`):
//
//   1. Carga adcl, adcr, los potenciómetros y sw en sus registros.
//   2. Los LFO avanzan con los lfoN_rate de la muestra anterior.
//   3. ACC = 0, LR = 0 y ejecuta el programa de principio a fin.
//   4. La memoria avanza; dacl y dacr salen por `dac_l`/`dac_r` y `fin` da un pulso.
//
// Al salir del reset, el núcleo borra la memoria de retardo (cfg_palabras
// ciclos) para empezar como el modelo, con todo a cero; mientras tanto,
// `ocupado` vale 1 y no atiende ticks. El reset no borra la BSRAM por sí solo.
//
// Primera versión: multiciclo sin solapamiento (spec de la Fase 04). Cada
// instrucción espera a su resultado antes de la siguiente. El multiplicador y la
// memoria tienen la misma latencia: se presentan operandos en un ciclo y el
// resultado está 5 ciclos después (LAT). Las dos salidas van registradas: la
// BSRAM en modo bypass y la lógica detrás de ella fallaban en el silicio por
// encima de 100 MHz aunque nextpnr diera más (fails.md, F-11).
// `ciclos` da los de la última muestra.
//
// El programa se carga por `prog_*` (palabras de 54 bit) y `cfg_*` (lo que el
// ensamblador deja en el .json). Se cargan con el núcleo parado.
`default_nettype none

module nucleo #(
    parameter integer PALABRAS_MAX = 43_008
) (
    input  wire               clk,
    input  wire               rst,
    // Programa
    input  wire               prog_we,
    input  wire [10:0]        prog_dir,
    input  wire [53:0]        prog_dato,
    input  wire [11:0]        cfg_instrucciones,   // 1..2048
    input  wire [15:0]        cfg_palabras,        // memoria de retardo, 1..PALABRAS_MAX
    input  wire [7:0]         cfg_lfo_tipos,       // 2 bit por LFO: 0 SIN, 1 RND, 2 RAMP
    input  wire [59:0]        cfg_lfo_excursiones, // 15 bit por LFO
    // Muestra
    input  wire               tick,
    input  wire signed [23:0] adc_l,
    input  wire signed [23:0] adc_r,
    input  wire [143:0]       pots,                // 6 × 24 bit
    input  wire signed [23:0] sw,
    output reg  signed [23:0] dac_l,
    output reg  signed [23:0] dac_r,
    output reg                fin,
    output wire               ocupado,
    output reg  [15:0]        ciclos
);
    // ── Mapa de registros y códigos (isa.py) ──────────────────────────────
    localparam [5:0] ADCL = 6'd32, ADCR = 6'd33, DACL = 6'd34, DACR = 6'd35,
                     LFO_BASE = 6'd42, SW = 6'd50;
    localparam integer POT_BASE = 36;
    // NOP (0), LDAX (13), CLR (14) y ABSA (15) van por la rama por defecto.
    localparam [5:0] RDA = 6'd1,  WRA = 6'd2,   WRAP = 6'd3,
                     RDAX = 6'd4, WRAX = 6'd5, RDFX = 6'd6,  MAXX = 6'd7,
                     MULX = 6'd8, SOF = 6'd9,  CLIP = 6'd10, SKP = 6'd11,
                     CHO = 6'd12;
    localparam [1:0] T_SIN = 2'd0, T_RAMP = 2'd2;   // RND (1): rama por defecto de CHO
    localparam [2:0] LAT = 3'd5;

    // ── Estado ────────────────────────────────────────────────────────────
    localparam [2:0] E_PARADO = 3'd0, E_LFO = 3'd1, E_LEER = 3'd2, E_DECO = 3'd3,
                     E_EJEC = 3'd4, E_FIN = 3'd5, E_BORRAR = 3'd6, E_ESCR = 3'd7;
    reg [2:0]  estado;
    reg [11:0] pc;
    reg [4:0]  paso;
    reg [2:0]  espera;
    reg        primera;
    reg signed [47:0] acc;
    reg signed [23:0] lr;
    reg signed [23:0] regs [0:63];
    reg [53:0] ins;
    reg [15:0] cuenta;
    reg [15:0] borrar;
    reg [1:0]  lee;
    reg        escr;

    assign ocupado = (estado != E_PARADO);

    wire [5:0]         op = ins[53:48];
    wire [5:0]         rg = ins[47:42];
    /* verilator lint_off UNUSEDSIGNAL */
    wire [5:0]         fl = ins[41:36];   // SKP usa 4 bit; CHO, 2
    /* verilator lint_on UNUSEDSIGNAL */
    wire signed [17:0] cf = ins[35:18];
    wire [17:0]        ad = ins[17:0];
    // Operandos registrados en E_DECO (timing a 100 MHz): R, depth y el LFO
    // elegido. Los LFO no cambian mientras corre el programa.
    reg  signed [23:0] r_d, dep_d, tri_d, ven_d, actual_d;
    reg         [23:0] fase_d;
    reg         [1:0]  tipo_d;
    reg         [14:0] exc_d;

    // ── Microcódigo: 2 048 × 54 en BSRAM, lectura en 3 ciclos ─────────────
    // bsram_pipe: bloques con registro de salida (F-11). E_LEER espera a la
    // palabra. Escrito como array, una parte salía en SPX9 (hold, Fase 04).
    wire [53:0] ins_leida;
    bsram_pipe #(.PALABRAS(2048), .ANCHO(54)) u_microcodigo (
        .clk(clk), .we(prog_we), .dir_w(prog_dir), .dato_w(prog_dato),
        .dir_r(pc[10:0]), .dato_r(ins_leida)
    );

    // ── a24 = ACC redondeado y saturado a dato, registrado ────────────────
    // El ACC solo cambia al final de una instrucción; E_LEER y E_DECO dan tiempo
    // a que a24 esté al día cuando empieza la siguiente.
    wire signed [23:0] a24_c;
    acc_a_dato u_a24 (.acc(acc), .dato(a24_c));
    reg  signed [23:0] a24;
    always @(posedge clk) a24 <= a24_c;

    // ── Multiplicador (LAT ciclos) ────────────────────────────────────────
    reg  signed [26:0] ma;
    reg  signed [35:0] mb;
    wire signed [62:0] p_mult;
    reg  signed [62:0] p_1, p;     // salida registrada dos veces: LAT igual a la memoria
    mult_27x36 u_mult (.clk(clk), .a(ma), .b(mb), .p(p_mult));
    always @(posedge clk) begin
        p_1 <= p_mult;
        p   <= p_1;
    end
    function automatic signed [26:0] a27(input signed [24:0] v);
        a27 = {{2{v[24]}}, v};
    endfunction
    function automatic signed [35:0] b36(input signed [24:0] v);
        b36 = {{11{v[24]}}, v};
    endfunction

    // ── Memoria de retardo (LAT ciclos de lectura) ────────────────────────
    reg  signed [16:0] mdir_r, mdir_w;
    reg                mwe;
    reg  signed [23:0] mdato_w;
    reg                mavanzar;
    wire signed [23:0] mdato_r;
    memoria_retardo #(.PALABRAS_MAX(PALABRAS_MAX)) u_mem (
        .clk(clk), .rst(rst), .palabras(cfg_palabras), .avanzar(mavanzar),
        .dir_r(mdir_r), .dato_r(mdato_r), .we(mwe), .dir_w(mdir_w), .dato_w(mdato_w)
    );

    // ── LFO ───────────────────────────────────────────────────────────────
    reg                lfo_avanzar;
    wire               lfo_listo;
    wire [23:0]        lfo_fase;
    wire signed [23:0] lfo_tri, lfo_ven, lfo_actual;
    lfo_banco u_lfo (
        .clk(clk), .rst(rst), .tipos(cfg_lfo_tipos), .avanzar(lfo_avanzar),
        .rates({regs[LFO_BASE + 6], regs[LFO_BASE + 4], regs[LFO_BASE + 2], regs[LFO_BASE]}),
        .listo(lfo_listo), .sel(ins_leida[43:42]), .media(ins_leida[37]),
        .fase_sel(lfo_fase), .tri_sel(lfo_tri), .ven_sel(lfo_ven), .actual_sel(lfo_actual)
    );
    wire [1:0]         sel_leida = ins_leida[43:42];

    // ── Tabla Hermite (1 ciclo) ───────────────────────────────────────────
    reg  [7:0]  frac;
    wire [71:0] coefs;
    reg  [71:0] coefs_r;
    tabla_hermite u_tabla (.frac(frac), .coefs(coefs));
    always @(posedge clk) coefs_r <= coefs;
    wire signed [17:0] c0 = coefs_r[71:54], c1 = coefs_r[53:36], c2 = coefs_r[35:18], c3 = coefs_r[17:0];

    // ── ALU y curva suave ─────────────────────────────────────────────────
    reg  signed [23:0] x;          // operando guardado (CLIP, SIN)
    reg  signed [25:0] tres_x;     // 3·x, calculado al fijar x
    reg  signed [23:0] y_clip;     // curva suave registrada (CLIP y LFO SIN)
    reg  signed [24:0] dif;        // a24 − R (RDFX), registrado
    reg  signed [23:0] v_r;        // valor Hermite convertido a dato, registrado
    // Todas las entradas del multiplicador salen de registros: con aritmética
    // delante, el multiplexor de `ma` era el camino crítico (fails.md, F-11).
    always @(posedge clk) dif <= {a24[23], a24} - {r_d[23], r_d};
    wire signed [47:0] acc_alu;
    // Salida de la ALU registrada: E_ESCR la escribe en el ACC un ciclo después
    // (la ALU entera en el mismo ciclo que el ACC era camino crítico, F-11).
    reg  signed [47:0] alu_r;
    always @(posedge clk) alu_r <= acc_alu;
    alu #(.REGISTRADA(1)) u_alu (
        .clk(clk), .op(op), .acc(acc), .p(p), .lr(lr), .r(r_d), .addr(ad), .acc_sig(acc_alu)
    );
    wire signed [23:0] curva;
    curva_fin u_curva (.tres_x(tres_x), .p(p), .y(curva));

    // ── CHO: desplazamiento, lecturas y suma Hermite ──────────────────────
    reg  signed [16:0] base;       // dirección entera de la lectura modulada
    reg         [23:0] q8;         // desplazamiento de la lectura, en 1/256 de muestra
    reg  signed [47:0] suma;
    wire signed [23:0] v_hermite;
    acc_a_dato u_v (.acc(suma), .dato(v_hermite));
    wire signed [49:0] p50 = p[49:0];
    wire signed [24:0] p_23 = p50[47:23];   // p >> 23 en 25 bit (x2, amplitud, v·ventana)
    wire        [23:0] q8_ramp = p[39:16];                                   // (fase·E) >> 16
    /* verilator lint_off UNUSEDSIGNAL */
    wire signed [49:0] q8_sin  = {27'd0, exc_d, 8'd0} + (p50 >>> 15);       // (E << 8) + (amp·E >> 15)
    /* verilator lint_on UNUSEDSIGNAL */

    // ── SKP ───────────────────────────────────────────────────────────────
    wire saltar = (fl[0] & ~primera) | (fl[1] & (acc == 48'sd0)) |
                  (fl[2] & ~acc[47]) | (fl[3] & acc[47]);

    integer i;
    always @(posedge clk) begin
        fin         <= 1'b0;
        mwe         <= 1'b0;
        mavanzar    <= 1'b0;
        lfo_avanzar <= 1'b0;
        if (rst) begin
            estado <= E_BORRAR; borrar <= 16'd0; lee <= 2'd0; escr <= 1'b0;
            pc <= 12'd0; paso <= 5'd0; espera <= 3'd0;
            primera <= 1'b1; acc <= 48'sd0; lr <= 24'sd0; ins <= 54'd0;
            dac_l <= 24'sd0; dac_r <= 24'sd0; ciclos <= 16'd0; cuenta <= 16'd0;
            for (i = 0; i < 64; i = i + 1) regs[i] <= 24'sd0;
        end else begin
            if (estado != E_PARADO && estado != E_BORRAR) cuenta <= cuenta + 1'b1;
            case (estado)
            E_BORRAR: begin
                mwe <= 1'b1; mdir_w <= {1'b0, borrar}; mdato_w <= 24'sd0;
                if (borrar == cfg_palabras - 1'b1) estado <= E_PARADO;
                else borrar <= borrar + 1'b1;
            end
            E_PARADO: if (tick) begin
                regs[ADCL] <= adc_l;
                regs[ADCR] <= adc_r;
                for (i = 0; i < 6; i = i + 1) regs[POT_BASE + i] <= pots[24*i +: 24];
                regs[SW] <= sw;
                lfo_avanzar <= 1'b1;
                acc <= 48'sd0; lr <= 24'sd0; pc <= 12'd0; cuenta <= 16'd1;
                estado <= E_LFO;
            end
            E_LFO: if (lfo_listo) estado <= E_LEER;
            E_LEER: begin   // la palabra de pc tarda 3 ciclos en salir del microcódigo
                if (lee == 2'd2) begin
                    lee <= 2'd0;
                    estado <= (pc == cfg_instrucciones) ? E_FIN : E_DECO;
                end else begin
                    lee <= lee + 1'b1;
                end
            end
            E_DECO: begin
                ins <= ins_leida;
                r_d      <= regs[ins_leida[47:42]];
                dep_d    <= regs[6'd43 + {3'd0, sel_leida, 1'b0}];   // lfoN_depth = 42 + 2N + 1
                fase_d   <= lfo_fase;
                tri_d    <= lfo_tri;
                ven_d    <= lfo_ven;
                actual_d <= lfo_actual;
                tipo_d   <= cfg_lfo_tipos[2*sel_leida +: 2];
                exc_d    <= cfg_lfo_excursiones[15*sel_leida +: 15];
                paso <= 5'd0; espera <= 3'd0;
                estado <= E_EJEC;
            end
            E_EJEC: if (espera != 3'd0) begin
                espera <= espera - 1'b1;
            end else begin
                // Por defecto, la instrucción termina en este ciclo.
                case (op)
                RDAX, MAXX, WRA, WRAX, WRAP, RDFX, MULX, SOF:
                    if (paso == 5'd0 && op == RDFX) begin
                        paso <= 5'd2;   // dif = a24 − R se registra en este ciclo
                    end else if (paso == 5'd0 || paso == 5'd2) begin
                        case (op)
                            RDFX:    ma <= a27(dif);
                            RDAX, MAXX: ma <= a27({r_d[23], r_d});
                            default: ma <= a27({a24[23], a24});
                        endcase
                        mb <= (op == MULX) ? b36({r_d[23], r_d}) : b36({{7{cf[17]}}, cf});
                        if (op == WRA || op == WRAP) begin
                            mwe <= 1'b1; mdir_w <= {1'b0, ad[15:0]}; mdato_w <= a24;
                        end
                        if (op == WRAX) regs[rg] <= a24;
                        paso <= 5'd1; espera <= LAT - 1'b1;
                    end else begin
                        estado <= E_ESCR;
                    end
                RDA:
                    case (paso)
                    5'd0: begin mdir_r <= {1'b0, ad[15:0]}; paso <= 5'd1; espera <= LAT - 1'b1; end
                    5'd1: begin
                        lr <= mdato_r;
                        ma <= a27({mdato_r[23], mdato_r}); mb <= b36({{7{cf[17]}}, cf});
                        paso <= 5'd2; espera <= LAT - 1'b1;
                    end
                    default: begin estado <= E_ESCR; end
                    endcase
                CLIP:
                    case (paso)
                    5'd0: begin
                        x <= a24;
                        tres_x <= {{2{a24[23]}}, a24} + {a24[23], a24, 1'b0};
                        ma <= a27({a24[23], a24}); mb <= b36({a24[23], a24});
                        paso <= 5'd1; espera <= LAT - 1'b1;
                    end
                    5'd1: begin
                        ma <= a27(p_23); mb <= b36({x[23], x});   // x2 · x
                        paso <= 5'd2; espera <= LAT - 1'b1;
                    end
                    5'd2: begin y_clip <= curva; paso <= 5'd3; end
                    default: begin   // ACC = curva_suave(a24) << 16
                        acc <= {{8{y_clip[23]}}, y_clip, 16'd0};
                        pc <= pc + 1'b1; estado <= E_LEER;
                    end
                    endcase
                CHO:
                    case (paso)
                    // Desplazamiento q8 según el tipo de LFO (lfo.py).
                    5'd0: begin
                        case (tipo_d)
                            T_RAMP: begin
                                ma <= a27({1'b0, fase_d}); mb <= b36({10'd0, exc_d});
                                paso <= 5'd5;
                            end
                            T_SIN: begin
                                x <= tri_d;
                                tres_x <= {{2{tri_d[23]}}, tri_d} + {tri_d[23], tri_d, 1'b0};
                                ma <= a27({tri_d[23], tri_d}); mb <= b36({tri_d[23], tri_d});
                                paso <= 5'd1;
                            end
                            default: begin   // RND: forma = actual
                                ma <= a27({actual_d[23], actual_d});
                                mb <= b36({dep_d[23], dep_d});
                                paso <= 5'd3;
                            end
                        endcase
                        espera <= LAT - 1'b1;
                    end
                    5'd1: begin   // SIN: x2 · x
                        ma <= a27(p_23); mb <= b36({x[23], x});
                        paso <= 5'd2; espera <= LAT - 1'b1;
                    end
                    5'd2: begin y_clip <= curva; paso <= 5'd23; end   // forma = curva_suave(tri)
                    5'd23: begin   // SIN: forma · depth
                        ma <= a27({y_clip[23], y_clip}); mb <= b36({dep_d[23], dep_d});
                        paso <= 5'd3; espera <= LAT - 1'b1;
                    end
                    5'd3: begin   // amplitud = (forma·depth) >> 23; amplitud · E
                        ma <= a27(p_23); mb <= b36({10'd0, exc_d});
                        paso <= 5'd4; espera <= LAT - 1'b1;
                    end
                    // q8 listo: se registra, y la base y la primera lectura van en pasos
                    // aparte (tres sumas seguidas eran el camino crítico, fails.md F-11).
                    5'd4: begin q8 <= q8_sin[23:0]; paso <= 5'd20; end
                    5'd5: begin q8 <= q8_ramp;      paso <= 5'd20; end
                    5'd20: begin   // base = addr + q8 >> 8; frac = q8 & 0xFF
                        base <= $signed({1'b0, ad[15:0]}) + $signed({1'b0, q8[23:8]});
                        frac <= q8[7:0];
                        paso <= 5'd21;
                    end
                    5'd21: begin mdir_r <= base - 17'sd1; paso <= 5'd6; end
                    5'd6: begin mdir_r <= base;          paso <= 5'd7; end
                    5'd7: begin mdir_r <= base + 17'sd1; paso <= 5'd8; end
                    5'd8: begin mdir_r <= base + 17'sd2; paso <= 5'd24; end
                    5'd24: paso <= 5'd9;   // la primera lectura llega LAT ciclos después
                    // Llegan M[base−1], M[base], M[base+1] y M[base+2] (LAT ciclos
                    // después de pedirlas) y entran al multiplicador con c0..c3.
                    5'd9:  begin ma <= a27({mdato_r[23], mdato_r}); mb <= b36({{7{c0[17]}}, c0}); paso <= 5'd10; end
                    5'd10: begin ma <= a27({mdato_r[23], mdato_r}); mb <= b36({{7{c1[17]}}, c1}); paso <= 5'd11; end
                    5'd11: begin ma <= a27({mdato_r[23], mdato_r}); mb <= b36({{7{c2[17]}}, c2}); paso <= 5'd12; end
                    5'd12: begin ma <= a27({mdato_r[23], mdato_r}); mb <= b36({{7{c3[17]}}, c3}); paso <= 5'd25; end
                    5'd25: paso <= 5'd13;   // el primer producto llega LAT ciclos después
                    // Los productos llegan en los pasos 13 a 16.
                    5'd13: begin suma <= p[47:0];        paso <= 5'd14; end
                    5'd14: begin suma <= suma + p[47:0]; paso <= 5'd15; end
                    5'd15: begin suma <= suma + p[47:0]; paso <= 5'd16; end
                    5'd16: begin suma <= suma + p[47:0]; paso <= 5'd17; end
                    5'd17: begin v_r <= v_hermite; paso <= 5'd22; end   // v = acc_a_dato(suma)
                    5'd22: begin   // con NA, v pasa por la ventana
                        if (fl[0]) begin
                            ma <= a27({v_r[23], v_r}); mb <= b36({ven_d[23], ven_d});
                            paso <= 5'd18; espera <= LAT - 1'b1;
                        end else begin
                            lr <= v_r;
                            ma <= a27({v_r[23], v_r}); mb <= b36({{7{cf[17]}}, cf});
                            paso <= 5'd19; espera <= LAT - 1'b1;
                        end
                    end
                    5'd18: begin   // v = (v · ventana) >> 23
                        lr <= p50[46:23];
                        ma <= a27(p_23); mb <= b36({{7{cf[17]}}, cf});
                        paso <= 5'd19; espera <= LAT - 1'b1;
                    end
                    default: begin estado <= E_ESCR; end
                    endcase
                SKP: begin
                    pc <= pc + 12'd1 + (saltar ? ad[11:0] : 12'd0);
                    estado <= E_LEER;
                end
                default: begin   // NOP, LDAX, CLR, ABSA
                    estado <= E_ESCR;
                end
                endcase
            end
            E_ESCR: begin   // la ALU tiene dos etapas y alu_r una más: 2 ciclos
                if (escr) begin
                    escr <= 1'b0;
                    acc <= alu_r;
                    pc <= pc + 1'b1; estado <= E_LEER;
                end else begin
                    escr <= 1'b1;
                end
            end
            E_FIN: begin
                mavanzar <= 1'b1;
                primera <= 1'b0;
                dac_l <= regs[DACL];
                dac_r <= regs[DACR];
                ciclos <= cuenta;
                fin <= 1'b1;
                estado <= E_PARADO;
            end
            default: estado <= E_PARADO;
            endcase
        end
    end
endmodule

`default_nettype wire
