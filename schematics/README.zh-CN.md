<!-- i18n: fuente=schematics/README.md sha=ab59ae6ef9d2 estado=al_dia -->
<!-- GENERADO por scripts/esquematicos.py. No se edita a mano. -->

# RTL 原理图

`rtl/` 中每个模块一个 PDF，采用电子电路符号。由 Yosys 和 netlistsvg 从 Verilog
生成，不手工绘制（ADR 0012，西班牙语）。

## 阅读方法

- **带 `+`、`-`、`*`、`<`、`==` 的梯形：** 加法器、减法器、乘法器或比较器。
- **有多个输入和一个选择端的梯形：** 多路选择器（`$mux`、`$pmux`）。
- **时钟端带三角形的矩形：** 触发器或寄存器（`$dff`、`$adff`、`$sdff`）。
- **与门、或门、异或门和非门：** 单比特逻辑，使用标准符号。
- **带模块名的矩形：** 子模块，有自己的 PDF。
- **左右两侧的箭头：** 模块的输入与输出端口。

大型模块（`nucleo`、`tabla_hermite`）有数百个单元。PDF 为矢量图，
放大后细节不会丢失。

## 重新生成

1. 安装一次 netlistsvg：`cd herramientas/esquematicos && npm install`。
2. 运行 `.venv/bin/python scripts/esquematicos.py`，只会重新生成有变化的原理图。
3. `--comprobar` 列出已过时的原理图。

## 索引

PDF 的标题栏和本表中的说明来自 Verilog 注释，为西班牙语。

| PDF | 源文件 | 源文件 sha256 | 说明 |
|---|---|---|---|
| `comun/carga_programa.pdf` | `rtl/comun/carga_programa.v` | `c801d0fd99bf` | Copia un programa desde una ROM (rtl/top/programa_*.v, generada por `sofifi tablas`) al microcódigo del núcleo por su puerto de programa. |
| `comun/generador_muestra.pdf` | `rtl/comun/generador_muestra.v` | `a4f2b8933bc9` | Reloj de muestra del núcleo (ADR 0005): un pulso `tick` cada 2 048 ciclos de 100 MHz, es decir 48 828,125 Hz exactos. |
| `comun/linea_hex.pdf` | `rtl/comun/linea_hex.v` | `2e3b405a5561` | Envía por la UART una línea "<etiqueta> <valor en hexadecimal>\r\n". |
| `comun/medidor_frecuencia.pdf` | `rtl/comun/medidor_frecuencia.v` | `e89ffa766328` | Cuenta los ciclos de `clk_medido` durante VENTANA ciclos de `clk_ref`. |
| `comun/uart_rx.pdf` | `rtl/comun/uart_rx.v` | `1c5ee2369bc9` | UART de recepción 8N1. |
| `comun/uart_tx.pdf` | `rtl/comun/uart_tx.v` | `626d9ea2c7eb` | UART de transmisión 8N1. |
| `nucleo/acc_a_dato.pdf` | `rtl/nucleo/acc_a_dato.v` | `d80ed023b685` | Conversión de formato del núcleo (ADR 0008), equivalente bit a bit a la función del mismo nombre de model/sofifi/domain/aritmetica.py. |
| `nucleo/alu.pdf` | `rtl/nucleo/alu.v` | `0ba8091f49b7` | Paso final de cada instrucción: combina el producto `p` del multiplicador con el ACC y los operandos, y satura a 48 bit. |
| `nucleo/curva_fin.pdf` | `rtl/nucleo/curva_fin.v` | `df4d9eb69467` | Último paso de curva_suave (model/sofifi/domain/aritmetica.py): |
| `nucleo/dato_a_memoria.pdf` | `rtl/nucleo/dato_a_memoria.v` | `732fb2f92662` | Conversión de formato del núcleo (ADR 0008), equivalente bit a bit a la función del mismo nombre de model/sofifi/domain/aritmetica.py. |
| `nucleo/lfo_banco.pdf` | `rtl/nucleo/lfo_banco.v` | `30d5511ea6c1` | Los 4 LFO del núcleo (ADR 0008). |
| `nucleo/memoria_retardo.pdf` | `rtl/nucleo/memoria_retardo.v` | `3aba7824aecb` | Memoria de retardo circular del núcleo, como la del FV-1 (ADR 0004, ADR 0008). |
| `nucleo/nucleo.pdf` | `rtl/nucleo/nucleo.v` | `c91b56e1a904` | Núcleo DSP microcodificado de SOFIFI (ADR 0006, ADR 0009). |
| `nucleo/saturar_acc.pdf` | `rtl/nucleo/saturar_acc.v` | `057dc6597c8e` | Conversión de formato del núcleo (ADR 0008), equivalente bit a bit a la función del mismo nombre de model/sofifi/domain/aritmetica.py. |
| `nucleo/tabla_hermite.pdf` | `rtl/nucleo/tabla_hermite.v` | `9c8e264fc727` | GENERADO por `sofifi tablas` desde model/sofifi/domain/interpolacion.py. |
| `primitivas/bsram_bloque.pdf` | `rtl/primitivas/bsram_bloque.v` | `12e5a5b6e720` | Un bloque de BSRAM del GW5A en modo 1K × 18: escritura por el puerto A y lectura por el B, con el registro de salida interno del bloque (READ_MODE1 = 1). |
| `primitivas/bsram_dp.pdf` | `rtl/primitivas/bsram_dp.v` | `a9fca00de987` | Memoria de doble puerto: un puerto de escritura y uno de lectura, en el mismo reloj. |
| `primitivas/bsram_pipe.pdf` | `rtl/primitivas/bsram_pipe.v` | `0345336f3310` | Memoria de un puerto de escritura y uno de lectura hecha con bloques bsram_bloque (1K × 18, salida registrada dentro del bloque). |
| `primitivas/mult_27x18.pdf` | `rtl/primitivas/mult_27x18.v` | `857579f75a6e` | Multiplicador con signo de 27 × 18 bit, con latencia de 2 ciclos: registra las entradas y la salida. |
| `primitivas/mult_27x36.pdf` | `rtl/primitivas/mult_27x36.v` | `ba029281dcb5` | Multiplicador con signo de 27 × 36 bit, con latencia de 3 ciclos: registra las entradas, el producto (PREG) y la salida. |
| `primitivas/pll_100.pdf` | `rtl/primitivas/pll_100.v` | `35ddf86070ba` | Reloj de 100 MHz desde el cristal de 50 MHz de la Tang Primer 25K. |
| `primitivas/registro_copia.pdf` | `rtl/primitivas/registro_copia.v` | `25ea9c5a2455` | Registro de ANCHO bit que Yosys no fusiona con otro igual. |
| `top/hil_nucleo.pdf` | `rtl/top/hil_nucleo.v` | `eef64a16c1bd` | Verificación del núcleo en la placa (Fase 05, hardware-in-the-loop). |
| `top/hola_uart.pdf` | `rtl/top/hola_uart.v` | `2f54c9b1fe9f` | Primer bitstream (Fase 02): envía "SOFIFI xxxxxxxx\r\n" una vez por segundo por la UART del depurador BL616 (115 200 8N1), con un contador en hexadecimal. |
| `top/nucleo_placa.pdf` | `rtl/top/nucleo_placa.v` | `932e448b33e6` | El núcleo en la placa (Fase 04): PLL de 100 MHz, una muestra cada 2 048 ciclos (48 828,125 Hz, ADR 0005) y el plate cargado desde ROM por el puerto de programa, como hará la microSD (Fase 08). |
| `top/programa_plate.pdf` | `rtl/top/programa_plate.v` | `00a808f53503` | GENERADO por `sofifi tablas` desde programas/plate.sasm. |
| `top/prueba_bsram.pdf` | `rtl/top/prueba_bsram.v` | `c11b70757e05` | Prueba de la BSRAM (Fase 03), a 100 MHz, con el tamaño real de la memoria de retardo del núcleo: 43 008 palabras de 18 bit (42 bloques). |
| `top/prueba_dsp.pdf` | `rtl/top/prueba_dsp.v` | `7b3c63e1485e` | Prueba del bloque DSP (Fase 03), a 100 MHz. |
| `top/prueba_fs.pdf` | `rtl/top/prueba_fs.v` | `248cc3ad6edb` | Prueba del reloj de muestra y de la recepción UART (Fase 05), a 100 MHz: |
| `top/prueba_pll.pdf` | `rtl/top/prueba_pll.v` | `26730b4db73b` | Prueba del PLL (Fase 03). |
