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
| F-15 | 06 | La lectura adelantada funcionaba en simulación y fallaba en el silicio a 100 MHz | resuelto; margen medido ≥ 20 % |
| F-16 | 06 | Las simulaciones grandes no compilaban con el verilator de pip | resuelto |
| F-17 | 06 | El difusor de velvet noise no superó a los allpass | descartado: no se publica |
| F-18 | 06 | Cuatro fallos de programación del catálogo | resueltos antes de publicar |
| F-19 | 07 | Con RDAA y WRAA, el silicio fallaba a 114 MHz en la primera muestra | resuelto; margen medido ≥ 25 % |
| F-20 | 07 | El borrado de la región absoluta dejaba dos palabras sin borrar | resuelto |
| F-21 | 07 | En marea, el LFO de software se quedaba pegado en +1 | resuelto antes de publicar |
| F-22 | 07 | El shoegaze sonaba cinco veces más fuerte que el plate | resuelto antes de publicar |
| F-23 | 07 | Una cadena con saturación sonaba seis veces más fuerte que el plate | resuelto antes de publicar |
| F-24 | 07 | La cola del microcódigo se llevó la última BSRAM | resuelto |
| F-25 | 08 | Tres fallos del controlador SD, encontrados en simulación | resuelto antes de la placa |
| F-26 | 08 | Cuatro trampas del punto fijo en el lote 9 del catálogo | resuelto antes de publicar |
| F-27 | 08 | Constantes pequeñas, bucles de control y una huella ciega en el lote 10 | resuelto antes de publicar |
| F-28 | 08 | La velocidad mínima de phaser y filtro era 0, y tres trampas del lote 11 | resuelto |
| F-29 | 08 | Cinco trampas de modulación y de nivel en el lote 12 | resuelto antes de publicar |
| F-30 | 08 | Detectores, costuras y límites de lectura en el lote 13 | resuelto antes de publicar |

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
- **Causa raíz:** cuatro pasos se encadenaban en un solo ciclo:
  - la decodificación;
  - el banco de registros (multiplexor 64:1);
  - el redondeo de `a24`;
  - `CLIP` (tres operaciones de 50 bit).
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
- **Causa raíz:** el modelo de tiempos de nextpnr para el GW5A es optimista en torno a un 30 %. Lo es sobre todo con la BSRAM en modo *bypass* (sin registro de salida), la única que infiere Yosys. También con la lógica que va detrás de ella.
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

## F-15 · La lectura adelantada fallaba en el silicio a 100 MHz

- **Síntoma:** con la lectura adelantada del microcódigo, el plate coincidía con el modelo en simulación. En la placa fallaba a 100 MHz, siempre desde la muestra 924. Con el mismo rutado funcionaba a 88,9 MHz y por debajo. nextpnr daba 157 MHz.
- **Diagnóstico**, paso a paso:
  1. El diseño de `main` seguía pasando a 100 MHz el mismo día: la placa no había cambiado.
  2. Las medidas en la placa descartaron la cadena de acarreo de 50 bit, la suma con saturación, la BSRAM sola, el DSP y el rutado del reloj. La opción `-nodffe` de Yosys no tiene efecto en el GW5A.
  3. La muestra 924 es aquella en la que la cola del plate llega a las tomas largas de la memoria: ahí la memoria empieza a devolver valores distintos de cero. Por eso el fallo «dependía de los datos».
  4. **Herramienta nueva:** el top `hil_nucleo` graba la traza del núcleo (orden `T`): el pc y el ACC en cada cambio del ACC. `scripts/margen_reloj.py --traza` la compara con el modelo y dice qué instrucción falla primero.
  5. Con la traza, cada rutado fallaba en un sitio distinto. Fallaban la lectura de la memoria de retardo (`RDA` devolvía 0: una dirección mal), la suma de la ALU (bit 25) y el multiplicador (`MULX`).
  6. Las cadenas de acarreo estaban colocadas sin cortes. No había un camino roto.
- **Causa raíz:** nextpnr sobrestima la velocidad de **todo** el diseño en el GW5A, en un factor de 1,45 a 1,5. Cada rutado falla en el camino que queda más justo. Los caminos de la BSRAM son los peores: una dirección que llega en un ciclo a 38 bloques repartidos por el chip, y un multiplexor de 38 salidas.
- **Resolución:**
  - `bsram_pipe` segmentada (`GRUPO = 8` en la memoria de retardo):
    - una copia de la dirección por grupo y por bloque (`registro_copia`, que Yosys no fusiona);
    - la salida de cada bloque, registrada a su lado;
    - multiplexores registrados por grupo.
  - La lectura pasa de 3 a 7 ciclos. El núcleo espera `LAT_MEM = 9` solo en `RDA` y `CHO`.
  - Banco de registros en dos niveles: 8 candidatos registrados en cada ciclo y la elección en `E_DECO`. La palabra del microcódigo se registra otra vez antes de decodificar.
  - Dirección física de la memoria con tres sumas en paralelo, y `puntero ± P` que bajan con el puntero.
  - El multiplicador usa el registro interno `PREG` del DSP.
- **Resultado medido** (nextpnr da 154 MHz para este rutado): 100 MHz, 4 de 4; 114,3 MHz, 2 de 2; **120 MHz, 4 de 4**; 125 MHz, 3 de 4; 133,3 MHz, 0 de 1. **Margen de al menos un 20 %**, frente al 6 % de la Fase 05.
- **Coste:** unos 3 100 flip-flops más (LUT4 en el informe de nextpnr: de 8 204 a 11 490, por las LUT de paso). Los ciclos por muestra bajan menos de lo previsto: shimmer 1 514 (antes 1 601), plate 1 195 (antes 1 258), freeze 1 313 (antes 1 393). Unos 14 ciclos por instrucción: la espera al resultado de cada instrucción sigue mandando.
- **Lección:** cuando el silicio falla y nextpnr no, hay que localizar la instrucción en la placa (la traza) antes de tocar el diseño. Las memorias que ocupan medio chip necesitan copias locales de la dirección y salidas registradas junto a cada bloque. Para medir entre 114,3 y 133,3 MHz, `margen_reloj.py --mdiv` cambia también el VCO.

## F-16 · Las simulaciones grandes no compilaban con el verilator de pip

- **Síntoma:** `c++: error: Vtop__pch.h.fast: linker input file not found`, solo en diseños grandes (el `hil_nucleo` con la traza).
- **Causa raíz:** el `verilated.mk` del paquete deja vacía la variable `CFG_CXXFLAGS_PCH_I`, que debería valer `-include`. Cuando verilator parte un diseño grande en varios ficheros, usa una cabecera precompilada, y g++ la recibe como si fuera un fichero de entrada.
- **Resolución:** `sim/conftest.py` añade `CFG_CXXFLAGS_PCH_I=-include` a `MAKEFLAGS`.
- **Lección:** un fallo de compilación que solo sale al crecer el diseño suele estar en la configuración de la herramienta, no en el código.

## F-17 · El difusor de velvet noise no superó a los allpass

- **Síntoma:** se probó un hall con un difusor de velvet noise (24 taps en 50 ms) en lugar de sus 4 allpass de entrada.
  - La cola salió **menos** densa: 10 % de muestras significativas, frente a 28 %.
  - Tenía más cresta: 12,9 frente a 8,8.
  - Con 4 líneas en lugar de 8, era además la cola más coloreada del catálogo: 6,4 entre bandas de octava, frente a 1,9 del plate.
- **Causa raíz:** un allpass en cadena da una respuesta infinita y cada vez más densa. El velvet noise da tantos impulsos como taps. En SOFIFI cada tap es un `RDA` de 19 ciclos: los 100 taps que harían falta para igualar la densidad cuestan unos 1 900 ciclos, y no caben junto a la red.
- **Resolución:** no se publica el programa. La hoja de ruta de la Fase 03 (punto 5) queda cubierta por el hall (red de 8 líneas con Householder).
- **Lección:** medir la propiedad que se promete (densidad, color) antes de nombrar el programa. Un algoritmo que funciona en un PC puede no ser el mejor cuando cada lectura de memoria cuesta 19 ciclos.

## F-18 · Cuatro fallos de programación del catálogo de la Fase 06

- **Síntoma:** las pruebas acústicas detectaron, antes de publicar:
  1. un autopan, un tilt y un ciclo de trabajo que no llegaban a su extremo;
  2. un slicer que nunca cerraba con pot1 = 1;
  3. un compresor cuya ganancia cruzaba 0 y se iba a −1;
  4. cuatro delays con la misma huella.
- **Causa raíz**, por orden:
  1. `rdax potN, C` con C > 1 seguido de `sof`: `SOF` usa el ACC ya **saturado** a ±1 (a24), así que 2·pot nunca pasaba de 1.
  2. `1 − pot` con pot = 0,99999988 y D = 0,99997 da −0,00003: un `skp gez` no saltaba.
  3. El lazo restaba el exceso de forma lineal (un integrador) mientras la envolvente, que cae despacio, seguía alta.
  4. En 0,1 s de impulso solo sonaba la señal seca: los ecos llegaban más tarde.
- **Resolución:**
  1. Multiplicar dentro del `SOF` (`rdax pot, 1.0` y `sof 1.999, −1.0`).
  2. Saltos incondicionales (`skp gez|neg`) cuando la rama no depende del signo.
  3. Bajada proporcional a la propia ganancia: exponencial, nunca cruza 0.
  4. Huellas más largas y una prueba que exige huellas distintas entre programas.
- **Lección:** en el núcleo, el ACC es ancho, pero cada instrucción que lee a24 (`SOF`, `WRAX`, `MULX`, `RDFX`) satura. Una prueba que mide el extremo del mando encuentra estos fallos; una que mide el centro, no.

## F-19 · Con RDAA y WRAA, el silicio fallaba a 114 MHz en la primera muestra

- **Síntoma:** el núcleo con `RDAA` y `WRAA` coincidía con el modelo en la simulación y en la placa a 100 MHz. A 114,3 MHz fallaba siempre, desde la muestra 0. En la Fase 06, el mismo plate pasaba a 120 MHz. nextpnr daba 157 MHz.
- **Diagnóstico:**
  1. La traza (`margen_reloj.py --traza`) dio la entrada 2: placa pc = 8, modelo pc = 4.
  2. El ACC de la placa en esa entrada era el del modelo en pc = 8. Entonces `rdax tmp` (pc 3 y pc 5) había dado 0 las dos veces.
  3. `wrax tmp` (pc 2) no había escrito el registro, o la lectura había fallado. En la muestra 0 la memoria aún no da datos: era un camino de control.
  4. En el rutado, los 24 bit de `reg7` (`tmp`) estaban repartidos por todo el chip (x de 12 a 53). El control (`estado`, `es_wrax`) estaba en x = 51 y `a24` en x de 12 a 21.
- **Causa raíz:** la escritura de `WRAX` decodificaba `rg` y las condiciones de estado en el mismo ciclo en que escribía. Esa red llega a los 1 536 biestables del banco, repartidos por todo el chip. El diseño creció con la Fase 07, la colocación cambió y ese camino quedó como el más justo.
- **Resolución:**
  - Escritura del banco en dos etapas. `E_EJEC` registra una máscara de 64 bit y el dato; en el ciclo siguiente cada registro se escribe con su bit de la máscara. No cuesta ciclos: la siguiente lectura llega varios ciclos después.
  - La resta `M[i+1] − M[i]` de `RDAA` se registra antes del multiplicador (regla de F-11). `RDAA` pasa de 26 a 27 ciclos.
- **Resultado medido** (nextpnr da 144 MHz para este rutado): 100 MHz, 2 de 2; 114,3 MHz, 2 de 2; 120 MHz, 3 de 3; **125 MHz, 3 de 3**; 133,3 MHz, 1 de 1. En la Fase 06 eran 125 MHz, 3 de 4, y 133,3 MHz, 0 de 1.
- **Lección:** un registro que escribe en el banco entero cruza el chip, igual que una dirección de memoria. La decodificación va en un ciclo y la escritura en el siguiente. nextpnr bajó de 157 a 144 MHz y la placa mejoró: su cifra no sirve para comparar dos rutados.

## F-20 · El borrado de la región absoluta dejaba dos palabras sin borrar

- **Síntoma:** la prueba `absoluta_igual_al_modelo` fallaba en la muestra 67 al correr detrás de otra prueba. Sola, pasaba.
- **Diagnóstico:**
  1. En la muestra 67, `rdaa pe, 0.5, 32700` lee el índice 32 767 de la región. El modelo lee 0 y el RTL leía un valor que había dejado la prueba anterior.
  2. El filtro de cocotb es una expresión regular: `igual_al_modelo` elegía también `absoluta_igual_al_modelo`. Por eso la prueba corría detrás de cada programa, con la memoria sucia.
- **Causa raíz:** en `E_BORRAR`, `mdir_w` sale de un registro, pero el modo absoluto salía de `borrar_abs` directamente. El modo iba un ciclo por delante de la dirección. La última palabra circular se escribía en la región, y la última palabra de la región, en la zona circular.
- **Resolución:**
  - `mabs_borrar` se registra en el mismo flanco que `mdir_w`.
  - La prueba pasa a llamarse `absoluta_como_el_modelo` y ensucia antes los extremos de la región con `WRAA`. Con el fallo de antes, la prueba falla.
- **Lección:** las señales que acompañan a una dirección registrada se registran con ella. Una prueba de borrado necesita memoria sucia: con la memoria a cero de la simulación, el borrado no se prueba (como en F-12).

## F-21 · En marea, el LFO de software se quedaba pegado en +1

- **Síntoma:** en la prueba de `marea`, la cola derecha sonaba unas diez veces más baja que la izquierda, y ninguna de las dos hacía olas.
- **Diagnóstico:** la ganancia izquierda valía 1 y la derecha 0,1 en todas las muestras. Las dos salen del LFO: el LFO estaba siempre en +1.
- **Causa raíz:** el programa redondeaba el triángulo con `CLIP` y escribía el resultado en `tri`. `tri` es el estado de `comun/lfo_triangulo.sasm`. `CLIP` tiene pendiente 1,5 en el origen: cada muestra empujaba el valor hacia 1, y allí se quedaba.
- **Resolución:** el valor redondeado va a otro registro (`ola`). `tri` solo lo escribe el bloque común.
- **Lección:** un registro de estado de un bloque común no se escribe fuera del bloque. Lo que se calcula a partir de él va a otro registro.

## F-22 · El shoegaze sonaba cinco veces más fuerte que el plate

- **Síntoma:** la demo de `shoegaze` tenía un nivel RMS de 0,13; la del plate, 0,027. La prueba acústica pasaba.
- **Diagnóstico:** con la saturación, la cola se recorta cerca de ±1. El plate deja la cola cerca de ±0,1. La ganancia de ×16 sube la cola hasta el techo.
- **Causa raíz:** la ganancia de salida era fija (0,5). La prueba medía la compresión, no el nivel frente al plate.
- **Resolución:** la salida baja de 0,6 a 0,1 cuando sube pot3. Con la mezcla a la mitad, el nivel queda a ±25 % del plate en todo el recorrido del mando.
- **Lección:** un salto de volumen al cambiar de programa es un riesgo (SECURITY.md). Cada programa nuevo se compara en nivel con el plate antes de publicarlo.

## F-23 · Una cadena con saturación sonaba seis veces más fuerte que el plate

- **Síntoma:** la demo de «Fuzz en la nube» (`saturacion` → `cloud`) recortaba: pico de 1,03 y nivel RMS diez veces el del plate.
- **Diagnóstico:** el mando «nivel» de `saturacion` estaba fijo en 0,6 y la mezcla en 1. Con una guitarra suave, la saturación sube la señal hasta el techo; el `cloud` la recibe casi a escala completa.
- **Causa raíz:** la lección de F-22 se aplicó al programa `shoegaze`, pero no había ninguna prueba de nivel para las cadenas. Un programa que va bien solo puede ir mal en una cadena.
- **Resolución:** «nivel» a 0,1 en esa cadena y ganancia 0,2 en «Sustain en la placa». Nueva prueba `ninguna_cadena_salta_de_volumen`: con una nota suave y una fuerte, ninguna cadena suena más del doble que el plate.
- **Lección:** una regla que sale de un fallo se convierte en prueba. Si se queda en una nota, el mismo fallo vuelve por otro camino.

## F-24 · La cola del microcódigo se llevó la última BSRAM

- **Síntoma:** con el núcleo segmentado (ADR 0014), nextpnr paraba: «no BELs remaining to implement cell type 'DP'». La simulación pasaba.
- **Diagnóstico:** el informe de recursos daba 56 BSRAM de 56. Una de más salía de la cola de búsqueda del microcódigo (8 × 54 bit).
- **Causa raíz:** Yosys convierte en BSRAM cualquier array con lectura por índice, aunque sea pequeño. En `hil_nucleo` la captura ya usa todas las BSRAM libres.
- **Resolución:** `(* ram_style = "logic" *)` en la cola. Después, la segunda vuelta la bajó a 4 palabras.
- **Lección:** un array nuevo en el RTL lleva su `ram_style` desde el principio. En este chip, cada BSRAM es memoria de retardo.

## F-25 · Tres fallos del controlador SD, encontrados en simulación

- **Síntoma 1:** el cargador rechazaba todos los bancos con el motivo «cabecera».
  - **Causa:** la magia se comparaba con la cadena `"SOFIFI\0\0"`. En Verilog, `\0` no es un escape fiable, y la constante no valía los 8 bytes esperados.
  - **Resolución:** la magia es la constante `64'h534F_4649_4649_0000`.
- **Síntoma 2:** la lectura de bloques fallaba con el motivo «token» a 25 MHz, y funcionaba a reloj lento.
  - **Causa:** MISO pasa por dos biestables de sincronización. Con medio periodo de SCK de 2 ciclos, el bit llegaba tarde a la muestra.
  - **Resolución:** el medio periodo rápido es de 4 ciclos como mínimo (12,5 MHz). El parámetro lo dice.
- **Síntoma 3:** el programa llegaba bien al núcleo, pero con la memoria y los LFO de otro.
  - **Causa:** los bloques de microcódigo sobrescribían los bytes guardados de los metadatos.
  - **Resolución:** solo se guardan los bytes de la cabecera y de los metadatos.
- **Lección:** el modelo de tarjeta en cocotb y las imágenes de `sofifi banco` encontraron los tres fallos antes de la placa. Las constantes de varios bytes van en hexadecimal.

## F-26 · Cuatro trampas del punto fijo en el lote 9 del catálogo

Las pruebas acústicas de los programas nuevos encontraron cuatro fallos antes de publicar.

- **El allpass de la forma FV-1 se satura con polos cerca de 1** (`desplazador`).
  - **Síntoma:** el eco salía a una cuarta parte de su nivel, y la banda contraria solo caía 31 dB.
  - **Causa:** la forma RDA + WRAP guarda un estado que crece como 1/(1 − k). Con k = 0,998, la palabra de 18 bit se satura.
  - **Resolución:** forma directa I: cada etapa guarda su salida y la siguiente la lee como x[n−1]. La banda contraria cae 64 dB.
- **Un coeficiente de RDAX mayor que 1 satura antes de SOF** (`desplazador`).
  - **Síntoma:** el mando de ancho y el footswitch no hacían nada.
  - **Causa:** SOF lee a24, el ACC saturado a [−1, 1). `rdax pot, -2.0` ya vale −1 antes de sumar.
  - **Resolución:** `rdax pot, -1.0` y después `sof 1.999, 0.99999`.
- **WRAX satura el registro por debajo de 1** (`arcoiris`).
  - **Síntoma:** una regeneración de 1,1 se quedaba en 0,99999 y el bucle no autooscilaba.
  - **Resolución:** la ganancia mayor que 1 va en el coeficiente (`rdax fb, 1.1`), no en un registro.
- **Una longitud de bucle fraccionaria apaga el bucle** (`erosion`).
  - **Síntoma:** con erosión 0, el bucle perdía agudos y nivel en cada vuelta.
  - **Causa:** la lectura caía entre dos muestras. La interpolación es un paso bajo, y se aplica una vez por vuelta.
  - **Resolución:** la longitud se redondea a muestras enteras. Con erosión 0, el bucle se repite bit a bit.
- **Lección:** en el punto fijo, el ACC y los registros saturan a [−1, 1). En un bucle con realimentación, un filtro escondido se eleva al número de vueltas. Las pruebas miden el nivel y la repetición exacta, no solo que «suena».

## F-27 · Constantes pequeñas, bucles de control y una huella ciega en el lote 10

- **Una constante menor que 1/32 768 no cabe en el operando D de SOF** (`violin`).
  - **Síntoma:** la edad de la nota y la rampa más lenta no avanzaban.
  - **Causa:** D es S2.15: su paso más pequeño es 1/32 768. 1/fs vale menos.
  - **Resolución:** la constante sale del producto de dos SOF, o de un factor ×64 que después multiplica un registro de 1/64.
- **Un paso bajo con un coeficiente diminuto se para antes de llegar** (`arco`).
  - **Síntoma:** el fundido de salida se quedaba en 0,002 y no llegaba a 0.
  - **Causa:** con RDFX y un coeficiente de 2^-15, el paso de cada muestra se redondea a 0 cerca del destino.
  - **Resolución:** un término lineal fijo y un suelo en 0.
- **Un control automático de ganancia se atasca o mata el bucle** (`arco`, `oscilador`).
  - **Síntoma:** en `arco`, la ganancia se quedaba en 0 para siempre. En `oscilador`, el lazo moría tras la primera nota.
  - **Causa:** una ganancia multiplicativa que llega a 0 ya no sube. Y un ataque fuerte con una recuperación lenta hundía la ganancia por debajo de la que mantiene la oscilación.
  - **Resolución:** un suelo para la ganancia (1/256). En `oscilador`, un ataque más suave y una recuperación de 85 ms.
- **Una huella con los mandos neutros no distingue programas** (`dinamica`).
  - **Síntoma:** `dinamica` y `freeze` tenían la misma huella.
  - **Causa:** la prueba de huella pone pot3 = 0,5, que en `dinamica` es «sin dinámica»: el programa es entonces un plate con el tanque con CLIP, igual que `freeze` sin pulsar.
  - **Resolución:** `POTS_HUELLA` da a `dinamica` una profundidad de 0,9, con una nota de 0,6 s.
- **Lección:** las constantes de tiempo largas no caben en una instrucción: se construyen. Un bucle de control necesita un suelo. Una huella solo vale si el estímulo y los mandos llegan al efecto.

## F-28 · La velocidad mínima de phaser y filtro era 0, y tres trampas del lote 11

- **Una constante que se redondea a 0** (`phaser` y `filtro`, publicados en la Fase 06).
  - **Síntoma:** con pot0 = 0, el barrido no iba a 0,05 Hz: se paraba. Lo vio el autor de `estelar` al escribir el mismo cálculo.
  - **Causa:** `sof 1.0, 4*0.05/fs` pide un D de 4·10⁻⁶. El paso de D es 1/32 768 ≈ 3·10⁻⁵, y el valor se redondeaba a 0 sin aviso.
  - **Resolución:** la velocidad se calcula ×64 y después se divide (`sof 1/64, 0`). **El ensamblador ahora rechaza** un coeficiente o un D distinto de 0 que se redondea a 0. Al ensamblar los 63 programas, solo saltó `filtro`.
- **Realimentar la suma de muchas tomas no funciona** (`enjambre`, `probabilidad`, `dados`).
  - **Síntoma:** la cola moría en menos de 0,5 s o el bucle autooscilaba saturado.
  - **Causa:** la suma de N tomas tiene picos de ganancia N en algunas frecuencias y una ganancia media mucho menor.
  - **Resolución:** el bucle sale de una sola toma, la más larga.
- **El coste cuenta todas las ramas de SKP** (`probabilidad`, `dados`).
  - **Síntoma:** un contador por toma o un reparto de tres vías gastaba más de 2 000 ciclos.
  - **Resolución:** un solo contador o dos vías por toma.
- **Un SKP que no salta deja la comparación en el ACC** (`dados`).
  - **Síntoma:** la salida se saturaba sin entrada.
  - **Resolución:** un `clr` al principio de la rama.
- **Lección:** una regla que una persona puede olvidar va en el ensamblador. Un bucle de realimentación se diseña con su ganancia peor, no con la media.

## F-29 · Cinco trampas de modulación y de nivel en el lote 12

- **La opción `media` de CHO no invierte un LFO SIN** (`dimension`).
  - **Síntoma:** la suma L + R ondulaba igual que cada canal: la antifase no existía.
  - **Causa:** `media` solo desplaza media vuelta la RAMP y la ventana; el seno no cambia. El modelo y el RTL coinciden.
  - **Resolución:** dos LFO SIN con la misma velocidad; la segunda línea usa un `depth` negativo.
- **Un chorus centrado en 8 ms hace un peine con la señal seca** (`orilla`).
  - **Síntoma:** a 196 Hz el nivel caía a 0,22 veces el del plate.
  - **Causa:** el seco y la voz al 50 % se cancelaban cerca de 187 Hz.
  - **Resolución:** el retardo recorre de 3 a 15 ms.
- **Un LFO triangular asimétrico se queda en el borde** (`vibe`).
  - **Síntoma:** con la subida más rápida que la bajada, el barrido se paraba en +1.
  - **Causa:** el paso de bajada no sacaba al LFO de la zona del borde, y el sentido cambiaba en cada muestra.
  - **Resolución:** el borde se comprueba sobre tri·sentido. `comun/lfo_triangulo.sasm` no cambia.
- **Un registro compartido entre dos filtros borra su estado** (`baldosa`).
  - **Síntoma:** con decay al máximo, la cola caía 36 dB en 0,4 s.
  - **Causa:** el allpass escribía su salida en el registro del paso bajo.
  - **Resolución:** cada filtro tiene su registro.
- **Un compresor y un expansor que no casan** (`eco_casero`).
  - **Síntoma:** cada nota empezaba con un pico de 2,4 veces y, con la realimentación al máximo, el bucle se desbocaba.
  - **Resolución:** los dos usan el mismo detector de media, y el compresor es de realimentación (1/envolvente sin división).
- **Lección:** un efecto de modulación se prueba en la suma mono y a frecuencias graves, no solo en un canal. Cada estado de un filtro necesita su propio registro.

## F-30 · Detectores, costuras y límites de lectura en el lote 13

- **El detector de ataques de `comun/compuerta.sasm` dispara con los graves** (`tartamudeo`).
  - **Síntoma:** una nota sostenida de 82 Hz disparaba 12 veces por segundo, y las notas de un arpegio no disparaban.
  - **Causa:** la envolvente rápida tiene mucho rizado en graves. La regla «rápida > 2·lenta» no se cumple mientras suena la nota anterior.
  - **Resolución:** un detector de pico con MAXX (caída de unos 30 ms) y la regla «pico > 1,5·lenta + umbral». El bloque común no cambia.
- **Una cabeza de lectura alcanza la costura del anillo** (`frenada`).
  - **Síntoma:** con un eco largo y una frenada larga, un clic al soltar el pedal.
  - **Causa:** la escritura alcanzaba a la cabeza que frena, que leía el punto donde el anillo da la vuelta.
  - **Resolución:** una ventana apaga esa cabeza cerca de la escritura.
- **Una velocidad variable pide dividir** (`resbalon`).
  - **Causa:** la fase de la ventana avanza (1 − v)/L por muestra, y la ISA no divide.
  - **Resolución:** un recíproco que se corrige en cada muestra: r ← r + 2·(1/32 − L·r).
- **Un CHO solo llega a 2·E muestras desde su base** (`dos_ecos`).
  - **Síntoma:** la toma a 1,5 veces el tiempo no llegaba a 0,82 s.
  - **Causa:** la excursión E de un LFO es como mucho 16 384 muestras.
  - **Resolución:** dos tomas con dos LFO de base distinta y un fundido entre ellas.
- **Lección:** un bloque común se valida con notas graves y con arpegios. Cada cabeza de lectura de un anillo necesita su ventana cerca de la escritura.

## F-31 · Lazos, periodos y detectores en el lote 14

- **Una espiral de pitch no se sostiene** (`espiral`).
  - **Síntoma:** con el pedal y una realimentación de 1,9, la cola se apagaba en 1-2 s.
  - **Causa:** el shifter del lazo saca la energía de la banda en cada vuelta. La ganancia sola no la devuelve.
  - **Resolución:** con el pedal, una parte de la señal salta el shifter dentro del lazo. El CLIP fija el techo.
- **Una cabeza de escritura con periodo 32 767** (`compas`).
  - **Síntoma:** una lectura `wp − d` que cruza la vuelta lee un retardo una muestra corto.
  - **Causa:** RDAA enmascara a 32 768 muestras, y la cabeza vuelve a 0 en 32 767.
  - **Resolución:** la cabeza recorre [0, 1) con periodo 32 768 exacto. `looper` y `granular` usan la vuelta antigua: queda pendiente comprobarlos.
- **El detector de ataques dispara varias veces en una nota grave** (`swell_ritmico`).
  - **Causa:** el pico cae un 8 % entre semiperiodos y la regla «pico > 1,5·lenta + umbral» cruza el 0 varias veces.
  - **Resolución:** un tiempo muerto de unos 60 ms tras cada ataque.
- **Una nota sostenida y su eco forman un peine** (`arpegio`).
  - **Síntoma:** la voz +4 sonaba un 65 % más baja a 330 Hz que a 262 Hz.
  - **Resolución:** el eco dura un paso, y solo el eco entra en la reverb.
- **Un coeficiente que cambia con un mando no cabe en RDFX** (`semilla`).
  - **Resolución:** el paso bajo usa MULX con un registro, como `cloud`.
- **Lección:** un lazo con transposición necesita un camino sin transponer. Una cabeza que da la vuelta tiene el periodo de la máscara.
