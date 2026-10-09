// SPDX-License-Identifier: MIT
//
// Cargador de programas desde el banco de la microSD (Fase 08). Lee la ranura
// pedida con sd_spi.v y la escribe en el núcleo solo si es válida. El formato
// es el de model/sofifi/domain/banco.py.
//
// Con un pulso en `cargar` y la ranura en `ranura`:
//   1. Bloque 0: magia "SOFIFI", versión 1, número de programas en [1, 1024],
//      CRC-32 de la cabecera y ranura < número de programas.
//   2. Primera pasada, sin escribir nada: metadatos de la ranura (magia,
//      instrucciones en [1, 2048], memoria en [1, 43 008], LFOs) y microcódigo.
//      Comprueba el CRC-32 de los dos, que cada código de operación existe y que
//      ningún SKP salta fuera del programa. El núcleo sigue con el programa
//      anterior.
//   3. Segunda pasada: para el núcleo (`nucleo_rst`), vuelve a leer el
//      microcódigo, lo escribe por el puerto de programa y comprueba otra vez el
//      CRC. Si cuadra, pone la configuración nueva y suelta el núcleo, que borra
//      su memoria y arranca. `hecho` da un pulso.
//
// Si la cabecera o la primera pasada fallan, `fallo` da un pulso con su motivo en
// `motivo` y el núcleo no se toca. Si falla la segunda pasada (la tarjeta cambió
// entre las dos lecturas), el núcleo queda parado: mejor silencio que un
// programa a medias.
//
// El cargador no hace las comprobaciones semánticas de Programa (alcance de CHO,
// registros de solo lectura): las hace `sofifi banco` al escribir. Un programa
// raro con CRC correcto solo puede dar audio raro: toda dirección del núcleo
// cae dentro de su memoria de retardo.
//
// CRC-32 de zlib, bit a bit (8 ciclos por byte): los bytes llegan como mucho
// cada 64 ciclos.
`default_nettype none

module cargador (
    input  wire        clk,
    input  wire        rst,
    input  wire        cargar,
    input  wire [9:0]  ranura,
    output reg         ocupado,
    output reg         hecho,
    output reg         fallo,
    output reg  [3:0]  motivo,
    // sd_spi
    output reg         sd_leer,
    output reg  [31:0] sd_bloque,
    input  wire        sd_ocupado,
    input  wire        sd_error,
    input  wire [7:0]  sd_dato,
    input  wire        sd_dato_v,
    input  wire        sd_fin,
    // Núcleo
    output reg         nucleo_rst,
    output reg         prog_we,
    output reg  [10:0] prog_dir,
    output reg  [53:0] prog_dato,
    output reg  [11:0] cfg_instrucciones,
    output reg  [15:0] cfg_palabras,
    output reg  [7:0]  cfg_lfo_tipos,
    output reg  [59:0] cfg_lfo_excursiones,
    output reg         cfg_absoluta
);
    // Motivos de fallo.
    localparam [3:0] M_SD = 4'd1, M_CABECERA = 4'd2, M_CRC_CABECERA = 4'd3, M_RANURA = 4'd4,
                     M_METADATOS = 4'd5, M_LFO = 4'd6, M_CODIGO = 4'd7, M_CRC = 4'd8,
                     M_CRC_ESCRITURA = 4'd9;
    localparam [31:0] POLI = 32'hEDB88320;
    localparam [5:0] OP_SKP = 6'd11, OP_RDAA = 6'd16, OP_WRAA = 6'd17, OP_MAX = 6'd17;

    // ── CRC-32 bit a bit ──────────────────────────────────────────────────
    reg        crc_iniciar, crc_meter;
    reg [31:0] crc;
    reg [7:0]  crc_byte;
    reg [3:0]  crc_bits;      // bits que faltan del byte en curso
    always @(posedge clk) begin
        if (rst || crc_iniciar) begin
            crc <= 32'hFFFFFFFF; crc_bits <= 4'd0;
        end else if (crc_meter) begin
            crc_byte <= sd_dato; crc_bits <= 4'd8;
        end else if (crc_bits != 4'd0) begin
            crc <= (crc >> 1) ^ (((crc[0] ^ crc_byte[0]) != 1'b0) ? POLI : 32'd0);
            crc_byte <= crc_byte >> 1;
            crc_bits <= crc_bits - 1'b1;
        end
    end
    wire [31:0] crc_final = ~crc;

    // ── Estado ────────────────────────────────────────────────────────────
    localparam [3:0] C_LIBRE = 4'd0, C_PEDIR = 4'd1, C_ESPERA = 4'd2, C_BLOQUE = 4'd3,
                     C_CABECERA = 4'd4, C_METADATOS = 4'd5, C_SIGUIENTE = 4'd6,
                     C_COMPROBAR = 4'd7, C_SOLTAR = 4'd8;
    reg [3:0]  c;
    reg [1:0]  fase;          // 0: cabecera; 1: primera pasada; 2: segunda pasada
    reg [3:0]  siguiente;     // estado tras leer el bloque
    reg [9:0]  k;             // ranura pedida
    reg [9:0]  i_byte;        // byte dentro del bloque
    reg [4:0]  i_micro;       // bloque de microcódigo (0..26)
    reg [13:0] bytes_micro;   // bytes de microcódigo por leer
    reg [13:0] metidos;       // bytes de microcódigo ya contados
    (* ram_style = "logic" *)   // F-24: un array por índice acaba en BSRAM
    reg [7:0]  b [0:59];      // primeros bytes del bloque (cabecera o metadatos)
    reg [31:0] crc_esperado;
    // Microcódigo: palabras de 54 bit desempaquetadas de los bytes.
    reg [61:0] acum;
    reg [6:0]  n_acum;        // bits válidos en acum
    reg [11:0] n_palabras;    // palabras ya sacadas
    reg [11:0] n_instr;
    reg        absoluta;
    reg        malo;          // código de operación o salto no válidos

    wire [15:0] numero   = {b[9], b[10]};
    wire [15:0] instr    = {b[40], b[41]};
    wire [15:0] palabras = {b[42], b[43]};
    // Desempaquetado en tres etapas registradas (timing a 100 MHz): 1) copia de
    // acum y desplazamiento (0 a 7: acum no pasa de 61 bits); 2) la palabra;
    // 3) comprobaciones y escritura. Un byte nuevo tarda 64 ciclos o más.
    reg  [1:0]  etapa;        // 0: libre; 1: desplazar; 2: comprobar
    reg  [61:0] copia;
    reg  [2:0]  desp;
    reg  [53:0] palabra;
    wire [5:0]  op       = palabra[53:48];
    wire [17:0] salto    = palabra[17:0];
    // El byte en curso cuenta para el CRC: la cabecera hasta el byte 10, los
    // metadatos hasta el 55 y el microcódigo hasta bytes_micro.
    wire        mirar    = (fase == 2'd0) ? (i_byte < 10'd11) :
                           (siguiente == C_METADATOS) ? (i_byte < 10'd56) :
                           (metidos < bytes_micro);

    function automatic [1:0] tipo_lfo(input [7:0] tipo);   // sin LFO: 0, como sofifi tablas
        tipo_lfo = (tipo == 8'hFF) ? 2'd0 : tipo[1:0];
    endfunction
    function automatic lfo_ok(input [7:0] tipo, input [15:0] exc);
        lfo_ok = (tipo == 8'hFF) || (tipo <= 8'd2 && exc >= 16'd1 && exc <= 16'd16384);
    endfunction

    // Bytes de 0 a 59 de la cabecera (15) o de los metadatos (60) en b[].
    always @(posedge clk)
        if (c == C_BLOQUE && sd_dato_v && i_byte < 10'd60 && siguiente != C_SIGUIENTE)
            b[i_byte[5:0]] <= sd_dato;   // no en el microcódigo: los metadatos se usan al final

    always @(posedge clk) begin
        hecho <= 1'b0; fallo <= 1'b0; sd_leer <= 1'b0; prog_we <= 1'b0;
        crc_iniciar <= 1'b0; crc_meter <= 1'b0;
        if (rst) begin
            c <= C_LIBRE; ocupado <= 1'b0; nucleo_rst <= 1'b0; motivo <= 4'd0; etapa <= 2'd0;
            cfg_instrucciones <= 12'd1; cfg_palabras <= 16'd1; cfg_lfo_tipos <= 8'd0;
            cfg_lfo_excursiones <= 60'd0; cfg_absoluta <= 1'b0;
        end else begin
            case (c)
            C_LIBRE: if (cargar) begin
                k <= ranura; ocupado <= 1'b1; fase <= 2'd0;
                sd_bloque <= 32'd0; siguiente <= C_CABECERA;
                crc_iniciar <= 1'b1; c <= C_PEDIR;
            end
            C_PEDIR: if (sd_error) begin
                motivo <= M_SD; c <= C_SIGUIENTE;   // C_SIGUIENTE con motivo: fallo
            end else if (!sd_ocupado) begin
                sd_leer <= 1'b1; i_byte <= 10'd0; c <= C_ESPERA;
            end
            C_ESPERA: c <= C_BLOQUE;   // sd_spi pone `ocupado` un ciclo después
            C_BLOQUE: begin
                if (sd_error) begin motivo <= M_SD; c <= C_SIGUIENTE; end
                if (sd_dato_v) begin
                    i_byte <= i_byte + 1'b1;
                    if (mirar) crc_meter <= 1'b1;
                    // Microcódigo: los bytes llegan cada 64 ciclos o más, y la
                    // palabra sale antes del siguiente: acum no pasa de 61 bit.
                    if (siguiente == C_SIGUIENTE && mirar) begin
                        metidos <= metidos + 1'b1;
                        acum <= {acum[53:0], sd_dato};
                        n_acum <= n_acum + 7'd8;
                    end
                end
                // Saca una palabra en cuanto hay 54 bits.
                if (siguiente == C_SIGUIENTE && etapa == 2'd0 && n_acum >= 7'd54 &&
                    !(sd_dato_v && mirar)) begin
                    n_acum <= n_acum - 7'd54;
                    copia <= acum; desp <= 3'(n_acum - 7'd54); etapa <= 2'd1;
                end
                if (etapa == 2'd1) begin palabra <= 54'(copia >> desp); etapa <= 2'd2; end
                if (etapa == 2'd2) begin
                    etapa <= 2'd0;
                    if (n_palabras < n_instr) begin
                        n_palabras <= n_palabras + 1'b1;
                        if (op > OP_MAX) malo <= 1'b1;
                        if (op == OP_SKP &&
                            {7'd0, n_palabras} + 19'd1 + {1'b0, salto} > {7'd0, n_instr})
                            malo <= 1'b1;
                        if (op == OP_RDAA || op == OP_WRAA) absoluta <= 1'b1;
                        if (fase == 2'd2) begin
                            prog_we <= 1'b1; prog_dir <= n_palabras[10:0]; prog_dato <= palabra;
                        end
                    end
                end
                if (sd_fin) c <= siguiente;
            end
            C_CABECERA: begin
                if ({b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7]} != 64'h534F_4649_4649_0000 ||
                    b[8] != 8'd1 || numero == 16'd0 || numero > 16'd1024)
                    begin motivo <= M_CABECERA; c <= C_SIGUIENTE; end
                else if (crc_final != {b[11], b[12], b[13], b[14]})
                    begin motivo <= M_CRC_CABECERA; c <= C_SIGUIENTE; end
                else if ({6'd0, k} >= numero)
                    begin motivo <= M_RANURA; c <= C_SIGUIENTE; end
                else begin   // metadatos de la ranura: bloque 1 + 28·k
                    fase <= 2'd1; crc_iniciar <= 1'b1;
                    sd_bloque <= 32'd1 + 32'd28 * {22'd0, k};
                    siguiente <= C_METADATOS; c <= C_PEDIR;
                end
            end
            C_METADATOS: begin
                if ({b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7]} != "SOFIPROG" ||
                    instr == 16'd0 || instr > 16'd2048 ||
                    palabras == 16'd0 || palabras > 16'd43008)
                    begin motivo <= M_METADATOS; c <= C_SIGUIENTE; end
                else if (!lfo_ok(b[44], {b[45], b[46]}) || !lfo_ok(b[47], {b[48], b[49]}) ||
                         !lfo_ok(b[50], {b[51], b[52]}) || !lfo_ok(b[53], {b[54], b[55]}))
                    begin motivo <= M_LFO; c <= C_SIGUIENTE; end
                else begin
                    crc_esperado <= {b[56], b[57], b[58], b[59]};
                    n_instr <= instr[11:0];
                    // ⌈54·n / 8⌉ = ⌈27·n / 4⌉
                    bytes_micro <= 14'((18'd27 * {2'd0, instr} + 18'd3) >> 2);
                    i_micro <= 5'd0; metidos <= 14'd0;
                    acum <= 62'd0; n_acum <= 7'd0; n_palabras <= 12'd0; etapa <= 2'd0;
                    malo <= 1'b0; absoluta <= 1'b0;
                    sd_bloque <= sd_bloque + 32'd1;
                    siguiente <= C_SIGUIENTE; c <= C_PEDIR;
                end
            end
            C_SIGUIENTE: if (motivo != 4'd0) begin   // un fallo llega aquí con su motivo
                fallo <= 1'b1; ocupado <= 1'b0; c <= C_LIBRE;
                // Con el núcleo ya parado (segunda pasada), queda parado.
            end else if (crc_bits != 4'd0 || n_acum >= 7'd54 || etapa != 2'd0) begin
                // espera a que el CRC y el desempaquetado terminen
            end else if (metidos < bytes_micro) begin   // otro bloque de microcódigo
                i_micro <= i_micro + 1'b1;
                sd_bloque <= sd_bloque + 32'd1; c <= C_PEDIR;
            end else c <= C_COMPROBAR;
            C_COMPROBAR: begin
                if (crc_final != crc_esperado) begin
                    motivo <= (fase == 2'd2) ? M_CRC_ESCRITURA : M_CRC; c <= C_SIGUIENTE;
                end else if (malo || n_palabras != n_instr) begin
                    motivo <= M_CODIGO; c <= C_SIGUIENTE;
                end else if (fase == 2'd1) begin   // vale: segunda pasada, escribiendo
                    fase <= 2'd2; nucleo_rst <= 1'b1;
                    crc_iniciar <= 1'b1;
                    // El CRC cubre también los metadatos: se vuelven a leer.
                    sd_bloque <= 32'd1 + 32'd28 * {22'd0, k};
                    siguiente <= C_METADATOS; c <= C_PEDIR;
                end else c <= C_SOLTAR;
            end
            C_SOLTAR: begin
                cfg_instrucciones <= n_instr;
                cfg_palabras <= palabras;
                cfg_lfo_tipos <= {tipo_lfo(b[53]), tipo_lfo(b[50]), tipo_lfo(b[47]), tipo_lfo(b[44])};
                cfg_lfo_excursiones <= {b[54][6:0], b[55], b[51][6:0], b[52],
                                        b[48][6:0], b[49], b[45][6:0], b[46]};
                cfg_absoluta <= absoluta;
                nucleo_rst <= 1'b0; hecho <= 1'b1; ocupado <= 1'b0; motivo <= 4'd0;
                c <= C_LIBRE;
            end
            default: c <= C_LIBRE;
            endcase
            if (c == C_LIBRE && cargar) motivo <= 4'd0;
        end
    end
endmodule

`default_nettype wire
