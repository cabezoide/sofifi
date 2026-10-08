// SPDX-License-Identifier: MIT
//
// Verificación del núcleo en la placa (Fase 05, hardware-in-the-loop). Al recibir
// el byte 'C' por la UART:
//
//   1. reinicia el núcleo, que borra su memoria de retardo (empieza como el modelo);
//   2. procesa N_CAPTURA muestras a velocidad real (48 828 Hz) con el plate y un
//      estímulo fijo, y guarda dac_l y dac_r en BSRAM;
//   3. vuelca cada muestra como "M 00<dac_l><dac_r>\r\n" (14 dígitos), después
//      "K <ciclos>\r\n" (máximo de ciclos por muestra) y "Z <crc>\r\n".
//
// Con 'T' y dos bytes más (K0, big-endian) graba la traza del núcleo en vez de
// las muestras: {pc[6:0], ACC[47:1]} cada vez que cambia el ACC, desde la
// muestra K0 y hasta llenar la captura. Localiza en el silicio la primera
// instrucción que falla (fails.md, F-15). "K" lleva entonces, además, las
// entradas grabadas: {entradas, ciclos}.
//
// El CRC es el CRC-32 de zlib sobre los bytes de las muestras (dac_l y dac_r en
// big-endian, 3 bytes cada uno). scripts/hil_nucleo.py lo comprueba y compara
// cada muestra con el modelo.
//
// Solo vuelca cuando el PC lo pide: a pleno caudal, el puente UART del BL616 se
// cuelga si el PC no lee (Fase 03).
//
// Estímulo (scripts/hil_nucleo.py lo reproduce), con N = N_CAPTURA: muestra 0,
// impulso (0,5; -0,25); hasta N/4, silencio; desde N/4, un triángulo de 64
// muestras de periodo y ±0,25 de amplitud, invertido en el canal derecho. El
// footswitch está pulsado en [N/4, N/2) y en [3N/4, 3N/4 + N/16): el looper
// graba y después hace overdub (Fase 07). El plate no lee `sw`. Con N = 4 096:
// triángulo desde la 1 024; footswitch de 1 024 a 2 047 y de 3 072 a 3 327.
//
// PROGRAMA elige la ROM: "plate" (por defecto), "looper" (top hil_looper) o
// "hil" (top hil_programa). Las dos primeras están en programa_<nombre>.v,
// generadas por `sofifi tablas`. La ROM programa_hil la escribe `sofifi rom` en
// build/ con cualquier programa o cadena que quepa en PALABRAS_MAX (`make hil`).
`default_nettype none

module hil_nucleo #(
    parameter integer F_RELOJ      = 100_000_000,
    parameter integer BAUDIOS      = 115_200,
    parameter integer N_CAPTURA    = 4096,     // potencia de 2
    parameter integer PALABRAS_MAX = 38_912,   // 38 bloques: deja BSRAM para la captura
    parameter [47:0]  PROGRAMA     = "plate"     // 6 caracteres como máximo
) (
    input  wire clk,      // 50 MHz (E2)
    input  wire rst_n,
    input  wire uart_rx,
    output wire uart_tx
);
    localparam integer AK = $clog2(N_CAPTURA);
    localparam integer DIVISOR = F_RELOJ / BAUDIOS;

    wire clk_100, bloqueado;
    pll_100 u_pll (.clk_50(clk), .clk_100(clk_100), .bloqueado(bloqueado));

    (* ASYNC_REG = "TRUE" *) reg [2:0] rst_s;
    /* verilator lint_off PROCASSINIT */
    reg [3:0] arranque = 4'd0;
    /* verilator lint_on PROCASSINIT */
    always @(posedge clk_100) begin
        rst_s <= {rst_s[1:0], ~(bloqueado & rst_n)};
        if (!arranque[3]) arranque <= arranque + 1'b1;
    end
    wire rst = rst_s[2] | ~arranque[3];

    // ── Programa ──────────────────────────────────────────────────────────
    wire [53:0] palabra;
    wire [11:0] instrucciones;
    wire [15:0] palabras;
    wire [7:0]  lfo_tipos;
    wire [59:0] lfo_excursiones;
    wire        absoluta;
    wire [10:0] dir, prog_dir;
    wire [53:0] prog_dato;
    wire        prog_we, cargado;
    generate if (PROGRAMA == "looper") begin : g_looper
        programa_looper u_prog (
            .dir(dir), .palabra(palabra), .instrucciones(instrucciones),
            .palabras(palabras), .lfo_tipos(lfo_tipos), .lfo_excursiones(lfo_excursiones),
            .absoluta(absoluta)
        );
    end else if (PROGRAMA == "hil") begin : g_hil
        programa_hil u_prog (
            .dir(dir), .palabra(palabra), .instrucciones(instrucciones),
            .palabras(palabras), .lfo_tipos(lfo_tipos), .lfo_excursiones(lfo_excursiones),
            .absoluta(absoluta)
        );
    end else begin : g_plate
        programa_plate u_prog (
            .dir(dir), .palabra(palabra), .instrucciones(instrucciones),
            .palabras(palabras), .lfo_tipos(lfo_tipos), .lfo_excursiones(lfo_excursiones),
            .absoluta(absoluta)
        );
    end endgenerate
    carga_programa u_carga (
        .clk(clk_100), .rst(rst), .instrucciones(instrucciones),
        .dir(dir), .palabra(palabra), .prog_we(prog_we), .prog_dir(prog_dir),
        .prog_dato(prog_dato), .cargado(cargado)
    );

    // ── Estado ────────────────────────────────────────────────────────────
    localparam [3:0] H_ESPERA = 4'd0, H_RESET = 4'd1, H_BORRA = 4'd2, H_CAPTURA = 4'd3,
                     H_LEER = 4'd4, H_ENVIAR = 4'd5, H_CICLOS = 4'd6, H_CRC = 4'd7,
                     H_K0_ALTO = 4'd8, H_K0_BAJO = 4'd9;
    reg [3:0]    estado;
    reg          traza;      // 1: graba la traza del núcleo en vez de las muestras
    reg [15:0]   k0;
    reg [AK-1:0] k;
    reg [2:0]    espera;

    // ── Estímulo de la muestra k ──────────────────────────────────────────
    wire [5:0]         t   = k[5:0];
    wire signed [6:0]  triang = (t < 6'd32) ? $signed({1'b0, t}) - 7'sd16
                                            : 7'sd48 - $signed({1'b0, t});
    wire signed [23:0] tono = {triang, 17'd0};   // triang · 2^17, en [-2^21, 2^21]
    wire [31:0]        k32  = {{(32-AK){1'b0}}, k};   // vale para cualquier N_CAPTURA
    localparam [31:0]  N4  = N_CAPTURA / 4;
    localparam [31:0]  N16 = N_CAPTURA / 16;
    wire signed [23:0] adc_l = (k32 == 32'd0) ? 24'sh400000 :
                               (k32 < N4)     ? 24'sd0 : tono;
    wire signed [23:0] adc_r = (k32 == 32'd0) ? 24'shE00000 :
                               (k32 < N4)     ? 24'sd0 : -tono;
    wire               pulsado = (k32 >= N4 && k32 < 2 * N4) ||
                                 (k32 >= 3 * N4 && k32 < 3 * N4 + N16);
    wire signed [23:0] sw = pulsado ? 24'sh7FFFFF : 24'sd0;

    // ── Núcleo ────────────────────────────────────────────────────────────
    wire               tick;
    wire signed [23:0] dac_l, dac_r;
    wire               fin, ocupado;
    wire [15:0]        ciclos;
    generador_muestra u_gen (.clk(clk_100), .activo(estado == H_CAPTURA), .tick(tick));
    nucleo #(.PALABRAS_MAX(PALABRAS_MAX)) u_nucleo (
        .clk(clk_100), .rst(rst | ~cargado | (estado == H_RESET)),
        .prog_we(prog_we), .prog_dir(prog_dir), .prog_dato(prog_dato),
        .cfg_instrucciones(instrucciones), .cfg_palabras(palabras),
        .cfg_lfo_tipos(lfo_tipos), .cfg_lfo_excursiones(lfo_excursiones),
        .cfg_absoluta(absoluta),
        .tick(tick), .adc_l(adc_l), .adc_r(adc_r),
        .pots({6{24'sh400000}}), .sw(sw),
        .dac_l(dac_l), .dac_r(dac_r), .fin(fin), .ocupado(ocupado), .ciclos(ciclos),
        .traza_pc(traza_pc), .traza_acc(traza_acc)
    );
    /* verilator lint_off UNUSEDSIGNAL */   // la traza guarda 7 bit de pc (≤ 128 instrucciones)
    wire [11:0]        traza_pc;
    /* verilator lint_on UNUSEDSIGNAL */
    wire signed [47:0] traza_acc;

    // ── Captura ───────────────────────────────────────────────────────────
    // La traza pasa por registros antes de escribir: la comparación de 48 bit
    // no alarga ningún camino (fails.md, F-15). acc_b y pc_b van dos ciclos
    // detrás del núcleo; `cambio` dice si acc_b es distinto del anterior.
    reg  signed [47:0] acc_a, acc_b;
    reg  [6:0]         pc_a, pc_b;
    reg                cambio;
    reg  [AK:0]        entradas;     // de la traza; entradas[AK] = captura llena
    reg                desde_k0;
    reg                cap_we;
    reg  [AK-1:0]      cap_dir;
    reg  [53:0]        cap_dato;
    wire               grabar_traza = traza && desde_k0 && cambio && !entradas[AK];
    always @(posedge clk_100) begin
        acc_a    <= traza_acc;
        pc_a     <= traza_pc[6:0];
        acc_b    <= acc_a;
        pc_b     <= pc_a;
        cambio   <= (acc_a != acc_b);
        desde_k0 <= (k32 >= {16'd0, k0});
        cap_we   <= (estado == H_CAPTURA) && (traza ? grabar_traza : fin);
        cap_dir  <= traza ? entradas[AK-1:0] : k;
        cap_dato <= traza ? {pc_b, acc_b[47:1]} : {6'd0, dac_l, dac_r};
        if (estado == H_BORRA) entradas <= {(AK+1){1'b0}};
        else if (estado == H_CAPTURA && grabar_traza) entradas <= entradas + 1'b1;
    end

    wire [53:0] capturada;
    // bsram_pipe: con bsram_dp (bypass), la lectura de la captura fallaba por
    // encima de 100 MHz y corrompía el volcado (fails.md, F-11). Lee en 3 ciclos.
    bsram_pipe #(.PALABRAS(N_CAPTURA), .ANCHO(54)) u_captura (
        .clk(clk_100), .we(cap_we), .dir_w(cap_dir), .dato_w(cap_dato),
        .dir_r(k), .dato_r(capturada)
    );

    // ── UART ──────────────────────────────────────────────────────────────
    wire [7:0] recibido;
    wire       recibido_ok;
    uart_rx #(.DIVISOR(DIVISOR)) u_rx (
        .clk(clk_100), .rst(rst), .rx(uart_rx), .dato(recibido), .valido(recibido_ok)
    );
    reg        inicio;
    reg [7:0]  etiqueta;
    reg [55:0] valor;
    wire       ocupado_tx;
    linea_hex #(.DIGITOS(14), .DIVISOR(DIVISOR)) u_linea (
        .clk(clk_100), .rst(rst), .inicio(inicio), .etiqueta(etiqueta),
        .valor(valor), .ocupado(ocupado_tx), .tx(uart_tx)
    );

    // ── CRC-32 de zlib, bit a bit (LSB primero en cada byte) ─────────────
    reg [31:0] crc;
    reg [5:0]  bit_crc;      // 0..47; 48 = muestra terminada
    reg [53:0] muestra;
    wire [2:0] byte_crc = 3'(bit_crc >> 3);
    wire       dato_bit = muestra[6'd40 - {byte_crc, 3'b000} + {3'b000, bit_crc[2:0]}];
    wire       realim   = crc[0] ^ dato_bit;

    reg [15:0] ciclos_max;

    always @(posedge clk_100) begin
        inicio <= 1'b0;
        if (rst || !cargado) begin
            estado <= H_ESPERA; k <= {AK{1'b0}}; espera <= 3'd0; traza <= 1'b0;
        end else begin
            case (estado)
            H_ESPERA: if (recibido_ok && recibido == "C") begin
                traza <= 1'b0; estado <= H_RESET; espera <= 3'd3;
            end else if (recibido_ok && recibido == "T") begin
                traza <= 1'b1; estado <= H_K0_ALTO;
            end
            H_K0_ALTO: if (recibido_ok) begin k0[15:8] <= recibido; estado <= H_K0_BAJO; end
            H_K0_BAJO: if (recibido_ok) begin
                k0[7:0] <= recibido; estado <= H_RESET; espera <= 3'd3;
            end
            H_RESET: if (espera != 3'd0) espera <= espera - 1'b1; else estado <= H_BORRA;
            H_BORRA: if (!ocupado) begin
                k <= {AK{1'b0}}; ciclos_max <= 16'd0; estado <= H_CAPTURA;
            end
            H_CAPTURA: if (fin) begin
                if (ciclos > ciclos_max) ciclos_max <= ciclos;
                if (k == {AK{1'b1}}) begin
                    k <= {AK{1'b0}}; crc <= 32'hFFFFFFFF; estado <= H_LEER; espera <= 3'd3;
                end else begin
                    k <= k + 1'b1;
                end
            end
            H_LEER: if (espera != 3'd0) espera <= espera - 1'b1; else begin
                muestra <= capturada; bit_crc <= 6'd0; estado <= H_ENVIAR;
            end
            H_ENVIAR: begin
                if (bit_crc != 6'd48) begin
                    crc <= (crc >> 1) ^ (realim ? 32'hEDB88320 : 32'd0);
                    bit_crc <= bit_crc + 1'b1;
                end else if (!ocupado_tx && !inicio) begin
                    etiqueta <= "M"; valor <= {2'b00, muestra}; inicio <= 1'b1;
                    if (k == {AK{1'b1}}) estado <= H_CICLOS;
                    else begin k <= k + 1'b1; estado <= H_LEER; espera <= 3'd3; end
                end
            end
            H_CICLOS: if (!ocupado_tx && !inicio) begin
                etiqueta <= "K"; valor <= {24'd0, 16'(entradas), ciclos_max}; inicio <= 1'b1;
                estado <= H_CRC;
            end
            H_CRC: if (!ocupado_tx && !inicio) begin
                etiqueta <= "Z"; valor <= {24'd0, ~crc}; inicio <= 1'b1;
                k <= {AK{1'b0}}; estado <= H_ESPERA;
            end
            default: estado <= H_ESPERA;
            endcase
        end
    end
endmodule

`default_nettype wire
