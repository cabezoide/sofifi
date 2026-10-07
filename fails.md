# Fallos y su resolución

Registro de los fallos encontrados en el proyecto. Cada uno tiene síntoma, diagnóstico, causa raíz, resolución y lección. Sirve para no repetirlos y para entender por qué el diseño es como es.

Se añade una entrada nueva cuando un fallo está diagnosticado y resuelto. Las entradas no se reescriben: si algo cambia después, se añade una nota con la fecha.

| ID | Fase | Fallo | Estado |
|---|---|---|---|
| F-01 | 02 | El envoltorio de verilator se lanzaba a sí mismo y tumbaba la máquina | resuelto |
| F-02 | 03 | El puente UART del BL616 se cuelga | resuelto (con regla de uso) |
| F-03 | 03 | apicula 0.32 no empaqueta un PLLA con divisores por defecto | resuelto |
| F-04 | 03 | Yosys no infiere bloques DSP para el GW5A | resuelto |
| F-05 | 03 | nextpnr no deduce la frecuencia de salida del PLL | resuelto |
| F-06 | 03 | En simulación el reset no llegaba nunca | resuelto |
| F-07 | 02 | El primer bitstream gastaba el doble de lógica | resuelto |
| F-08 | 04 | Desplazamientos sin signo y un desbordamiento en el RTL | resuelto |
| F-09 | 04 | Violaciones de hold en las BSRAM de un solo puerto | resuelto |
| F-10 | 04 | El núcleo no cerraba timing (70 MHz) | resuelto |
| F-11 | 05 | El silicio fallaba a 100 MHz aunque nextpnr daba 132 | resuelto; margen medido ≥ 6 %, a subir |
| F-12 | 05 | Una prueba del borrado de memoria no detectaba nada | resuelto |
| F-13 | 05 | La primera línea del volcado se perdía | resuelto |
| F-14 | 05 | apicula 0.32 no empaqueta BSRAM sin contenido inicial | resuelto |

---

## F-01 · El envoltorio de verilator se lanzaba a sí mismo

- **Síntoma:** la máquina de desarrollo se colgó dos veces. El kernel mataba procesos por falta de memoria (OOM).
- **Diagnóstico:** en el volcado del OOM había unos 14 000 procesos `verilator`.
- **Causa raíz:** se creó a mano el enlace `.venv/bin/verilator -> verilator-cli`. El envoltorio de pip busca `verilator` en PATH y lo ejecuta. Con el enlace, se encontraba a sí mismo y se relanzaba sin fin.
- **Resolución:** sin enlace. `sim/conftest.py` y `scripts/ci_local.sh` llaman al binario real del paquete con `VERILATOR_ROOT`. La compuerta ejecuta las herramientas EDA bajo `ulimit -u`.
- **Lección:** al probar una herramienta nueva que lanza subprocesos, hacerlo con `ulimit -u` y `timeout`.

## F-02 · El puente UART del BL616 se cuelga

- **Síntoma:** la placa deja de enviar datos al PC, con cualquier bitstream, hasta reconectar el USB. La FPGA sí se configura (openFPGALoader informa `Done Final`).
- **Diagnóstico:** se probó con siete reconexiones a lo largo de las fases 03 y 05. En la Fase 03 parecía un fallo de la BSRAM. En la Fase 05 el patrón quedó claro:

  | Situación | Resultado |
  |---|---|
  | La FPGA envía a caudal alto y el PC lee sin parar (volcados del HIL, 11,5 kB/s) | no se cuelga |
  | Se reprograma la FPGA mientras envía ≥ 2 kB/s (el PC no lee durante el JTAG) | se cuelga |
  | Se reprograma mientras envía ~1,4 kB/s o menos | sobrevive |

- **Causa raíz:** el firmware del BL616 no soporta que se acumulen bytes sin leer mientras atiende otra cosa, en particular durante la programación por JTAG. No está en nuestras manos.
- **Resolución:**
  - los tops de prueba limitan su caudal (unos 300 B/s a 1,4 kB/s);
  - el HIL solo vuelca cuando el PC lo pide;
  - los scripts cargan un diseño silencioso (`prueba_pll`) **antes** de soltar el puerto.
- **Lección:** antes de reprogramar, la FPGA no debe estar enviando a caudal alto. Si lo está, leer el puerto mientras se programa.

## F-03 · apicula 0.32 no empaqueta un PLLA con divisores por defecto

- **Síntoma:** `gowin_pack` termina con `invalid literal for int() with base 2: '8'`.
- **Causa raíz:** apicula guarda en decimal los valores por defecto del PLLA y los lee como binario.
- **Resolución:** `rtl/primitivas/pll_100.v` fija todos los divisores, también los de las salidas sin usar.

## F-04 · Yosys no infiere bloques DSP para el GW5A

- **Síntoma:** un `a * b` acababa en LUT y ALU.
- **Causa raíz:** Yosys 0.69 solo infiere DSP para las familias gw1n y gw2a.
- **Resolución:** se instancia `MULT27X36` en `rtl/primitivas/mult_27x36.v`. Ocupa 2 de los 28 bloques DSP. Verificado en la placa hasta 160 MHz.

## F-05 · nextpnr no deduce la frecuencia de salida del PLL

- **Síntoma:** el informe aplicaba a `clk_100` el objetivo genérico de 50 MHz.
- **Resolución:** `scripts/fpga.sh` pone 100 MHz de objetivo a todos los relojes.

## F-06 · En simulación el reset no llegaba nunca

- **Síntoma:** un top de prueba enviaba basura en simulación.
- **Causa raíz:** verilator arranca los registros a 0. Con el PLL simulado, `bloqueado` vale 1 desde el principio y el reset derivado de él no se activa nunca.
- **Resolución:** un contador de arranque propio en cada dominio de reloj.

## F-07 · El primer bitstream gastaba el doble de lógica

- **Síntoma:** `hola_uart` ocupaba 353 LUT4 y 146 ALU. La persona propietaria preguntó si era normal.
- **Causa raíz:** convertía a ASCII los 8 dígitos del contador en paralelo y después elegía uno.
- **Resolución:** se elige primero el dígito y se convierte una vez: 207 LUT4 y 82 ALU. De aquí nació la segunda vuelta de optimización (ADR 0010).

## F-08 · Desplazamientos sin signo y un desbordamiento en el RTL

- **Síntoma:** pruebas unitarias contra el modelo que fallaban mientras las de los programas pasaban.
- **Causa raíz:** en Verilog, una selección de bits (`p[49:0]`) y una concatenación (`{...}`) son **sin signo**, así que `>>>` hace un desplazamiento lógico. Pasó dos veces (en `curva_fin`). Además, en el LFO RND, `objetivo − actual` necesitaba 25 bit y se calculaba en 24.
- **Resolución:** pasar por un cable `signed` antes de desplazar; diferencia en 25 bit.
- **Lección:** cada bloque se prueba contra su función del modelo con miles de vectores aleatorios. Las pruebas de los programas solo cubren los valores que esos programas producen.

## F-09 · Violaciones de hold en las BSRAM de un solo puerto

- **Síntoma:** 104 violaciones de hold en la primera síntesis del núcleo.
- **Causa raíz:** Yosys llevaba las ROM (tabla Hermite, programa) y parte del microcódigo a BSRAM `SPX9`. En el GW5A, esas dan violaciones de hold; las `DPX9B` no.
- **Resolución:** ROM en lógica con `(* rom_style = "logic" *)` **en el `case`** (en el puerto no tiene efecto); el microcódigo, con un envoltorio de doble puerto.

## F-10 · El núcleo no cerraba timing (70 MHz)

- **Síntoma:** la primera síntesis del núcleo daba 70 MHz frente a 100.
- **Causa raíz:** en un solo ciclo se encadenaban la decodificación, el banco de registros (multiplexor 64:1), el redondeo de `a24` y `CLIP` (tres operaciones de 50 bit).
- **Resolución:** operandos registrados en la decodificación y `CLIP` en dos pasos: 140 MHz según nextpnr. No bastó en el silicio: ver F-11.

## F-11 · El silicio fallaba a 100 MHz aunque nextpnr daba 132

- **Síntoma:** en la placa, el plate salía con la primera muestra a la mitad. En simulación, en la síntesis y en el netlist sintetizado coincidía con el modelo.
- **Diagnóstico**, paso a paso:
  1. Se descartó el multiplicador con B de 24 bit: 300 productos sin error en la placa.
  2. Se descartó la BSRAM en modo 2K × 9: 0 errores en la placa.
  3. Se simuló el netlist de Yosys: coincidía con el modelo, así que la síntesis era correcta.
  4. Un programa mínimo con el mismo cálculo funcionaba en la placa. Dependía de la colocación.
  5. **Prueba decisiva:** se cambió solo el divisor del PLL en el JSON ya rutado, sin volver a colocar. A 50, 72,7, 80 y 88,9 MHz funcionaba; a 100 no. Era timing.
  6. Con el mismo método, el DSP funcionaba hasta 160 MHz y la BSRAM inferida fallaba por encima de 100, con 117 MHz de análisis estático.
- **Causa raíz:** el modelo de tiempos de nextpnr para el GW5A es optimista en torno a un 30 %. Sobre todo para la BSRAM en modo *bypass* (sin registro de salida), que es la única que infiere Yosys, y para la lógica que va detrás de ella.
- **Resolución:**
  - `rtl/primitivas/bsram_bloque.v`: BSRAM instanciada a mano con su registro de salida interno (`READ_MODE1 = 1`);
  - `rtl/primitivas/bsram_pipe.v`: memorias grandes hechas de esos bloques, con el multiplexor registrado;
  - la salida del multiplicador, registrada dos veces; la ALU, en dos etapas; la dirección del `CHO`, en tres pasos; el cargador del programa, registrado.
- **Resultado medido:** nextpnr da 155 MHz. En la placa: 9 de 9 capturas perfectas a 100 MHz, 3 de 3 a 106,25 MHz y 2 de 5 a 114,3 MHz. La frecuencia real máxima está entre 106 y 114 MHz: **margen de al menos un 6 %**. Es poco para un pedal que se calienta; el objetivo es superar el 20 % al rediseñar el secuenciador (antes de la Fase 06).
- **Coste:** los ciclos por muestra pasan de 661 a 1 258 (plate) y de 840 a 1 601 (shimmer), de 2 048.
- **Lección:** el análisis de nextpnr no basta. El margen se mide en la placa, cambiando solo el divisor del PLL sobre el mismo rutado (ADR 0011).

## F-12 · Una prueba del borrado de memoria no detectaba nada

- **Síntoma:** la prueba pasaba también con el borrado desactivado.
- **Causa raíz:** con las líneas largas del plate, los datos viejos tardan miles de muestras en volver a leerse.
- **Resolución:** un programa de 8 muestras de retardo sobre 9 palabras. Falla sin borrado y pasa con él.
- **Lección:** comprobar que cada prueba nueva falla cuando el código está mal.

## F-13 · La primera línea del volcado se perdía

- **Síntoma:** llegaban 4 095 muestras de 4 096 y todas quedaban corridas una posición.
- **Causa raíz:** el BL616 guarda bytes de un diseño anterior. `reset_input_buffer()` solo vacía el búfer del PC, y la primera línea llegaba pegada a esos restos.
- **Resolución:** `scripts/hil_nucleo.py` descarta lo que llega durante 0,3 s antes de pedir la captura.

## F-14 · apicula 0.32 no empaqueta BSRAM sin contenido inicial

- **Síntoma:** `gowin_pack` termina con `IndexError` en `write_gw5_bsram_init_map`, y deja un bitstream incompleto.
- **Causa raíz:** si ninguna BSRAM del diseño declara `INIT_RAM_xx`, apicula falla. Pasó al instanciar todos los bloques a mano.
- **Resolución:** `bsram_bloque.v` declara las 64 palabras de inicialización a cero.
- **Lección:** comprobar el código de salida de `fpga.sh`; un `.fs` puede existir aunque el empaquetado haya fallado.
