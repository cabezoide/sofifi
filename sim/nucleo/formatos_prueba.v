// SPDX-License-Identifier: MIT
// Envoltorio de prueba: expone a la vez las tres conversiones de formatos.v.
`default_nettype none
module formatos_prueba (
    input  wire signed [47:0] acc,
    input  wire signed [23:0] dato,
    input  wire signed [49:0] valor,
    output wire signed [23:0] acc_dato,
    output wire signed [17:0] palabra,
    output wire signed [47:0] acc_sat
);
    acc_a_dato     u_a (.acc(acc), .dato(acc_dato));
    dato_a_memoria u_m (.dato(dato), .palabra(palabra));
    saturar_acc    u_s (.valor(valor), .acc(acc_sat));
endmodule
`default_nettype wire
