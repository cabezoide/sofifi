<!-- GENERADO por scripts/esquematicos.py. No se edita a mano. -->

# Esquemáticos del RTL

Un PDF por cada módulo de `rtl/`, en notación electrónica. Se generan desde el
Verilog con Yosys y netlistsvg; no se dibujan a mano (ADR 0012).

## Cómo se leen

- **Trapecio con `+`, `-`, `*`, `<`, `==`:** sumador, restador, multiplicador o comparador.
- **Trapecio con varias entradas y una selección:** multiplexor (`$mux`, `$pmux`).
- **Rectángulo con un triángulo en el reloj:** flip-flop o registro (`$dff`, `$adff`, `$sdff`).
- **Puertas AND, OR, XOR y NOT:** lógica de un bit, con sus símbolos estándar.
- **Rectángulo con un nombre de módulo:** un submódulo; tiene su propio PDF.
- **Flechas a izquierda y derecha:** puertos de entrada y de salida del módulo.

Los módulos grandes (`nucleo`, `tabla_hermite`) tienen cientos de celdas: el
PDF es vectorial y se puede ampliar sin perder detalle.

## Regenerar

1. Instalar netlistsvg una vez: `cd herramientas/esquematicos && npm install`.
2. Correr `.venv/bin/python scripts/esquematicos.py`. Solo regenera los que cambiaron.
3. `--comprobar` dice qué esquemáticos están desactualizados.

## Índice

| PDF | Fuente | sha256 de la fuente | Qué es |
|---|---|---|---|
| `comun/carga_programa.pdf` | `rtl/comun/carga_programa.v` | `c801d0fd99bf` | Copia un programa desde una ROM (rtl/top/programa_*.v, generada por `sofifi tablas`) al microcódigo del núcleo por su puerto de programa. |
| `comun/generador_muestra.pdf` | `rtl/comun/generador_muestra.v` | `a4f2b8933bc9` | Reloj de muestra del núcleo (ADR 0005): un pulso `tick` cada 2 048 ciclos de 100 MHz, es decir 48 828,125 Hz exactos. |
| `comun/linea_hex.pdf` | `rtl/comun/linea_hex.v` | `2e3b405a5561` | Envía por la UART una línea "<etiqueta> <valor en hexadecimal>\r\n". |
| `comun/medidor_frecuencia.pdf` | `rtl/comun/medidor_frecuencia.v` | `e89ffa766328` | Cuenta los ciclos de `clk_medido` durante VENTANA ciclos de `clk_ref`. |
| `comun/uart_rx.pdf` | `rtl/comun/uart_rx.v` | `1c5ee2369bc9` | UART de recepción 8N1. |
| `comun/uart_tx.pdf` | `rtl/comun/uart_tx.v` | `626d9ea2c7eb` | UART de transmisión 8N1. |
| `nucleo/acc_a_dato.pdf` | `rtl/nucleo/acc_a_dato.v` | `d80ed023b685` | Conversión de formato del núcleo (ADR 0008), equivalente bit a bit a la función del mismo nombre de model/sofifi/domain/aritmetica.py. |
| `nucleo/alu.pdf` | `rtl/nucleo/alu.v` | `57bb72ab17dc` | Paso final de cada instrucción: combina el producto `p` del multiplicador con el ACC y los operandos, y satura a 48 bit. |
| `nucleo/curva_fin.pdf` | `rtl/nucleo/curva_fin.v` | `df4d9eb69467` | Último paso de curva_suave (model/sofifi/domain/aritmetica.py): |
| `nucleo/dato_a_memoria.pdf` | `rtl/nucleo/dato_a_memoria.v` | `732fb2f92662` | Conversión de formato del núcleo (ADR 0008), equivalente bit a bit a la función del mismo nombre de model/sofifi/domain/aritmetica.py. |
| `nucleo/lfo_banco.pdf` | `rtl/nucleo/lfo_banco.v` | `30d5511ea6c1` | Los 4 LFO del núcleo (ADR 0008). |
| `nucleo/memoria_retardo.pdf` | `rtl/nucleo/memoria_retardo.v` | `cadf027b3f22` | Memoria de retardo circular del núcleo, como la del FV-1 (ADR 0004, ADR 0008). |
| `nucleo/nucleo.pdf` | `rtl/nucleo/nucleo.v` | `a7fe839f1c97` | Núcleo DSP microcodificado de SOFIFI (ADR 0006, ADR 0009). |
| `nucleo/saturar_acc.pdf` | `rtl/nucleo/saturar_acc.v` | `d074e4cb6976` | Conversión de formato del núcleo (ADR 0008), equivalente bit a bit a la función del mismo nombre de model/sofifi/domain/aritmetica.py. |
| `nucleo/tabla_hermite.pdf` | `rtl/nucleo/tabla_hermite.v` | `9c8e264fc727` | GENERADO por `sofifi tablas` desde model/sofifi/domain/interpolacion.py. |
| `primitivas/bsram_bloque.pdf` | `rtl/primitivas/bsram_bloque.v` | `12e5a5b6e720` | Un bloque de BSRAM del GW5A en modo 1K × 18: escritura por el puerto A y lectura por el B, con el registro de salida interno del bloque (READ_MODE1 = 1). |
| `primitivas/bsram_dp.pdf` | `rtl/primitivas/bsram_dp.v` | `a9fca00de987` | Memoria de doble puerto: un puerto de escritura y uno de lectura, en el mismo reloj. |
| `primitivas/bsram_pipe.pdf` | `rtl/primitivas/bsram_pipe.v` | `0345336f3310` | Memoria de un puerto de escritura y uno de lectura hecha con bloques bsram_bloque (1K × 18, salida registrada dentro del bloque). |
| `primitivas/mult_27x18.pdf` | `rtl/primitivas/mult_27x18.v` | `857579f75a6e` | Multiplicador con signo de 27 × 18 bit, con latencia de 2 ciclos: registra las entradas y la salida. |
| `primitivas/mult_27x36.pdf` | `rtl/primitivas/mult_27x36.v` | `ba029281dcb5` | Multiplicador con signo de 27 × 36 bit, con latencia de 3 ciclos: registra las entradas, el producto (PREG) y la salida. |
| `primitivas/pll_100.pdf` | `rtl/primitivas/pll_100.v` | `35ddf86070ba` | Reloj de 100 MHz desde el cristal de 50 MHz de la Tang Primer 25K. |
| `primitivas/registro_copia.pdf` | `rtl/primitivas/registro_copia.v` | `25ea9c5a2455` | Registro de ANCHO bit que Yosys no fusiona con otro igual. |
| `sd/carga_sd.pdf` | `rtl/sd/carga_sd.v` | `1f37570f1869` | Carga de programas desde la microSD (Fase 08): sd_spi.v + cargador.v. |
| `sd/cargador.pdf` | `rtl/sd/cargador.v` | `ecbc8170989f` | Cargador de programas desde el banco de la microSD (Fase 08). |
| `sd/sd_spi.pdf` | `rtl/sd/sd_spi.v` | `8b800e71e7cd` | Controlador de tarjeta SD en modo SPI (Fase 08, ADR 0004): arranque y lectura de bloques de 512 bytes. |
| `top/hil_looper.pdf` | `rtl/top/hil_looper.v` | `f9fa8bc14659` | hil_nucleo con el looper (Fase 07): prueba RDAA y WRAA en la placa. |
| `top/hil_nucleo.pdf` | `rtl/top/hil_nucleo.v` | `c17fa929291d` | Verificación del núcleo en la placa (Fase 05, hardware-in-the-loop). |
| `top/hil_programa.pdf` | `rtl/top/hil_programa.v` | `4140d4067240` | hil_nucleo con la ROM que escribe `sofifi rom` en build/programa_hil.v: un programa o una cadena cualquiera en la placa. |
| `top/hola_uart.pdf` | `rtl/top/hola_uart.v` | `2f54c9b1fe9f` | Primer bitstream (Fase 02): envía "SOFIFI xxxxxxxx\r\n" una vez por segundo por la UART del depurador BL616 (115 200 8N1), con un contador en hexadecimal. |
| `top/nucleo_placa.pdf` | `rtl/top/nucleo_placa.v` | `9cd658a3116b` | El núcleo en la placa (Fase 04): PLL de 100 MHz, una muestra cada 2 048 ciclos (48 828,125 Hz, ADR 0005) y el plate cargado desde ROM por el puerto de programa, como hará la microSD (Fase 08). |
| `top/programa_looper.pdf` | `rtl/top/programa_looper.v` | `3d6fc4abc5a3` | GENERADO por `sofifi tablas` desde programas/looper.sasm. |
| `top/programa_plate.pdf` | `rtl/top/programa_plate.v` | `c17f03ff244d` | GENERADO por `sofifi tablas` desde programas/plate.sasm. |
| `top/prueba_bsram.pdf` | `rtl/top/prueba_bsram.v` | `c11b70757e05` | Prueba de la BSRAM (Fase 03), a 100 MHz, con el tamaño real de la memoria de retardo del núcleo: 43 008 palabras de 18 bit (42 bloques). |
| `top/prueba_dsp.pdf` | `rtl/top/prueba_dsp.v` | `7b3c63e1485e` | Prueba del bloque DSP (Fase 03), a 100 MHz. |
| `top/prueba_fs.pdf` | `rtl/top/prueba_fs.v` | `248cc3ad6edb` | Prueba del reloj de muestra y de la recepción UART (Fase 05), a 100 MHz: |
| `top/prueba_pll.pdf` | `rtl/top/prueba_pll.v` | `26730b4db73b` | Prueba del PLL (Fase 03). |
| `top/prueba_sd.pdf` | `rtl/top/prueba_sd.v` | `5915aec54e2a` | Prueba de la microSD en la placa (Fase 08): arranca la tarjeta del Sipeed PMOD TF en el conector J6 del Dock y carga ranuras del banco de `sofifi banco`. |
| `top/prueba_sd_logica.pdf` | `rtl/top/prueba_sd_logica.v` | `892b765090ff` | Lógica de rtl/top/prueba_sd.v (protocolo y órdenes, allí), sin PLL ni pines triestado: es lo que simula sim/top/prueba_sd_test.py con el modelo de tarjeta. |
