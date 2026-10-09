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
// Segmentado en orden (ADR 0014): una instrucción presenta sus operandos al
// multiplicador y el producto llega LAT = 5 ciclos después. La instrucción no
// espera a su producto: lo deja en la línea de retiro y el secuenciador pasa a
// la siguiente. El retiro aplica los productos al ACC en el orden del programa.
// Solo espera la instrucción que lee el ACC (o a24) hasta que el retiro se vacía,
// y la que lee un registro recién escrito por WRAX. El microcódigo llega por
// una cola de búsqueda continua. Las dos salidas del multiplicador y de la
// BSRAM van registradas: en modo bypass fallaban en el silicio por encima de
// 100 MHz aunque nextpnr diera más (fails.md, F-11).
// Con más de GRUPO_MEM bloques, la memoria va segmentada y sus lecturas tardan 4
// ciclos más (LAT_MEM): su dirección llegaba a bloques de todo el chip en un
// solo ciclo y el silicio fallaba según la colocación (fails.md, F-15).
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
    input  wire               cfg_absoluta,        // 1: el programa usa la región absoluta (RDAA, WRAA)
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
    output reg  [15:0]        ciclos,
    // Depuración: el top HIL graba la traza (pc, ACC) para localizar en el
    // silicio la primera instrucción que falla (fails.md, F-15).
    output wire [11:0]        traza_pc,
    output wire signed [47:0] traza_acc
);
    // ── Mapa de registros y códigos (isa.py) ──────────────────────────────
    localparam [5:0] ADCL = 6'd32, ADCR = 6'd33, DACL = 6'd34, DACR = 6'd35,
                     LFO_BASE = 6'd42, SW = 6'd50;
    localparam integer POT_BASE = 36;
    // NOP (0), LDAX (13), CLR (14) y ABSA (15) van por la rama por defecto.
    localparam [5:0] RDA = 6'd1,  WRA = 6'd2,   WRAP = 6'd3,
                     RDAX = 6'd4, WRAX = 6'd5, RDFX = 6'd6,  MAXX = 6'd7,
                     MULX = 6'd8, SOF = 6'd9,  CLIP = 6'd10, SKP = 6'd11,
                     CHO = 6'd12, RDAA = 6'd16, WRAA = 6'd17;
    localparam [1:0] T_SIN = 2'd0, T_RAMP = 2'd2;   // RND (1): rama por defecto de CHO
    localparam [3:0] LAT = 4'd5;
    localparam integer GRUPO_MEM = 8;   // bloques de memoria de retardo por grupo
    localparam integer SEG_MEM   = ((PALABRAS_MAX + 1023) / 1024 > GRUPO_MEM) ? 1 : 0;
    localparam [3:0] EXTRA_MEM = 4'(4 * SEG_MEM);
    localparam [3:0] LAT_MEM   = LAT + EXTRA_MEM;

    // ── Estado ────────────────────────────────────────────────────────────
    // E_LEER decodifica la cabeza de la cola en cuanto no hay dependencia.
    localparam [2:0] E_PARADO = 3'd0, E_LFO = 3'd1, E_LEER = 3'd2,
                     E_EJEC = 3'd4, E_FIN = 3'd5, E_BORRAR = 3'd6;
    reg [2:0]  estado;
    reg [11:0] pc;
    reg [4:0]  paso;
    reg [3:0]  espera;
    reg        primera;
    reg signed [47:0] acc;
    reg signed [23:0] lr;
    reg signed [23:0] regs [0:63];
    reg [53:0] ins;
    reg [15:0] cuenta;
    reg [15:0] borrar;
    // Búsqueda continua del microcódigo: pc_mc es la siguiente dirección que se
    // pide. La palabra pedida en t sale de ins_leida en t+4 (`vuelo` sigue las
    // cuatro en camino) y entra en la cola. La cabeza de la cola va en un
    // registro aparte: de ella salen la decodificación, el LFO elegido y los
    // candidatos del banco. `ocup` cuenta las palabras pedidas y aún no
    // decodificadas; no pasa de COLA. Un salto o una muestra nueva vacían todo.
    // Con 4 basta: se decodifica como mucho una instrucción cada 2 ciclos y la
    // cola se llena mientras una instrucción espera a su dependencia.
    localparam integer COLA = 4;
    reg [11:0] pc_mc;
    reg [3:0]  vuelo;
    reg [2:0]  ocup;
    (* ram_style = "logic" *)   // en BSRAM no cabe: todas están ocupadas
    reg [53:0] cola [0:3];
    reg [1:0]  cola_esc, cola_lec;
    reg [2:0]  cola_n;
    reg [53:0] cabeza;
    reg        cab_v, cab_vieja;   // cab_vieja: la cabeza lleva al menos un ciclo
    reg        cab_lee_acc, cab_lee_reg;
    reg        vaciar;             // la orden de vaciar, desde el secuenciador
    reg [11:0] destino;
    wire       tomar;              // la decodificación consume la cabeza

    assign ocupado   = (estado != E_PARADO);
    assign traza_pc  = acc_pc;   // el pc de la siguiente a la que escribió el ACC
    assign traza_acc = acc;

    wire [5:0]         op = ins[53:48];
    wire [5:0]         rg = ins[47:42];
    /* verilator lint_off UNUSEDSIGNAL */
    wire [5:0]         fl = ins[41:36];   // SKP usa 4 bit; CHO, 2
    /* verilator lint_on UNUSEDSIGNAL */
    wire signed [17:0] cf = ins[35:18];
    wire [17:0]        ad = ins[17:0];
    // Operandos registrados al decodificar (timing a 100 MHz): R, depth y el LFO
    // elegido. Los LFO no cambian mientras corre el programa.
    reg  signed [23:0] r_d, dep_d, tri_d, ven_d, actual_d;
    reg         [23:0] fase_d;
    reg         [1:0]  tipo_d;
    reg         [14:0] exc_d;

    // ── Microcódigo: 2 048 × 54 en BSRAM, lectura en 3 ciclos ─────────────
    // bsram_pipe: bloques con registro de salida (F-11). Escrito como array,
    // una parte salía en SPX9 (hold, Fase 04). La palabra se registra en
    // ins_leida y otra vez en la cabeza de la cola: el multiplexor del banco de
    // registros (64:1) no arranca de un cable que cruza el chip (fails.md, F-15).
    wire [53:0] ins_bsram;
    reg  [53:0] ins_leida;
    wire        pedir = (ocup < 3'(COLA)) && !vaciar;
    wire        llega = vuelo[3];
    wire        cargar_cab = (!cab_v || tomar) && cola_n != 3'd0;
    always @(posedge clk) begin
        if (rst || vaciar) begin
            pc_mc <= rst ? 12'd0 : destino;
            vuelo <= 4'd0; ocup <= 3'd0;
            cola_esc <= 2'd0; cola_lec <= 2'd0; cola_n <= 3'd0;
            cab_v <= 1'b0; cab_vieja <= 1'b0;
        end else begin
            vuelo <= {vuelo[2:0], pedir};
            if (pedir) pc_mc <= pc_mc + 1'b1;
            ocup <= ocup + {2'd0, pedir} - {2'd0, tomar};
            if (llega) begin cola[cola_esc] <= ins_leida; cola_esc <= cola_esc + 1'b1; end
            cola_n <= cola_n + {2'd0, llega} - {2'd0, cargar_cab};
            cab_vieja <= cab_v && !tomar;
            if (cargar_cab) begin
                cabeza <= cola[cola_lec]; cola_lec <= cola_lec + 1'b1;
                cab_lee_acc <= lee_acc_f(cola[cola_lec][53:48]);
                cab_lee_reg <= lee_reg_f(cola[cola_lec][53:48]);
                cab_v <= 1'b1;
            end else if (tomar) cab_v <= 1'b0;
        end
    end
    bsram_pipe #(.PALABRAS(2048), .ANCHO(54)) u_microcodigo (
        .clk(clk), .we(prog_we), .dir_w(prog_dir), .dato_w(prog_dato),
        .dir_r(pc_mc[10:0]), .dato_r(ins_bsram)
    );
    always @(posedge clk) ins_leida <= ins_bsram;

    // Banco de registros en dos niveles (fails.md, F-15): en cada ciclo se
    // registran los 8 candidatos con los 3 bit bajos del índice de la cabeza; la
    // decodificación elige uno con los 3 altos. Valen si la cabeza lleva un ciclo
    // (cab_vieja) y ningún WRAX ha escrito el banco en los dos últimos (reg_edad).
    reg signed [23:0] candidato [0:7];
    integer g;
    always @(posedge clk)
        for (g = 0; g < 8; g = g + 1) candidato[g] <= regs[{3'(g), cabeza[44:42]}];

    // ── a24 = ACC redondeado y saturado a dato, registrado ────────────────
    // Una instrucción que lee el ACC se decodifica con el retiro vacío
    // (pendientes = 0), un ciclo después de la última escritura del ACC; en
    // E_EJEC, a24 ya está al día.
    wire signed [23:0] a24_c;
    acc_a_dato u_a24 (.acc(acc), .dato(a24_c));
    reg  signed [23:0] a24;
    always @(posedge clk) a24 <= a24_c;

    // ── Multiplicador (LAT ciclos) ────────────────────────────────────────
    reg  signed [26:0] ma;
    reg  signed [35:0] mb;
    wire signed [62:0] p_mult;
    reg  signed [62:0] p;          // 3 ciclos del DSP y este registro: LAT = 5
    mult_27x36 u_mult (.clk(clk), .a(ma), .b(mb), .p(p_mult));
    always @(posedge clk) p <= p_mult;
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
    // Región absoluta (ADR 0009): RDAA lee y WRAA escribe en palabras + índice.
    // El índice sale del registro R (15 bit de entero) y del campo addr, y se
    // enmascara a 15 bit. borrar_abs la borra al salir del reset.
    // mabs_borrar acompaña a mdir_w: los dos se registran en el mismo flanco.
    // Con borrar_abs directo, el modo iba un ciclo por delante de la dirección y
    // quedaban sin borrar la última palabra circular y la última absoluta.
    reg                borrar_abs, mabs_borrar;
    // Predecodificación (Fase 07): la decodificación registra la clase de la instrucción y
    // unas banderas. Con 18 instrucciones, decidir en E_EJEC desde el op de 6 bit
    // alargaba el camino de control (de 155 a 121 MHz según nextpnr).
    localparam [2:0] C_SIMPLE = 3'd0, C_RDA = 3'd1, C_CLIP = 3'd2, C_CHO = 3'd3,
                     C_SKP = 3'd4, C_RDAA = 3'd5, C_OTRA = 3'd6;
    reg [2:0] clase;
    reg es_rdfx, es_rdax_maxx, es_mulx, es_wra_wrap, es_wrax, es_wraa, es_rdaa;
    wire [5:0] op_leido = cabeza[53:48];
    // Dependencias de la cabeza: lee el ACC o a24, o lee el banco de registros.
    // MAXX y ABSA leen |ACC| en la primera etapa del retiro.
    // Se calculan al cargar la cabeza y van registradas (cab_lee_*): decidir la
    // decodificación desde el op de la cabeza fallaba en el silicio a 125 MHz.
    function automatic lee_acc_f(input [5:0] o);
        lee_acc_f = (o == WRA) || (o == WRAP) || (o == WRAX) || (o == RDFX) ||
                    (o == MULX) || (o == SOF) || (o == CLIP) || (o == SKP) ||
                    (o == WRAA) || (o == MAXX) || (o == 6'd15);   // ABSA
    endfunction
    function automatic lee_reg_f(input [5:0] o);
        lee_reg_f = (o == RDAX) || (o == MAXX) || (o == RDFX) || (o == MULX) ||
                    (o == 6'd13) ||   // LDAX
                    (o == RDAA) || (o == WRAA) || (o == CHO);
    endfunction
    wire               mabs_r = es_rdaa;
    wire               mabs_w = es_wraa | mabs_borrar;
    wire        [14:0] idx_abs = ad[14:0] + r_d[22:8];
    memoria_retardo #(.PALABRAS_MAX(PALABRAS_MAX), .GRUPO(GRUPO_MEM)) u_mem (
        .clk(clk), .rst(rst), .palabras(cfg_palabras), .avanzar(mavanzar),
        .dir_r(mdir_r), .abs_r(mabs_r), .dato_r(mdato_r),
        .we(mwe), .dir_w(mdir_w), .abs_w(mabs_w), .dato_w(mdato_w)
    );
    reg  signed [23:0] m0_abs;    // RDAA: M[i]; la fracción va en frac_abs
    reg         [7:0]  frac_abs;
    // M[i+1] − M[i], registrada: el multiplicador no lleva aritmética delante (F-11).
    reg  signed [24:0] dif_abs;
    always @(posedge clk) dif_abs <= {mdato_r[23], mdato_r} - {m0_abs[23], m0_abs};
    reg  signed [23:0] v_abs;     // RDAA: valor interpolado

    // ── LFO ───────────────────────────────────────────────────────────────
    reg                lfo_avanzar;
    wire               lfo_listo;
    wire [23:0]        lfo_fase;
    wire signed [23:0] lfo_tri, lfo_ven, lfo_actual;
    lfo_banco u_lfo (
        .clk(clk), .rst(rst), .tipos(cfg_lfo_tipos), .avanzar(lfo_avanzar),
        .rates({regs[LFO_BASE + 6], regs[LFO_BASE + 4], regs[LFO_BASE + 2], regs[LFO_BASE]}),
        .listo(lfo_listo), .sel(cabeza[43:42]), .media(cabeza[37]),
        .fase_sel(lfo_fase), .tri_sel(lfo_tri), .ven_sel(lfo_ven), .actual_sel(lfo_actual)
    );
    wire [1:0]         sel_leida = cabeza[43:42];

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
    // ── Retiro (ADR 0014) ─────────────────────────────────────────────────
    // La instrucción que presenta su último producto en t pone `empujar`; en
    // t+1 la línea toma su código, el único operando que la ALU necesita (LR en
    // WRAP, D en SOF, R en las demás) y el pc de la siguiente (para la traza). Ninguno cambia en t+1: la
    // siguiente decodificación los cambia al final de ese ciclo. Llegan al final
    // de la línea (LAT-1 etapas) en t+LAT, junto al producto: la ALU registra la
    // primera etapa y en t+LAT+1 escribe el ACC.
    // LDAX, CLR y ABSA también pasan por la línea, sin producto: el orden de
    // las escrituras del ACC es siempre el del programa.
    reg               empujar;
    localparam integer ETAPAS = 32'(LAT) - 1;
    reg  [ETAPAS-1:0] ret_v;
    reg  [5:0]        ret_op   [0:ETAPAS-1];
    reg  signed [23:0] ret_x   [0:ETAPAS-1];
    reg  [11:0]       ret_pc   [0:ETAPAS-1];
    wire signed [23:0] operando = (op == WRAP) ? lr : (op == SOF) ? {6'd0, ad} : r_d;
    reg               ret2_v;
    reg  [11:0]       ret2_pc, acc_pc;
    reg  [2:0]        pendientes;   // empujadas y aún sin escribir en el ACC
    integer j;
    always @(posedge clk) begin
        ret_v <= rst ? {ETAPAS{1'b0}} : {ret_v[ETAPAS-2:0], empujar};
        ret_op[0] <= op; ret_x[0] <= operando; ret_pc[0] <= pc;
        for (j = 1; j < ETAPAS; j = j + 1) begin
            ret_op[j] <= ret_op[j-1]; ret_x[j] <= ret_x[j-1]; ret_pc[j] <= ret_pc[j-1];
        end
        ret2_v  <= ret_v[ETAPAS-1] & ~rst;
        ret2_pc <= ret_pc[ETAPAS-1];
    end
    wire signed [47:0] acc_alu;
    // Dos etapas: la primera elige los operandos (lee el ACC); la segunda suma y
    // satura y su salida va directa al ACC. Entre dos empujes hay al menos 2
    // ciclos, así que la etapa 1 de un retiro ve el ACC del anterior.
    alu #(.REGISTRADA(1)) u_alu (
        .clk(clk), .op(ret_op[ETAPAS-1]), .acc(acc), .p(p), .lr(ret_x[ETAPAS-1]),
        .r(ret_x[ETAPAS-1]), .addr(ret_x[ETAPAS-1][17:0]), .acc_sig(acc_alu)
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

    // `tick` se registra a la entrada (Fase 07): llegaba combinacional desde el
    // generador de muestra y el cargador del top, y su lógica se sumaba a la de
    // arranque del núcleo en el camino crítico. Un ciclo más de latencia, sin
    // cambio en los bits ni en los ciclos que cuenta `ciclos`.
    // Las entradas se capturan en el flanco del `tick` original: el top puede
    // cambiarlas en el ciclo siguiente (el estímulo del HIL lo hace).
    reg tick_r;
    reg signed [23:0] adc_l_t, adc_r_t, sw_t;
    reg        [143:0] pots_t;
    always @(posedge clk) begin
        tick_r <= tick & ~rst;
        if (tick) begin adc_l_t <= adc_l; adc_r_t <= adc_r; pots_t <= pots; sw_t <= sw; end
    end

    // Escritura del banco en dos etapas (Fase 07, fails.md F-19): E_EJEC registra
    // una máscara de 64 bit y el dato; en el ciclo siguiente cada registro se
    // escribe con su bit de la máscara. Los 1 536 biestables del banco ocupan
    // todo el chip, y la decodificación de `rg` en el mismo ciclo fallaba en el
    // silicio a 114 MHz. La siguiente lectura llega varios ciclos después.
    reg        [63:0] esc_mascara;
    reg signed [23:0] esc_dato;

    // ── Decodificación ────────────────────────────────────────────────────
    // La cabeza se decodifica si no espera a nada: con `lee_acc`, a que el
    // retiro se vacíe (y a que no haya un empuje en este ciclo); con `lee_reg`,
    // a candidatos al día. El programa acaba igual: retiro vacío y banco escrito.
    reg  [1:0] reg_edad;   // ciclos desde la última escritura del banco por WRAX
    wire       retiro_vacio = (pendientes == 3'd0) && !empujar;
    // fin_prog va registrado: llega un ciclo tarde, pero E_LEER no lo mira hasta
    // un ciclo después de cambiar pc (la ejecución dura al menos un ciclo).
    reg        fin_prog;
    always @(posedge clk) fin_prog <= (pc == cfg_instrucciones);
    wire       sin_dep  = (!cab_lee_acc || retiro_vacio) &&
                          (!cab_lee_reg || (cab_vieja && reg_edad == 2'd2));
    assign tomar = (estado == E_LEER) && !vaciar && !fin_prog && cab_v && sin_dep;

    integer i;
    always @(posedge clk) begin
        fin         <= 1'b0;
        empujar     <= 1'b0;
        vaciar      <= 1'b0;
        mwe         <= 1'b0;
        mavanzar    <= 1'b0;
        lfo_avanzar <= 1'b0;
        esc_mascara <= 64'd0;
        mabs_borrar <= 1'b0;
        if (rst) begin
            estado <= E_BORRAR; borrar <= 16'd0; borrar_abs <= 1'b0;
            clase <= C_OTRA; es_rdfx <= 1'b0; es_rdax_maxx <= 1'b0; es_mulx <= 1'b0;
            es_wra_wrap <= 1'b0; es_wrax <= 1'b0; es_wraa <= 1'b0; es_rdaa <= 1'b0;
            pendientes <= 3'd0; reg_edad <= 2'd2; acc_pc <= 12'd0; destino <= 12'd0;
            pc <= 12'd0; paso <= 5'd0; espera <= 4'd0;
            primera <= 1'b1; acc <= 48'sd0; lr <= 24'sd0; ins <= 54'd0;
            dac_l <= 24'sd0; dac_r <= 24'sd0; ciclos <= 16'd0; cuenta <= 16'd0;
            for (i = 0; i < 64; i = i + 1) regs[i] <= 24'sd0;
        end else begin
            for (i = 0; i < 64; i = i + 1) if (esc_mascara[i]) regs[i] <= esc_dato;
            if (estado != E_PARADO && estado != E_BORRAR) cuenta <= cuenta + 1'b1;
            pendientes <= pendientes + {2'd0, empujar} - {2'd0, ret2_v};
            if (ret2_v) begin acc <= acc_alu; acc_pc <= ret2_pc; end
            if (reg_edad != 2'd2) reg_edad <= reg_edad + 1'b1;
            case (estado)
            E_BORRAR: begin   // primero la memoria circular; después, la región absoluta
                mwe <= 1'b1; mdir_w <= {1'b0, borrar}; mdato_w <= 24'sd0; mabs_borrar <= borrar_abs;
                if (!borrar_abs && borrar == cfg_palabras - 1'b1) begin
                    if (cfg_absoluta) begin borrar_abs <= 1'b1; borrar <= 16'd0; end
                    else estado <= E_PARADO;
                end else if (borrar_abs && borrar == 16'd32767) begin
                    borrar_abs <= 1'b0; estado <= E_PARADO;
                end else borrar <= borrar + 1'b1;
            end
            E_PARADO: if (tick_r) begin
                regs[ADCL] <= adc_l_t;
                regs[ADCR] <= adc_r_t;
                for (i = 0; i < 6; i = i + 1) regs[POT_BASE + i] <= pots_t[24*i +: 24];
                regs[SW] <= sw_t;
                lfo_avanzar <= 1'b1;
                acc <= 48'sd0; acc_pc <= 12'd0; lr <= 24'sd0; pc <= 12'd0; cuenta <= 16'd1;
                vaciar <= 1'b1; destino <= 12'd0;   // la cola se llena durante E_LFO
                estado <= E_LFO;
            end
            E_LFO: if (lfo_listo) estado <= E_LEER;
            E_LEER: if (fin_prog) begin
                if (retiro_vacio && reg_edad == 2'd2) estado <= E_FIN;
            end else if (tomar) begin
                ins <= cabeza;
                case (op_leido)
                    RDAX, MAXX, WRA, WRAX, WRAP, RDFX, MULX, SOF, WRAA: clase <= C_SIMPLE;
                    RDA:     clase <= C_RDA;
                    CLIP:    clase <= C_CLIP;
                    CHO:     clase <= C_CHO;
                    SKP:     clase <= C_SKP;
                    RDAA:    clase <= C_RDAA;
                    default: clase <= C_OTRA;   // NOP, LDAX, CLR, ABSA
                endcase
                es_rdfx      <= (op_leido == RDFX);
                es_rdax_maxx <= (op_leido == RDAX) || (op_leido == MAXX);
                es_mulx      <= (op_leido == MULX);
                es_wra_wrap  <= (op_leido == WRA) || (op_leido == WRAP);
                es_wrax      <= (op_leido == WRAX);
                es_wraa      <= (op_leido == WRAA);
                es_rdaa      <= (op_leido == RDAA);
                pc <= pc + 1'b1;   // pc: la siguiente a decodificar
                r_d      <= candidato[cabeza[47:45]];
                dep_d    <= regs[6'd43 + {3'd0, sel_leida, 1'b0}];   // lfoN_depth = 42 + 2N + 1
                fase_d   <= lfo_fase;
                tri_d    <= lfo_tri;
                ven_d    <= lfo_ven;
                actual_d <= lfo_actual;
                tipo_d   <= cfg_lfo_tipos[2*sel_leida +: 2];
                exc_d    <= cfg_lfo_excursiones[15*sel_leida +: 15];
                paso <= 5'd0; espera <= 4'd0;
                estado <= E_EJEC;
            end
            E_EJEC: if (espera != 4'd0) begin
                espera <= espera - 1'b1;
            end else begin
                // Por defecto, la instrucción termina en este ciclo.
                case (clase)
                C_SIMPLE:   // RDAX, MAXX, WRA, WRAX, WRAP, RDFX, MULX, SOF, WRAA
                    if (paso == 5'd0 && es_rdfx) begin
                        paso <= 5'd2;   // dif = a24 − R se registra en este ciclo
                    end else if (paso == 5'd0 || paso == 5'd2) begin
                        if (es_rdfx)           ma <= a27(dif);
                        else if (es_rdax_maxx) ma <= a27({r_d[23], r_d});
                        else                   ma <= a27({a24[23], a24});
                        mb <= es_mulx ? b36({r_d[23], r_d}) : b36({{7{cf[17]}}, cf});
                        if (es_wra_wrap) begin
                            mwe <= 1'b1; mdir_w <= {1'b0, ad[15:0]}; mdato_w <= a24;
                        end
                        if (es_wraa) begin
                            mwe <= 1'b1; mdir_w <= {2'b00, idx_abs}; mdato_w <= a24;
                        end
                        if (es_wrax) begin
                            esc_mascara <= 64'd1 << rg; esc_dato <= a24; reg_edad <= 2'd0;
                        end
                        empujar <= 1'b1; estado <= E_LEER;
                    end
                C_RDA:
                    case (paso)
                    5'd0: begin mdir_r <= {1'b0, ad[15:0]}; paso <= 5'd1; espera <= LAT_MEM - 1'b1; end
                    5'd1: begin
                        lr <= mdato_r;
                        ma <= a27({mdato_r[23], mdato_r}); mb <= b36({{7{cf[17]}}, cf});
                        empujar <= 1'b1; estado <= E_LEER;
                    end
                    default: estado <= E_LEER;
                    endcase
                C_CLIP:
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
                        acc <= {{8{y_clip[23]}}, y_clip, 16'd0}; acc_pc <= pc;
                        estado <= E_LEER;
                    end
                    endcase
                C_CHO:
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
                    // La primera lectura llega LAT_MEM ciclos después.
                    5'd24: begin paso <= 5'd9; espera <= EXTRA_MEM; end
                    // Llegan M[base−1], M[base], M[base+1] y M[base+2] (LAT_MEM ciclos
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
                            empujar <= 1'b1; estado <= E_LEER;
                        end
                    end
                    5'd18: begin   // v = (v · ventana) >> 23
                        lr <= p50[46:23];
                        ma <= a27(p_23); mb <= b36({{7{cf[17]}}, cf});
                        empujar <= 1'b1; estado <= E_LEER;
                    end
                    default: estado <= E_LEER;
                    endcase
                C_RDAA:
                    case (paso)
                    // Lecturas de M[i] y M[i+1] en dos ciclos seguidos.
                    5'd0:  begin mdir_r <= {2'b00, idx_abs}; frac_abs <= r_d[7:0]; paso <= 5'd26; end
                    5'd26: begin mdir_r <= mdir_r + 17'sd1; paso <= 5'd27; espera <= LAT_MEM - 4'd3; end
                    5'd27: paso <= 5'd28;   // M[i] llega LAT_MEM ciclos después de pedirla
                    5'd28: begin m0_abs <= mdato_r; paso <= 5'd29; end
                    5'd29: paso <= 5'd15;   // dif_abs = M[i+1] − M[i] se registra
                    5'd15: begin   // (M[i+1] − M[i])·f; la fracción, sin signo
                        ma <= a27(dif_abs);
                        mb <= b36({17'd0, frac_abs});
                        paso <= 5'd30; espera <= LAT - 1'b1;
                    end
                    5'd30: begin v_abs <= m0_abs + 24'(p50 >>> 8); paso <= 5'd31; end
                    5'd31: begin   // LR = v; ACC += v·C
                        lr <= v_abs;
                        ma <= a27({v_abs[23], v_abs}); mb <= b36({{7{cf[17]}}, cf});
                        empujar <= 1'b1; estado <= E_LEER;
                    end
                    default: estado <= E_LEER;
                    endcase
                C_SKP: begin   // pc ya apunta a la siguiente
                    if (saltar) begin
                        pc <= pc + ad[11:0];
                        vaciar <= 1'b1; destino <= pc + ad[11:0];
                    end
                    estado <= E_LEER;
                end
                default: begin   // NOP, LDAX, CLR, ABSA: sin producto
                    empujar <= (op != 6'd0);
                    estado <= E_LEER;
                end
                endcase
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
