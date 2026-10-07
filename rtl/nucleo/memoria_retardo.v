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
//
// Con más de GRUPO bloques, bsram_pipe va segmentada por grupos (fails.md,
// F-15) y la lectura tarda 4 ciclos más: `dato_r` en t+8. La escritura también
// se retrasa, así que una lectura presentada en t+1 sigue viéndola.
`default_nettype none

module memoria_retardo #(
    parameter integer PALABRAS_MAX = 43_008,
    parameter integer GRUPO        = 8        // bloques por grupo (bsram_pipe)
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

    // puntero ± P bajan con el puntero: así ninguna suma de P va detrás de él
    // (fails.md, F-15). `palabras` solo cambia durante el reset.
    reg [15:0]        puntero;
    reg signed [17:0] mas_p, menos_p;
    always @(posedge clk) begin
        if (rst) begin
            puntero <= 16'd0;
            mas_p   <= $signed({2'b00, palabras});
            menos_p <= -$signed({2'b00, palabras});
        end else if (avanzar) begin
            if (puntero == 16'd0) begin
                puntero <= palabras - 1'b1;
                mas_p   <= $signed({1'b0, palabras, 1'b0}) - 18'sd1;   // 2P − 1
                menos_p <= -18'sd1;
            end else begin
                puntero <= puntero - 1'b1;
                mas_p   <= mas_p - 18'sd1;
                menos_p <= menos_p - 18'sd1;
            end
        end
    end

    // (puntero + a) con a en [-1, P-1]: el resultado está en [-1, 2P-2]. Las tres
    // sumas posibles van en paralelo y el signo elige (fails.md, F-15): sumar,
    // comparar y corregir en serie era el camino crítico.

    /* verilator lint_off UNUSEDSIGNAL */   // de cada suma solo se usan AD bit y el signo
    function automatic [AD-1:0] fisica(input [15:0] ptr, input signed [17:0] ptr_mas_p,
                                       input signed [17:0] ptr_menos_p, input signed [16:0] a);
        reg signed [18:0] s0, s_menos, s_mas;
        begin
            s0      = $signed({3'b000, ptr}) + {{2{a[16]}}, a};
            s_menos = {ptr_menos_p[17], ptr_menos_p} + {{2{a[16]}}, a};
            s_mas   = {ptr_mas_p[17], ptr_mas_p} + {{2{a[16]}}, a};
            if (s0[18])            fisica = s_mas[AD-1:0];     // s0 < 0
            else if (!s_menos[18]) fisica = s_menos[AD-1:0];   // s0 ≥ P
            else                   fisica = s0[AD-1:0];
        end
    endfunction
    /* verilator lint_on UNUSEDSIGNAL */

    reg [AD-1:0] fis_r, fis_w;
    reg          we_r;
    reg [17:0]   palabra_w;
    wire [17:0]  palabra_nueva;
    dato_a_memoria u_dm (.dato(dato_w), .palabra(palabra_nueva));

    always @(posedge clk) begin
        fis_r     <= fisica(puntero, mas_p, menos_p, dir_r);
        fis_w     <= fisica(puntero, mas_p, menos_p, dir_w);
        we_r      <= we & ~rst;
        palabra_w <= palabra_nueva;
    end

    wire [17:0] palabra_r;
    bsram_pipe #(.PALABRAS(PALABRAS_MAX), .ANCHO(18), .GRUPO(GRUPO)) u_mem (
        .clk(clk), .we(we_r), .dir_w(fis_w), .dato_w(palabra_w),
        .dir_r(fis_r), .dato_r(palabra_r)
    );
    assign dato_r = {palabra_r, 6'd0};
endmodule

`default_nettype wire
