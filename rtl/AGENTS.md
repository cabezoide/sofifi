# rtl/AGENTS.md — Verilog sintetizable (tiene precedencia en esta carpeta)

Vacío en la versión 0.0. Las reglas se escriben antes que el código.

## Reglas

- **Verilog-2005, o el subconjunto de SystemVerilog que aceptan a la vez Gowin
  EDA y Yosys.** Si una construcción solo la acepta una de las dos herramientas,
  no entra.
- **Un solo dominio de reloj para el audio** (100 MHz; ADR 0005). Los cruces de
  dominio (por ejemplo, con la SD) usan FIFOs asíncronas y se declaran en el
  módulo.
- **Ningún bloque DSP sin modelo** en `model/` y sin testbench de comparación en
  `sim/` (ADR 0003).
- **Cabecera SPDX** en cada fichero; lo portado se declara en `docs/terceros.yaml`.
- **Primitivas Gowin** (BSRAM, DSP, PLL) siempre detrás de un envoltorio propio,
  para poder simular y para portar a otra FPGA.

## Trampas

- apicula tiene un issue abierto con la PLLA del GW5A-25 (#427). Hay que verificar
  la frecuencia real con un contador antes de fiarse del reloj. `rtl/top/prueba_pll.v` lo
  hace (Fase 03).
- **apicula 0.32 falla al empaquetar un PLLA con parámetros por defecto.** Guarda los
  valores por defecto en decimal y los lee como binario («invalid literal for int()
  with base 2: '8'»). `rtl/primitivas/pll_100.v` fija todos los divisores, también los de las
  salidas sin usar.
- **Yosys no infiere bloques DSP para la familia gw5a** (solo para gw1n y gw2a). Un
  `a * b` acaba en LUT y ALU. Hay que instanciar el bloque detrás de un envoltorio:
  `rtl/primitivas/mult_27x18.v`. `MULT27X36` ocupa 2 de los 28 bloques DSP.
- **La BSRAM sí se infiere** (`rtl/primitivas/bsram_dp.v` → `DPX9B`).
- **nextpnr no deduce la frecuencia de salida del PLL.** `scripts/fpga.sh` pone
  100 MHz de objetivo a todos los relojes (ADR 0005).
- **Las primitivas tienen dos ramas.** Con `SIMULACION` definido se usa un modelo de
  comportamiento; sin él, la primitiva Gowin. `rtl-lint` y los testbenches definen
  `SIMULACION`; la rama de síntesis la comprueba el trabajo `optimizacion`.
- **El puente UART del BL616 se cuelga si la FPGA envía a pleno caudal y el PC deja
  de leer.** Después no pasa ni un byte, con ningún bitstream, hasta reconectar el
  USB. La FPGA sí se configura (openFPGALoader informa `Done Final`). Los tops de
  prueba limitan el caudal: unos 1,4 kB/s la DSP y 300 B/s la BSRAM (Fase 03).
- **apicula 0.32 deja el CE de los flip-flops sin CE como «señal»** (corregido en
  apicula 0.33, PR #501). En la Fase 03 no causó fallos, pero nextpnr 0.11.1 exige
  apicula 0.32. Si un diseño funciona en simulación y no en la placa, probar
  `synth_gowin -strict-gw5a-dffs`.
- **Las BSRAM `SPX9` (un solo puerto) dan violaciones de hold en el GW5A**; las
  `DPX9B` no. Las memorias van con `rtl/primitivas/bsram_dp.v`, y las ROM con
  `(* rom_style = "logic" *)` **en el `case`** (en el puerto no tiene efecto).
- **En Verilog, una selección de bits (`p[49:0]`) y una concatenación (`{...}`)
  son sin signo**, y `>>>` sobre ellas es lógico. Pasar por un cable `signed` antes
  de desplazar. Dos fallos de este tipo los encontraron las pruebas unitarias,
  no las de los programas.
- **La BSRAM en modo bypass es mucho más lenta de lo que dice nextpnr** (fails.md,
  F-11). Ninguna salida de BSRAM va a lógica en el mismo ciclo: usar
  `rtl/primitivas/bsram_pipe.v`, con el registro de salida del bloque. `bsram_dp`
  queda para pruebas.
- **apicula 0.32 no empaqueta si ninguna BSRAM declara `INIT_RAM_xx`** (F-14):
  `rtl/primitivas/bsram_bloque.v` las declara a cero.
- **El timing se mide en la placa** (ADR 0011): `scripts/margen_reloj.py`. nextpnr
  es optimista en un factor de 1,45 a 1,5. Si falla, `--traza` dice qué instrucción.
- **Memorias de medio chip, segmentadas** (F-15): `bsram_pipe` con `GRUPO`. Para
  repartir una señal en copias, `rtl/primitivas/registro_copia.v`: Yosys fusiona
  registros iguales aunque lleven `keep` en el `reg`.
- **Reset de arranque en cada dominio de reloj.** Verilator arranca los registros a
  0, y con el PLL simulado `bloqueado` vale 1 desde el principio: sin un contador de
  arranque, el reset no llega nunca en simulación.
- Al usar BSRAM en modo 2K×9 hay que tener en cuenta que el bit 9 viene en otro
  bus.
