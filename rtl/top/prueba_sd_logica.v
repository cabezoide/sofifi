// SPDX-License-Identifier: MIT
//
// Lógica de rtl/top/prueba_sd.v (protocolo y órdenes, allí), sin PLL ni pines
// triestado: es lo que simula sim/top/prueba_sd_test.py con el modelo de tarjeta.
`default_nettype none

module prueba_sd_logica #(
    parameter integer F_RELOJ = 100_000_000,
    parameter integer BAUDIOS = 115_200,
    parameter integer DIV_LENTO = 125,
    parameter integer INTENTOS_ACMD41 = 4000
) (
    input  wire clk,      // 100 MHz
    input  wire rst,
    input  wire uart_rx,
    output wire uart_tx,
    output reg  v1,       // 0: se prueba la v2; 1: la v1
    output wire sd_cs_n,
    output wire sd_sck,
    output wire sd_mosi,
    input  wire sd_miso
);

    localparam integer DIVISOR = F_RELOJ / BAUDIOS;

    // ── Revisión del PMOD TF ──────────────────────────────────────────────
    reg        sd_rst;
    reg        hay;         // la tarjeta arrancó con la revisión en `v1`

    // ── Carga ─────────────────────────────────────────────────────────────
    reg         cargar;
    reg  [9:0]  ranura;
    wire        listo, sd_error, hecho, fallo, prog_we;
    wire [3:0]  codigo, motivo;
    wire [53:0] prog_dato;
    wire [11:0] instrucciones;
    wire [15:0] palabras;
    /* verilator lint_off UNUSEDSIGNAL */   // no se informan: LFO, dirección, ocupado
    wire [7:0]  lfo_tipos;
    wire [59:0] lfo_excursiones;
    wire        absoluta, nucleo_rst, ocupado;
    wire [10:0] prog_dir;
    /* verilator lint_on UNUSEDSIGNAL */
    carga_sd #(.DIV_LENTO(DIV_LENTO), .INTENTOS_ACMD41(INTENTOS_ACMD41)) u_carga (
        .clk(clk), .rst(rst | sd_rst), .cargar(cargar), .ranura(ranura),
        .sd_listo(listo), .sd_error(sd_error), .sd_codigo(codigo), .ocupado(ocupado),
        .hecho(hecho), .fallo(fallo), .motivo(motivo), .sd_cs_n(sd_cs_n), .sd_sck(sd_sck),
        .sd_mosi(sd_mosi), .sd_miso(sd_miso), .nucleo_rst(nucleo_rst), .prog_we(prog_we),
        .prog_dir(prog_dir), .prog_dato(prog_dato), .cfg_instrucciones(instrucciones),
        .cfg_palabras(palabras), .cfg_lfo_tipos(lfo_tipos),
        .cfg_lfo_excursiones(lfo_excursiones), .cfg_absoluta(absoluta)
    );

    // CRC-32 de las palabras escritas: 56 bits por palabra, byte alto primero y
    // cada byte desde su bit bajo (zlib). Llega una palabra cada ~430 ciclos.
    localparam [31:0] POLI = 32'hEDB88320;
    reg [31:0] crc;
    reg [55:0] palabra;
    reg [5:0]  n_bits;     // 0..55: bit en curso; 56: libre
    wire [2:0] byte_i = n_bits[5:3];
    wire [5:0] pos    = 6'd48 - {byte_i, 3'd0} + {3'd0, n_bits[2:0]};
    always @(posedge clk) begin
        if (rst || cargar) begin
            crc <= 32'hFFFFFFFF; n_bits <= 6'd56;
        end else if (prog_we) begin
            palabra <= {2'b00, prog_dato}; n_bits <= 6'd0;
        end else if (n_bits != 6'd56) begin
            crc <= (crc >> 1) ^ ((crc[0] ^ palabra[pos]) ? POLI : 32'd0);
            n_bits <= n_bits + 1'b1;
        end
    end

    // ── UART ──────────────────────────────────────────────────────────────
    wire [7:0] rx_dato;
    wire       rx_v;
    uart_rx #(.DIVISOR(DIVISOR)) u_rx (.clk(clk), .rst(rst), .rx(uart_rx), .dato(rx_dato), .valido(rx_v));
    reg        linea_ir;
    reg [7:0]  etiqueta;
    reg [31:0] valor;
    wire       linea_ocupada;
    linea_hex #(.DIGITOS(8), .DIVISOR(DIVISOR)) u_linea (
        .clk(clk), .rst(rst), .inicio(linea_ir), .etiqueta(etiqueta), .valor(valor),
        .ocupado(linea_ocupada), .tx(uart_tx)
    );

    // ── Secuencia ─────────────────────────────────────────────────────────
    localparam [3:0] T_ARRANCA = 4'd0, T_ESPERA = 4'd1, T_LIBRE = 4'd2, T_K_ALTO = 4'd3,
                     T_K_BAJO = 4'd4, T_CARGA = 4'd5, T_ENVIA = 4'd6;
    reg [3:0]  t;
    reg [2:0]  cola_n;          // líneas por enviar (de cola_etq/cola_val)
    reg [7:0]  cola_etq [0:2];
    reg [31:0] cola_val [0:2];
    reg [7:0]  pausa;
    always @(posedge clk) begin
        cargar <= 1'b0; linea_ir <= 1'b0;
        if (rst) begin
            t <= T_ARRANCA; v1 <= 1'b0; sd_rst <= 1'b1; hay <= 1'b0; cola_n <= 3'd0; pausa <= 8'd0;
        end else begin
            case (t)
            T_ARRANCA: begin   // reset corto del controlador y espera a la tarjeta
                pausa <= pausa + 1'b1;
                if (pausa == 8'hFF) begin sd_rst <= 1'b0; t <= T_ESPERA; end
            end
            T_ESPERA: if (listo) begin hay <= 1'b1; t <= T_LIBRE; end
                else if (sd_error && !v1) begin v1 <= 1'b1; sd_rst <= 1'b1; t <= T_ARRANCA; end
                else if (sd_error) t <= T_LIBRE;
            T_LIBRE: if (rx_v && rx_dato == "S") begin
                cola_etq[0] <= "M"; cola_val[0] <= {30'd0, hay ? (v1 ? 2'd1 : 2'd2) : 2'd0};
                cola_etq[1] <= "E"; cola_val[1] <= {28'd0, codigo};
                cola_n <= 3'd2; t <= T_ENVIA;
            end else if (rx_v && rx_dato == "L") t <= T_K_ALTO;
            T_K_ALTO: if (rx_v) begin ranura[9:8] <= rx_dato[1:0]; t <= T_K_BAJO; end
            T_K_BAJO: if (rx_v) begin ranura[7:0] <= rx_dato; cargar <= 1'b1; t <= T_CARGA; end
            T_CARGA: if (hecho) begin
                // La última palabra entró al menos 3 bytes de SD antes (> 56 ciclos).
                cola_etq[0] <= "I"; cola_val[0] <= {20'd0, instrucciones};
                cola_etq[1] <= "P"; cola_val[1] <= {16'd0, palabras};
                cola_etq[2] <= "X"; cola_val[2] <= ~crc;
                cola_n <= 3'd3; t <= T_ENVIA;
            end else if (fallo) begin
                cola_etq[0] <= "F"; cola_val[0] <= {28'd0, motivo};
                cola_n <= 3'd1; t <= T_ENVIA;
            end
            T_ENVIA: if (cola_n == 3'd0) t <= T_LIBRE;
                else if (!linea_ocupada && !linea_ir) begin
                    etiqueta <= cola_etq[0]; valor <= cola_val[0]; linea_ir <= 1'b1;
                    cola_etq[0] <= cola_etq[1]; cola_val[0] <= cola_val[1];
                    cola_etq[1] <= cola_etq[2]; cola_val[1] <= cola_val[2];
                    cola_n <= cola_n - 1'b1;
                end
            default: t <= T_ARRANCA;
            endcase
        end
    end
endmodule

`default_nettype wire
