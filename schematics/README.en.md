<!-- i18n: fuente=schematics/README.md sha=262861445cdc estado=al_dia -->
<!-- GENERADO por scripts/esquematicos.py. No se edita a mano. -->

# RTL schematics

One PDF for each module in `rtl/`, in electronic notation. Yosys and netlistsvg
generate them from the Verilog; nobody draws them by hand (ADR 0012, Spanish).

## How to read them

- **Trapezoid with `+`, `-`, `*`, `<`, `==`:** adder, subtractor, multiplier or comparator.
- **Trapezoid with several inputs and one select:** multiplexer (`$mux`, `$pmux`).
- **Rectangle with a triangle on the clock:** flip-flop or register (`$dff`, `$adff`, `$sdff`).
- **AND, OR, XOR and NOT gates:** one-bit logic, with their standard symbols.
- **Rectangle with a module name:** a submodule; it has its own PDF.
- **Arrows on the left and on the right:** input and output ports of the module.

The large modules (`nucleo`, `tabla_hermite`) have hundreds of cells. The PDF is
vector graphics: you can zoom in and keep all the detail.

## Generate them again

1. Install netlistsvg one time: `cd herramientas/esquematicos && npm install`.
2. Run `.venv/bin/python scripts/esquematicos.py`. It generates only the changed ones.
3. `--comprobar` tells which schematics are out of date.

## Index

The PDF title blocks and the descriptions in this table come from the Verilog comments, in Spanish.

| PDF | Source | sha256 of the source | What it is |
|---|---|---|---|
| `comun/carga_programa.pdf` | `rtl/comun/carga_programa.v` | `c801d0fd99bf` | Copia un programa desde una ROM (rtl/top/programa_*.v, generada por `sofifi tablas`) al microcódigo del núcleo por su puerto de programa. |
| `comun/generador_muestra.pdf` | `rtl/comun/generador_muestra.v` | `a4f2b8933bc9` | Reloj de muestra del núcleo (ADR 0005): un pulso `tick` cada 2 048 ciclos de 100 MHz, es decir 48 828,125 Hz exactos. |
| `comun/linea_hex.pdf` | `rtl/comun/linea_hex.v` | `2e3b405a5561` | Envía por la UART una línea "<etiqueta> <valor en hexadecimal>\r\n". |
| `comun/medidor_frecuencia.pdf` | `rtl/comun/medidor_frecuencia.v` | `e89ffa766328` | Cuenta los ciclos de `clk_medido` durante VENTANA ciclos de `clk_ref`. |
| `comun/uart_rx.pdf` | `rtl/comun/uart_rx.v` | `1c5ee2369bc9` | UART de recepción 8N1. |
| `comun/uart_tx.pdf` | `rtl/comun/uart_tx.v` | `626d9ea2c7eb` | UART de transmisión 8N1. |
| `nucleo/acc_a_dato.pdf` | `rtl/nucleo/acc_a_dato.v` | `d80ed023b685` | Conversión de formato del núcleo (ADR 0008), equivalente bit a bit a la función del mismo nombre de model/sofifi/domain/aritmetica.py. |
| `nucleo/alu.pdf` | `rtl/nucleo/alu.v` | `aaa491519065` | Paso final de cada instrucción: combina el producto `p` del multiplicador con el ACC y los operandos, y satura a 48 bit. |
| `nucleo/curva_fin.pdf` | `rtl/nucleo/curva_fin.v` | `df4d9eb69467` | Último paso de curva_suave (model/sofifi/domain/aritmetica.py): |
| `nucleo/dato_a_memoria.pdf` | `rtl/nucleo/dato_a_memoria.v` | `732fb2f92662` | Conversión de formato del núcleo (ADR 0008), equivalente bit a bit a la función del mismo nombre de model/sofifi/domain/aritmetica.py. |
| `nucleo/lfo_banco.pdf` | `rtl/nucleo/lfo_banco.v` | `30d5511ea6c1` | Los 4 LFO del núcleo (ADR 0008). |
| `nucleo/memoria_retardo.pdf` | `rtl/nucleo/memoria_retardo.v` | `cadf027b3f22` | Memoria de retardo circular del núcleo, como la del FV-1 (ADR 0004, ADR 0008). |
| `nucleo/nucleo.pdf` | `rtl/nucleo/nucleo.v` | `c2d571d2a2b5` | Núcleo DSP microcodificado de SOFIFI (ADR 0006, ADR 0009). |
| `nucleo/saturar_acc.pdf` | `rtl/nucleo/saturar_acc.v` | `057dc6597c8e` | Conversión de formato del núcleo (ADR 0008), equivalente bit a bit a la función del mismo nombre de model/sofifi/domain/aritmetica.py. |
| `nucleo/tabla_hermite.pdf` | `rtl/nucleo/tabla_hermite.v` | `9c8e264fc727` | GENERADO por `sofifi tablas` desde model/sofifi/domain/interpolacion.py. |
| `primitivas/bsram_bloque.pdf` | `rtl/primitivas/bsram_bloque.v` | `12e5a5b6e720` | Un bloque de BSRAM del GW5A en modo 1K × 18: escritura por el puerto A y lectura por el B, con el registro de salida interno del bloque (READ_MODE1 = 1). |
| `primitivas/bsram_dp.pdf` | `rtl/primitivas/bsram_dp.v` | `a9fca00de987` | Memoria de doble puerto: un puerto de escritura y uno de lectura, en el mismo reloj. |
| `primitivas/bsram_pipe.pdf` | `rtl/primitivas/bsram_pipe.v` | `0345336f3310` | Memoria de un puerto de escritura y uno de lectura hecha con bloques bsram_bloque (1K × 18, salida registrada dentro del bloque). |
| `primitivas/mult_27x18.pdf` | `rtl/primitivas/mult_27x18.v` | `857579f75a6e` | Multiplicador con signo de 27 × 18 bit, con latencia de 2 ciclos: registra las entradas y la salida. |
| `primitivas/mult_27x36.pdf` | `rtl/primitivas/mult_27x36.v` | `ba029281dcb5` | Multiplicador con signo de 27 × 36 bit, con latencia de 3 ciclos: registra las entradas, el producto (PREG) y la salida. |
| `primitivas/pll_100.pdf` | `rtl/primitivas/pll_100.v` | `35ddf86070ba` | Reloj de 100 MHz desde el cristal de 50 MHz de la Tang Primer 25K. |
| `primitivas/registro_copia.pdf` | `rtl/primitivas/registro_copia.v` | `25ea9c5a2455` | Registro de ANCHO bit que Yosys no fusiona con otro igual. |
| `top/hil_looper.pdf` | `rtl/top/hil_looper.v` | `f9fa8bc14659` | hil_nucleo con el looper (Fase 07): prueba RDAA y WRAA en la placa. |
| `top/hil_nucleo.pdf` | `rtl/top/hil_nucleo.v` | `c59c4d78085c` | Verificación del núcleo en la placa (Fase 05, hardware-in-the-loop). |
| `top/hola_uart.pdf` | `rtl/top/hola_uart.v` | `2f54c9b1fe9f` | Primer bitstream (Fase 02): envía "SOFIFI xxxxxxxx\r\n" una vez por segundo por la UART del depurador BL616 (115 200 8N1), con un contador en hexadecimal. |
| `top/nucleo_placa.pdf` | `rtl/top/nucleo_placa.v` | `9cd658a3116b` | El núcleo en la placa (Fase 04): PLL de 100 MHz, una muestra cada 2 048 ciclos (48 828,125 Hz, ADR 0005) y el plate cargado desde ROM por el puerto de programa, como hará la microSD (Fase 08). |
| `top/programa_looper.pdf` | `rtl/top/programa_looper.v` | `3d6fc4abc5a3` | GENERADO por `sofifi tablas` desde programas/looper.sasm. |
| `top/programa_plate.pdf` | `rtl/top/programa_plate.v` | `c17f03ff244d` | GENERADO por `sofifi tablas` desde programas/plate.sasm. |
| `top/prueba_bsram.pdf` | `rtl/top/prueba_bsram.v` | `c11b70757e05` | Prueba de la BSRAM (Fase 03), a 100 MHz, con el tamaño real de la memoria de retardo del núcleo: 43 008 palabras de 18 bit (42 bloques). |
| `top/prueba_dsp.pdf` | `rtl/top/prueba_dsp.v` | `7b3c63e1485e` | Prueba del bloque DSP (Fase 03), a 100 MHz. |
| `top/prueba_fs.pdf` | `rtl/top/prueba_fs.v` | `248cc3ad6edb` | Prueba del reloj de muestra y de la recepción UART (Fase 05), a 100 MHz: |
| `top/prueba_pll.pdf` | `rtl/top/prueba_pll.v` | `26730b4db73b` | Prueba del PLL (Fase 03). |
