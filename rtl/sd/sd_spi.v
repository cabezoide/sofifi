// SPDX-License-Identifier: MIT
//
// Controlador de tarjeta SD en modo SPI (Fase 08, ADR 0004): arranque y lectura
// de bloques de 512 bytes. No escribe en la tarjeta.
//
// Arranque, al salir del reset:
//   1. 80 ciclos de SCK con CS alto y MOSI alto, a reloj lento (≤ 400 kHz).
//   2. CMD0 (pasa a SPI): R1 = 0x01.
//   3. CMD8 con 0x1AA: R1 = 0x01 y eco 0x1AA. Solo tarjetas de la versión 2
//      (todas las SDHC y SDXC); una tarjeta de la versión 1 da error.
//   4. CMD55 + ACMD41 (HCS) hasta R1 = 0x00, con un tope de intentos.
//   5. CMD58: el bit CCS del OCR dice si la dirección es de bloque (SDHC, SDXC)
//      o de byte (SDSC).
//   6. Pasa al reloj rápido y pone `listo`.
//
// Lectura: con `listo` y sin `ocupado`, un pulso en `leer` y el número de
// bloque en `bloque`. La petición se guarda hasta atenderla.
// CMD17, espera el token 0xFE y saca los 512 bytes por `dato` con `dato_v`;
// el CRC16 de la tarjeta se lee y se descarta (el banco lleva su CRC-32).
// `fin` da un pulso al acabar. Si algo falla, `error` queda a 1 con su código
// en `codigo` hasta el siguiente reset; no se reintenta solo.
//
// SPI modo 0: MOSI cambia con SCK bajo y la tarjeta lo lee en el flanco de
// subida; MISO se muestrea en el flanco de subida. SCK sale de un divisor del
// reloj de 100 MHz: no hay otro dominio de reloj. MISO pasa por dos biestables.
`default_nettype none

module sd_spi #(
    parameter integer DIV_LENTO  = 125,      // medio periodo: 100 MHz / 250 = 400 kHz
    parameter integer DIV_RAPIDO = 4,        // medio periodo: 12,5 MHz; mínimo 4 (MISO pasa por 2 biestables)
    parameter integer INTENTOS_ACMD41 = 4000,  // > 1 s a reloj lento
    parameter integer ESPERA_TOKEN = 65535     // bytes de espera al token de datos
) (
    input  wire        clk,
    input  wire        rst,
    // Control
    input  wire        leer,
    input  wire [31:0] bloque,
    output reg         listo,
    output wire        ocupado,
    output reg         error,
    output reg  [3:0]  codigo,
    output reg  [7:0]  dato,
    output reg         dato_v,
    output reg         fin,
    // Tarjeta
    output reg         sd_cs_n,
    output reg         sd_sck,
    output reg         sd_mosi,
    input  wire        sd_miso
);
    // Códigos de error (`codigo`).
    localparam [3:0] ERR_CMD0 = 4'd1, ERR_CMD8 = 4'd2, ERR_ACMD41 = 4'd3, ERR_CMD58 = 4'd4,
                     ERR_CMD17 = 4'd5, ERR_TOKEN = 4'd6;

    // ── Motor de bytes: envía `tx` y recibe `rx` en 8 periodos de SCK ─────
    (* ASYNC_REG = "TRUE" *) reg [1:0] miso_s;
    always @(posedge clk) miso_s <= {miso_s[0], sd_miso};
    wire miso = miso_s[1];

    reg        rapido;
    reg [7:0]  div;
    reg        byte_ir, byte_hecho;
    reg [7:0]  tx, rx, desliza;
    reg [3:0]  bit_n;
    wire [7:0] medio = rapido ? 8'(DIV_RAPIDO - 1) : 8'(DIV_LENTO - 1);
    always @(posedge clk) begin
        byte_hecho <= 1'b0;
        if (rst) begin
            div <= 8'd0; bit_n <= 4'd0; sd_sck <= 1'b0; sd_mosi <= 1'b1;
        end else if (byte_ir && bit_n == 4'd0 && !byte_hecho) begin
            // Empieza un byte: el primer bit sale ya, con SCK bajo.
            desliza <= {tx[6:0], 1'b1}; sd_mosi <= tx[7];
            bit_n <= 4'd8; div <= 8'd0; sd_sck <= 1'b0;
        end else if (bit_n != 4'd0) begin
            if (div != medio) div <= div + 1'b1;
            else begin
                div <= 8'd0;
                if (!sd_sck) begin            // flanco de subida: se lee MISO
                    sd_sck <= 1'b1;
                    rx <= {rx[6:0], miso};
                end else begin                // flanco de bajada: siguiente bit
                    sd_sck <= 1'b0;
                    if (bit_n == 4'd1) begin
                        bit_n <= 4'd0; byte_hecho <= 1'b1; sd_mosi <= 1'b1;
                    end else begin
                        bit_n <= bit_n - 1'b1;
                        sd_mosi <= desliza[7]; desliza <= {desliza[6:0], 1'b1};
                    end
                end
            end
        end
    end

    // ── Secuencia ─────────────────────────────────────────────────────────
    localparam [4:0] S_RELOJES = 5'd0, S_CMD = 5'd1, S_R1 = 5'd2, S_EXTRA = 5'd3,
                     S_DECIDE = 5'd4, S_LIBRE = 5'd5, S_TOKEN = 5'd7,
                     S_DATOS = 5'd8, S_CRC = 5'd9, S_FALLO = 5'd10;
    localparam [2:0] P_CMD0 = 3'd0, P_CMD8 = 3'd1, P_CMD55 = 3'd2, P_ACMD41 = 3'd3,
                     P_CMD58 = 3'd4, P_CMD17 = 3'd5;
    reg [4:0]  s;
    reg [2:0]  paso;
    reg [55:0] trama;      // un byte 0xFF de separación y el comando de 6 bytes
    reg [2:0]  n_tx;       // bytes de la trama que faltan
    reg [3:0]  n;          // contador corto: relojes iniciales, intentos de R1, bytes extra
    reg [7:0]  r1;
    /* verilator lint_off UNUSEDSIGNAL */   // de R7 y del OCR solo se miran el eco y CCS
    reg [31:0] extra;      // R7 o OCR
    /* verilator lint_on UNUSEDSIGNAL */
    reg [15:0] cuenta;     // intentos de ACMD41, espera al token
    reg [9:0]  n_datos;
    reg        pedido;     // `leer` llegó y aún no se atiende
    reg [31:0] bloque_p;
    reg        ccs;

    assign ocupado = !listo || s != S_LIBRE || byte_ir || pedido;

    function automatic [55:0] comando(input [5:0] indice, input [31:0] arg, input [7:0] crc);
        comando = {8'hFF, 2'b01, indice, arg, crc};
    endfunction

    // Lanza un byte; el resultado está en rx cuando byte_hecho.
    task automatic enviar(input [7:0] b);
        begin tx <= b; byte_ir <= 1'b1; end
    endtask

    always @(posedge clk) begin
        dato_v <= 1'b0;
        fin    <= 1'b0;
        if (byte_hecho) byte_ir <= 1'b0;
        if (leer && listo && !pedido) begin pedido <= 1'b1; bloque_p <= bloque; end
        if (rst) begin
            pedido <= 1'b0;
            s <= S_RELOJES; paso <= P_CMD0; n <= 4'd0; sd_cs_n <= 1'b1;
            byte_ir <= 1'b0; tx <= 8'hFF; rapido <= 1'b0; listo <= 1'b0;
            error <= 1'b0; codigo <= 4'd0; ccs <= 1'b0; cuenta <= 16'd0;
        end else if (!byte_ir || byte_hecho) begin
            case (s)
            S_RELOJES: begin   // 10 bytes 0xFF con CS alto: 80 relojes
                if (byte_hecho) n <= n + 1'b1;
                if (byte_hecho && n == 4'd9) begin
                    sd_cs_n <= 1'b0; paso <= P_CMD0;
                    trama <= comando(6'd0, 32'd0, 8'h95); n_tx <= 3'd7; s <= S_CMD;
                end else enviar(8'hFF);
            end
            S_CMD: begin       // envía la trama de 6 bytes
                if (n_tx == 3'd0) begin n <= 4'd0; s <= S_R1; enviar(8'hFF); end
                else begin
                    enviar(trama[55:48]); trama <= {trama[47:0], 8'hFF};
                    n_tx <= n_tx - 1'b1;
                end
            end
            S_R1: if (byte_hecho) begin   // hasta 8 bytes a 0xFF antes de R1
                if (rx != 8'hFF) begin
                    r1 <= rx; n <= 4'd0;
                    if (paso == P_CMD8 || paso == P_CMD58) begin s <= S_EXTRA; enviar(8'hFF); end
                    else s <= S_DECIDE;
                end else if (n == 4'd8) begin r1 <= 8'hFF; s <= S_DECIDE; end
                else begin n <= n + 1'b1; enviar(8'hFF); end
            end
            S_EXTRA: if (byte_hecho) begin   // 4 bytes de R7 u OCR
                extra <= {extra[23:0], rx}; n <= n + 1'b1;
                if (n == 4'd3) s <= S_DECIDE; else enviar(8'hFF);
            end
            S_DECIDE: case (paso)
                P_CMD0: if (r1 == 8'h01) begin
                    paso <= P_CMD8; trama <= comando(6'd8, 32'h000001AA, 8'h87);
                    n_tx <= 3'd7; s <= S_CMD;
                end else begin codigo <= ERR_CMD0; s <= S_FALLO; end
                P_CMD8: if (r1 == 8'h01 && extra[11:0] == 12'h1AA) begin
                    paso <= P_CMD55; trama <= comando(6'd55, 32'd0, 8'h01);
                    n_tx <= 3'd7; s <= S_CMD; cuenta <= 16'd0;
                end else begin codigo <= ERR_CMD8; s <= S_FALLO; end
                P_CMD55: begin
                    paso <= P_ACMD41; trama <= comando(6'd41, 32'h40000000, 8'h01);
                    n_tx <= 3'd7; s <= S_CMD;
                end
                P_ACMD41: if (r1 == 8'h00) begin
                    paso <= P_CMD58; trama <= comando(6'd58, 32'd0, 8'h01);
                    n_tx <= 3'd7; s <= S_CMD;
                end else if (r1 == 8'h01 && cuenta != 16'(INTENTOS_ACMD41)) begin
                    cuenta <= cuenta + 1'b1;
                    paso <= P_CMD55; trama <= comando(6'd55, 32'd0, 8'h01);
                    n_tx <= 3'd7; s <= S_CMD;
                end else begin codigo <= ERR_ACMD41; s <= S_FALLO; end
                P_CMD58: if (r1 == 8'h00) begin
                    ccs <= extra[30]; rapido <= 1'b1; listo <= 1'b1;
                    sd_cs_n <= 1'b1; s <= S_LIBRE; enviar(8'hFF);
                end else begin codigo <= ERR_CMD58; s <= S_FALLO; end
                default: if (r1 == 8'h00) begin   // P_CMD17
                    cuenta <= 16'd0; s <= S_TOKEN; enviar(8'hFF);
                end else begin codigo <= ERR_CMD17; s <= S_FALLO; end
            endcase
            S_LIBRE: if (pedido) begin
                pedido <= 1'b0; sd_cs_n <= 1'b0; paso <= P_CMD17;
                trama <= comando(6'd17, ccs ? bloque_p : {bloque_p[22:0], 9'd0}, 8'h01);
                n_tx <= 3'd7; s <= S_CMD;
            end
            S_TOKEN: if (byte_hecho) begin   // 0xFF mientras espera; 0xFE abre los datos
                if (rx == 8'hFE) begin n_datos <= 10'd0; s <= S_DATOS; enviar(8'hFF); end
                else if (rx != 8'hFF || cuenta == 16'(ESPERA_TOKEN)) begin
                    codigo <= ERR_TOKEN; s <= S_FALLO;
                end else begin cuenta <= cuenta + 1'b1; enviar(8'hFF); end
            end
            S_DATOS: if (byte_hecho) begin
                dato <= rx; dato_v <= 1'b1; n_datos <= n_datos + 1'b1;
                if (n_datos == 10'd511) begin n <= 4'd0; s <= S_CRC; end
                enviar(8'hFF);
            end
            S_CRC: if (byte_hecho) begin     // dos bytes de CRC16 y uno con CS alto
                n <= n + 1'b1;
                if (n == 4'd1) sd_cs_n <= 1'b1;
                if (n == 4'd2) begin fin <= 1'b1; s <= S_LIBRE; end
                else enviar(8'hFF);
            end
            S_FALLO: begin error <= 1'b1; sd_cs_n <= 1'b1; end
            default: s <= S_FALLO;
            endcase
        end
    end
endmodule

`default_nettype wire
