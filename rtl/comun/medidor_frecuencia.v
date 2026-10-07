// SPDX-License-Identifier: MIT
//
// Cuenta los ciclos de `clk_medido` durante VENTANA ciclos de `clk_ref`.
// Al final de cada ventana, `cuenta` se actualiza y `nueva` da un pulso de un
// ciclo de `clk_ref`.
//
// Cruce de dominios: el contador del dominio medido viaja en código Gray. Cada
// incremento cambia un solo bit, así que la muestra sincronizada vale el valor
// antiguo o el nuevo, nunca una mezcla. El error es de ±1 ciclo por ventana.
`default_nettype none

module medidor_frecuencia #(
    parameter integer VENTANA = 50_000_000   // ciclos de clk_ref por medida
) (
    input  wire        clk_ref,
    input  wire        rst_ref,
    input  wire        clk_medido,
    output reg  [31:0] cuenta,
    output reg         nueva
);
    // Dominio medido: contador binario y su copia Gray registrada.
    reg [31:0] bin_m;
    reg [31:0] gray_m;
    always @(posedge clk_medido) begin
        bin_m  <= bin_m + 1'b1;
        gray_m <= bin_m ^ (bin_m >> 1);
    end

    // Dominio de referencia: sincronizador de dos etapas y paso a binario.
    (* ASYNC_REG = "TRUE" *) reg [31:0] gray_s1;
    (* ASYNC_REG = "TRUE" *) reg [31:0] gray_s2;
    reg [31:0] bin_r;
    integer i;
    always @(*) begin
        bin_r[31] = gray_s2[31];
        for (i = 30; i >= 0; i = i - 1) bin_r[i] = bin_r[i + 1] ^ gray_s2[i];
    end

    localparam integer ANCHO_V = $clog2(VENTANA);
    reg [ANCHO_V-1:0] ciclos;
    reg [31:0]        anterior;

    always @(posedge clk_ref) begin
        gray_s1 <= gray_m;
        gray_s2 <= gray_s1;
        nueva   <= 1'b0;
        if (rst_ref) begin
            ciclos   <= {ANCHO_V{1'b0}};
            anterior <= bin_r;
            cuenta   <= 32'd0;
        end else if (ciclos == ANCHO_V'(VENTANA - 1)) begin
            ciclos   <= {ANCHO_V{1'b0}};
            cuenta   <= bin_r - anterior;
            anterior <= bin_r;
            nueva    <= 1'b1;
        end else begin
            ciclos <= ciclos + 1'b1;
        end
    end
endmodule

`default_nettype wire
