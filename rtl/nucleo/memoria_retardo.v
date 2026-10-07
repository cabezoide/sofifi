// SPDX-License-Identifier: MIT
//
// Memoria de retardo circular del núcleo, como la del FV-1 (ADR 0004, ADR 0008).
// Equivale a model/sofifi/domain/memoria.py:
//
//   - física = (puntero + a) mod P, con P = `palabras` (la del programa);
//   - el puntero DECREMENTA una vez por muestra (`avanzar`);
//   - guarda 18 bit (dato_a_memoria) y devuelve el dato alineado (<< 6).
//
// La dirección relativa `a` está en [-1, P-1]: el programa lo garantiza para
// CHO (alcance_cho en isa.py, ADR 0009). Así basta una corrección de ±P.
//
// Tiempos: la dirección se registra (1 ciclo) y bsram_pipe tarda 3 (bloques con
// registro de salida interno y multiplexor registrado; fails.md, F-11). Una
// lectura presentada en el ciclo t da `dato_r` en t+4. Una escritura presentada
// en t se hace en t+1; una lectura presentada en t+1 ya la ve.
`default_nettype none

module memoria_retardo #(
    parameter integer PALABRAS_MAX = 43_008
) (
    input  wire               clk,
    input  wire               rst,
    input  wire [15:0]        palabras,   // P del programa, en [1, PALABRAS_MAX]
    input  wire               avanzar,    // pulso al final de cada muestra
    input  wire signed [16:0] dir_r,      // dirección relativa de lectura
    output wire signed [23:0] dato_r,
    input  wire               we,
    input  wire signed [16:0] dir_w,
    input  wire signed [23:0] dato_w
);
    localparam integer AD = $clog2(PALABRAS_MAX);

    reg [15:0] puntero;
    always @(posedge clk) begin
        if (rst)          puntero <= 16'd0;
        else if (avanzar) puntero <= (puntero == 16'd0) ? palabras - 1'b1 : puntero - 1'b1;
    end

    // (puntero + a) con a en [-1, P-1]: el resultado está en [-1, 2P-2].
    function automatic [AD-1:0] fisica(input [15:0] ptr, input signed [16:0] a, input [15:0] p);
        reg signed [18:0] s;
        begin
            s = $signed({3'b000, ptr}) + {{2{a[16]}}, a};
            if (s < 19'sd0)                         s = s + $signed({3'b000, p});
            else if (s >= $signed({3'b000, p}))     s = s - $signed({3'b000, p});
            fisica = s[AD-1:0];
        end
    endfunction

    reg [AD-1:0] fis_r, fis_w;
    reg          we_r;
    reg [17:0]   palabra_w;
    wire [17:0]  palabra_nueva;
    dato_a_memoria u_dm (.dato(dato_w), .palabra(palabra_nueva));

    always @(posedge clk) begin
        fis_r     <= fisica(puntero, dir_r, palabras);
        fis_w     <= fisica(puntero, dir_w, palabras);
        we_r      <= we & ~rst;
        palabra_w <= palabra_nueva;
    end

    wire [17:0] palabra_r;
    bsram_pipe #(.PALABRAS(PALABRAS_MAX), .ANCHO(18)) u_mem (
        .clk(clk), .we(we_r), .dir_w(fis_w), .dato_w(palabra_w),
        .dir_r(fis_r), .dato_r(palabra_r)
    );
    assign dato_r = {palabra_r, 6'd0};
endmodule

`default_nettype wire
