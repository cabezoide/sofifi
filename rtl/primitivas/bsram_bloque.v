// SPDX-License-Identifier: MIT
//
// Un bloque de BSRAM del GW5A en modo 1K × 18: escritura por el puerto A y
// lectura por el B, con el registro de salida interno del bloque (READ_MODE1 =
// 1). La lectura tarda 2 ciclos: la dirección presentada en t da `dato_r` en t+2.
//
// Por qué no se infiere: Yosys deja siempre la BSRAM en modo bypass (READ_MODE
// = 0), y en ese modo el retardo de reloj a salida real es mucho mayor que el
// que modela nextpnr: la memoria fallaba por encima de 100 MHz con 117 MHz de
// análisis estático (fails.md, F-11). Con el registro interno, la salida sale
// registrada del propio bloque.
//
// Escribir y leer la misma dirección en el mismo ciclo no está definido.
// Con SIMULACION definido se usa el modelo de comportamiento equivalente.
`default_nettype none

module bsram_bloque (
    input  wire        clk,
    input  wire        we,
    input  wire [9:0]  dir_w,
    input  wire [17:0] dato_w,
    input  wire [9:0]  dir_r,
    output wire [17:0] dato_r
);
`ifdef SIMULACION
    reg [17:0] mem [0:1023];
    reg [17:0] leido, salida;
    always @(posedge clk) begin
        if (we) mem[dir_w] <= dato_w;
        leido  <= mem[dir_r];
        salida <= leido;
    end
    assign dato_r = salida;
`else
    /* verilator lint_off PINCONNECTEMPTY */
    DPX9B #(
        .READ_MODE0(1'b0), .READ_MODE1(1'b1),
        .WRITE_MODE0(2'b00), .WRITE_MODE1(2'b00),
        .BIT_WIDTH_0(18), .BIT_WIDTH_1(18),
        .BLK_SEL_0(3'b000), .BLK_SEL_1(3'b000),
        .RESET_MODE("SYNC"),
        // Contenido inicial a cero, explícito: apicula 0.32 falla al empaquetar
        // (IndexError en write_gw5_bsram_init_map) si ninguna BSRAM lo declara.
        .INIT_RAM_00({288{1'b0}}),
        .INIT_RAM_01({288{1'b0}}),
        .INIT_RAM_02({288{1'b0}}),
        .INIT_RAM_03({288{1'b0}}),
        .INIT_RAM_04({288{1'b0}}),
        .INIT_RAM_05({288{1'b0}}),
        .INIT_RAM_06({288{1'b0}}),
        .INIT_RAM_07({288{1'b0}}),
        .INIT_RAM_08({288{1'b0}}),
        .INIT_RAM_09({288{1'b0}}),
        .INIT_RAM_0A({288{1'b0}}),
        .INIT_RAM_0B({288{1'b0}}),
        .INIT_RAM_0C({288{1'b0}}),
        .INIT_RAM_0D({288{1'b0}}),
        .INIT_RAM_0E({288{1'b0}}),
        .INIT_RAM_0F({288{1'b0}}),
        .INIT_RAM_10({288{1'b0}}),
        .INIT_RAM_11({288{1'b0}}),
        .INIT_RAM_12({288{1'b0}}),
        .INIT_RAM_13({288{1'b0}}),
        .INIT_RAM_14({288{1'b0}}),
        .INIT_RAM_15({288{1'b0}}),
        .INIT_RAM_16({288{1'b0}}),
        .INIT_RAM_17({288{1'b0}}),
        .INIT_RAM_18({288{1'b0}}),
        .INIT_RAM_19({288{1'b0}}),
        .INIT_RAM_1A({288{1'b0}}),
        .INIT_RAM_1B({288{1'b0}}),
        .INIT_RAM_1C({288{1'b0}}),
        .INIT_RAM_1D({288{1'b0}}),
        .INIT_RAM_1E({288{1'b0}}),
        .INIT_RAM_1F({288{1'b0}}),
        .INIT_RAM_20({288{1'b0}}),
        .INIT_RAM_21({288{1'b0}}),
        .INIT_RAM_22({288{1'b0}}),
        .INIT_RAM_23({288{1'b0}}),
        .INIT_RAM_24({288{1'b0}}),
        .INIT_RAM_25({288{1'b0}}),
        .INIT_RAM_26({288{1'b0}}),
        .INIT_RAM_27({288{1'b0}}),
        .INIT_RAM_28({288{1'b0}}),
        .INIT_RAM_29({288{1'b0}}),
        .INIT_RAM_2A({288{1'b0}}),
        .INIT_RAM_2B({288{1'b0}}),
        .INIT_RAM_2C({288{1'b0}}),
        .INIT_RAM_2D({288{1'b0}}),
        .INIT_RAM_2E({288{1'b0}}),
        .INIT_RAM_2F({288{1'b0}}),
        .INIT_RAM_30({288{1'b0}}),
        .INIT_RAM_31({288{1'b0}}),
        .INIT_RAM_32({288{1'b0}}),
        .INIT_RAM_33({288{1'b0}}),
        .INIT_RAM_34({288{1'b0}}),
        .INIT_RAM_35({288{1'b0}}),
        .INIT_RAM_36({288{1'b0}}),
        .INIT_RAM_37({288{1'b0}}),
        .INIT_RAM_38({288{1'b0}}),
        .INIT_RAM_39({288{1'b0}}),
        .INIT_RAM_3A({288{1'b0}}),
        .INIT_RAM_3B({288{1'b0}}),
        .INIT_RAM_3C({288{1'b0}}),
        .INIT_RAM_3D({288{1'b0}}),
        .INIT_RAM_3E({288{1'b0}}),
        .INIT_RAM_3F({288{1'b0}})
    ) u_bloque (
        .BLKSELA(3'b000), .BLKSELB(3'b000),
        .CLKA(clk), .CEA(1'b1), .WREA(we), .RESETA(1'b0), .OCEA(1'b1),
        .ADA({dir_w, 2'b00, 2'b11}), .DIA(dato_w), .DOA(),
        .CLKB(clk), .CEB(1'b1), .WREB(1'b0), .RESETB(1'b0), .OCEB(1'b1),
        .ADB({dir_r, 2'b00, 2'b00}), .DIB(18'd0), .DOB(dato_r)
    );
    /* verilator lint_on PINCONNECTEMPTY */
`endif
endmodule

`default_nettype wire
