// SPDX-License-Identifier: MIT
//
// Lector de la pista de audio de la microSD (Fase 13, ADR 0015). Lee con
// sd_spi.v y entrega una muestra por `tick`. El formato es el de
// model/sofifi/domain/pista.py.
//
//   1. Bloque 0: magia "SOFIPIST", versión 1, número de muestras en
//      [1, 2^30) y CRC-32 de esos campos. Si algo falla, `error` queda a 1 con
//      su motivo y la salida es silencio.
//   2. Bloques 1 y siguientes: 256 muestras de 16 bit con signo, en
//      big-endian. Van a una cola de 1 024 muestras en un bloque de BSRAM.
//   3. Al agotarse la pista, el lector vuelve al bloque 1: la pista se repite.
//
// El lector no sigue posiciones escritas en la tarjeta. El bloque sale de su
// propia cuenta, y las muestras que quedan, de la cabecera ya validada.
//
// La cola se rellena por bloques enteros, y solo cuando hay sitio para uno.
// Una tarjeta lenta vacía la cola: entonces `vacio` queda a 1 y la muestra es
// cero. Se declara y se mide; no se esconde. Con 1 024 muestras, la cola
// aguanta 21 ms, y un bloque tarda unos 0,33 ms a 12,5 MHz (16 muestras).
//
// Una pista más corta que un bloque también vacía la cola, porque cada vuelta
// vuelve a leer un bloque entero para pocas muestras. Por eso `sofifi pista`
// exige 256 muestras como mínimo (model/sofifi/domain/pista.py, MIN_MUESTRAS).
//
// La muestra va adelantada: `muestra` se carga en cuanto la cola entrega el
// valor siguiente, no en el `tick`. El núcleo lee su entrada en el ciclo del
// `tick`, así que la muestra tiene que estar puesta antes (la BSRAM tarda 3
// ciclos). El `tick` solo consume: pide la siguiente.
//
// `preparado` sube con la primera muestra lista y no baja. El top espera a esa
// señal para dar `tick` al núcleo: así la primera muestra del núcleo es la
// primera de la pista, y el RTL se puede comparar con el modelo (ADR 0003).
`default_nettype none

module lector_pista #(
    parameter integer MUESTRAS_COLA = 1024,
    parameter integer HOLGURA       = 256  // las muestras de un bloque
) (
    input  wire               clk,
    input  wire               rst,
    input  wire               tick,
    output reg  signed [23:0] muestra,  // S.23 para el núcleo
    output reg                vacio,    // la cola se quedó sin datos
    output reg                listo,    // la cabecera es válida
    output reg                preparado,  // ya hay una muestra lista: el núcleo puede arrancar
    output reg                error,
    output reg  [2:0]         motivo,
    // sd_spi
    output reg                sd_leer,
    output reg  [31:0]        sd_bloque,
    input  wire               sd_listo,
    input  wire               sd_ocupado,
    input  wire               sd_error,
    input  wire [7:0]         sd_dato,
    input  wire               sd_dato_v,
    input  wire               sd_fin
);
    localparam [63:0] MAGIA   = 64'h534F_4649_5049_5354;  // "SOFIPIST"
    localparam [7:0]  VERSION = 8'd1;
    localparam [31:0] POLI    = 32'hEDB88320;  // CRC-32 de zlib, bit a bit

    localparam [2:0] ERR_SD = 3'd1, ERR_MAGIA = 3'd2, ERR_VERSION = 3'd3,
                     ERR_CRC = 3'd4, ERR_MUESTRAS = 3'd5;
    localparam [2:0] E_INICIO = 3'd0, E_CABECERA = 3'd1, E_PEDIR = 3'd2,
                     E_DATOS = 3'd3, E_PARADO = 3'd4;

    localparam integer AC = $clog2(MUESTRAS_COLA);

    reg [2:0] estado;

    // ── Cola de muestras en un bloque de BSRAM ───────────────────────────
    reg  [AC-1:0] puntero_w, puntero_r;
    reg  [AC:0]   ocupadas;
    // La BSRAM va de 18 en 18 bit y la muestra son 16: los dos de arriba sobran.
    /* verilator lint_off UNUSEDSIGNAL */
    wire [17:0]   cola_sale;
    /* verilator lint_on UNUSEDSIGNAL */

    reg [8:0]  indice;      // byte dentro del bloque
    reg [7:0]  byte_alto;
    reg [9:0]  restan;      // muestras que quedan de este bloque
    reg        cabeza_v;
    reg        leyendo;

    // Una muestra entra con el segundo byte de la pareja; sale cuando la cabeza
    // está libre. Las dos cosas pueden pasar en el mismo ciclo, así que
    // `ocupadas` se actualiza en un solo sitio.
    wire mete = estado == E_DATOS && sd_dato_v && indice[0] && restan != 10'd0;
    wire saca = !tick && !cabeza_v && !leyendo && ocupadas != {(AC+1){1'b0}};
    wire espacio = ocupadas <= (AC+1)'(MUESTRAS_COLA - HOLGURA);

    bsram_pipe #(
        .PALABRAS (MUESTRAS_COLA),
        .ANCHO    (18)
    ) cola (
        .clk    (clk),
        .we     (mete),
        .dir_w  (puntero_w),
        .dato_w ({2'b00, byte_alto, sd_dato}),
        .dir_r  (puntero_r),
        .dato_r (cola_sale)
    );

    // ── CRC-32 de la cabecera, bit a bit (8 ciclos por byte) ─────────────
    reg        crc_meter;
    reg [31:0] crc;
    reg [7:0]  crc_byte;
    reg [3:0]  crc_bits;
    always @(posedge clk) begin
        if (rst) begin
            crc <= 32'hFFFFFFFF;
            crc_bits <= 4'd0;
        end else if (crc_meter) begin
            crc_byte <= sd_dato;
            crc_bits <= 4'd8;
        end else if (crc_bits != 4'd0) begin
            crc <= (crc >> 1) ^ ((crc[0] ^ crc_byte[0]) ? POLI : 32'd0);
            crc_byte <= crc_byte >> 1;
            crc_bits <= crc_bits - 1'b1;
        end
    end
    wire [31:0] crc_final = ~crc;

    // ── Cabecera, cola y bloques ─────────────────────────────────────────
    reg [31:0] total;        // muestras de la pista
    reg [31:0] pendientes;   // muestras que quedan de esta vuelta
    reg [31:0] campo;        // los cuatro últimos bytes de la cabecera
    reg [1:0]  espera;       // ciclos que faltan de la lectura de BSRAM
    reg        magia_mal;
    reg        version_mal;

    wire [7:0] magia_byte = MAGIA[8*(7-indice[2:0]) +: 8];
    wire       fin_cabecera = sd_dato_v && indice == 9'd12;

    always @(posedge clk) begin
        if (rst) begin
            estado <= E_INICIO;
            muestra <= 24'sd0;
            vacio <= 1'b0; listo <= 1'b0; error <= 1'b0; motivo <= 3'd0;
            preparado <= 1'b0;
            sd_leer <= 1'b0; sd_bloque <= 32'd0;
            puntero_w <= {AC{1'b0}}; puntero_r <= {AC{1'b0}};
            ocupadas <= {(AC+1){1'b0}};
            cabeza_v <= 1'b0; espera <= 2'd0; leyendo <= 1'b0;
            crc_meter <= 1'b0;
            indice <= 9'd0; total <= 32'd0; pendientes <= 32'd0; restan <= 10'd0;
            campo <= 32'd0; magia_mal <= 1'b0; version_mal <= 1'b0;
            byte_alto <= 8'd0;
        end else begin
            sd_leer <= 1'b0;
            crc_meter <= 1'b0;
            ocupadas <= ocupadas + {{AC{1'b0}}, mete} - {{AC{1'b0}}, saca};
            if (mete) puntero_w <= puntero_w + 1'b1;
            if (saca) puntero_r <= puntero_r + 1'b1;

            // ── Salida: el tick consume la muestra y pide la siguiente ───
            if (tick) begin
                if (!cabeza_v) muestra <= 24'sd0;  // la cola se quedó sin datos
                vacio    <= vacio | (listo && !cabeza_v);
                cabeza_v <= 1'b0;
            end
            if (saca) begin
                leyendo <= 1'b1;
                // La BSRAM tarda 3 ciclos: la dirección se presenta en este
                // ciclo y el dato se recoge en el tercero. Con un ciclo más,
                // la salida ya sería de la dirección siguiente.
                espera  <= 2'd2;
            end else if (leyendo) begin
                if (espera != 2'd0) begin
                    espera <= espera - 1'b1;
                end else begin
                    muestra   <= {cola_sale[15:0], 8'd0};
                    cabeza_v  <= 1'b1;
                    leyendo   <= 1'b0;
                    preparado <= preparado | listo;
                end
            end

            if (sd_error && estado != E_PARADO) begin
                estado <= E_PARADO;
                error  <= 1'b1;
                motivo <= ERR_SD;
            end else begin
                case (estado)
                    E_INICIO:
                        if (sd_listo && !sd_ocupado) begin
                            sd_leer <= 1'b1; sd_bloque <= 32'd0;
                            indice <= 9'd0; estado <= E_CABECERA;
                        end

                    E_CABECERA: begin
                        if (sd_dato_v) begin
                            indice <= indice + 1'b1;
                            if (indice < 9'd13) crc_meter <= 1'b1;
                            if (indice < 9'd8 && sd_dato != magia_byte) magia_mal <= 1'b1;
                            if (indice == 9'd8 && sd_dato != VERSION) version_mal <= 1'b1;
                            if (indice >= 9'd9 && indice < 9'd17) campo <= {campo[23:0], sd_dato};
                            if (fin_cabecera) total <= {campo[23:0], sd_dato};
                        end
                        if (sd_fin) begin
                            if (magia_mal) begin
                                estado <= E_PARADO; error <= 1'b1; motivo <= ERR_MAGIA;
                            end else if (version_mal) begin
                                estado <= E_PARADO; error <= 1'b1; motivo <= ERR_VERSION;
                            end else if (crc_final != campo) begin
                                estado <= E_PARADO; error <= 1'b1; motivo <= ERR_CRC;
                            end else if (total == 32'd0 || total[31:30] != 2'b00) begin
                                estado <= E_PARADO; error <= 1'b1; motivo <= ERR_MUESTRAS;
                            end else begin
                                listo <= 1'b1; pendientes <= total;
                                sd_bloque <= 32'd1; estado <= E_PEDIR;
                            end
                        end
                    end

                    E_PEDIR:
                        if (espacio && !sd_ocupado) begin
                            sd_leer <= 1'b1;
                            indice  <= 9'd0;
                            restan  <= (pendientes > 32'd255) ? 10'd256
                                                              : {1'b0, pendientes[8:0]};
                            estado  <= E_DATOS;
                        end

                    E_DATOS: begin
                        if (sd_dato_v) begin
                            indice <= indice + 1'b1;
                            if (!indice[0]) byte_alto <= sd_dato;
                            if (mete) begin
                                restan     <= restan - 1'b1;
                                pendientes <= pendientes - 1'b1;
                            end
                        end
                        if (sd_fin) begin
                            if (pendientes == 32'd0) begin
                                pendientes <= total;
                                sd_bloque  <= 32'd1;
                            end else begin
                                sd_bloque <= sd_bloque + 1'b1;
                            end
                            estado <= E_PEDIR;
                        end
                    end

                    default: ;  // E_PARADO: silencio hasta el próximo reset
                endcase
            end
        end
    end
endmodule

`default_nettype wire
