# SBOM · Componentes de SOFIFI

Qué piezas forman el pedal por dentro y con qué herramientas se construye. Cada pieza tiene una explicación sencilla: qué hace y qué aporta al conjunto. El detalle técnico (recursos, latencias, historia por fase) está en `docs/arquitectura_fpga.md`.

## La idea en una frase

La FPGA contiene un **pequeño procesador de audio hecho a medida** (el núcleo). Cada efecto (plate, shimmer, freeze…) es un **programa** que ese procesador ejecuta 48 828 veces por segundo, una vez por cada muestra de audio.

## Componentes del FPGA

### Relojes

| Componente | Qué hace, en sencillo | Qué aporta |
|---|---|---|
| **PLL** (`pll_100`) | Convierte el reloj de 50 MHz del cristal de la placa en uno de 100 MHz. | Da al núcleo el doble de velocidad: 2 048 pasos de trabajo por cada muestra de audio. |
| **Generador de muestra** | Da una señal cada 2 048 ciclos de reloj. | Marca el ritmo del audio: 48 828 muestras por segundo, exactas. |

### El núcleo DSP

| Componente | Qué hace, en sencillo | Qué aporta |
|---|---|---|
| **Microcódigo** | Memoria con las instrucciones del programa (hasta 2 048). | Permite cambiar de efecto sin cambiar el hardware: basta con cargar otro programa. |
| **Secuenciador** | Lee las instrucciones y dice a cada pieza qué hacer. Empieza una instrucción sin esperar a que acabe la anterior. Solo espera si necesita un resultado que aún no está listo (ADR 0014). | Es el «director de orquesta» del núcleo. Así, los programas gastan 1,6 veces menos ciclos. |
| **Banco de registros** | 64 casillas que guardan números: entradas, salidas, potenciómetros y variables del programa. | Es la «mesa de trabajo» de cada efecto. |
| **Multiplicador** (bloque DSP) | Multiplica dos números en un paso. | Casi todo en audio son multiplicaciones: volumen, filtros, mezclas. |
| **ALU** | Suma, compara y satura (evita que el sonido se desborde). | Combina los resultados y los guarda en el acumulador. |
| **Acumulador (ACC)** | Un registro de 48 bit donde se suman los productos. | Mucha precisión: evita el ruido de redondeo en las colas largas. |
| **Memoria de retardo** (BSRAM) | Guarda el audio de los últimos ~0,9 s, como una cinta en bucle. Va por grupos de bloques, cada uno con su copia de la dirección. Con `RDAA` y `WRAA`, 32 768 palabras funcionan como una cinta fija: lo grabado no se aleja. | Es la base de toda reverb y todo delay: oír el pasado del sonido. Los grupos dejan que funcione con margen en el chip real. La parte fija hace posibles el looper y el granular. |
| **LFO ×4** | Osciladores lentos (senoidal, aleatorio, rampa). | Mueven las lecturas de la memoria: el chorus, la modulación de la reverb y el cambio de tono del shimmer. |
| **ROM Hermite** | Tabla fija de 256 × 4 coeficientes. | Permite leer la memoria «entre muestras» sin ruido: modulación suave. |
| **Curva suave** | Una saturación cúbica, sin cortes bruscos. | Limita el sonido de forma musical (`CLIP`) y da forma al LFO senoidal. |

### Entrada, salida y pruebas

| Componente | Qué hace, en sencillo | Qué aporta |
|---|---|---|
| **UART TX / RX** | Puerto serie con el PC, a través del USB de la placa. | Permite hablar con la FPGA: pedir pruebas y recibir resultados. |
| **Cargador de programa** | Copia un programa desde una memoria fija al microcódigo al arrancar. | En los tops de prueba carga el plate, el looper o el programa de `make hil`. |
| **Captura y CRC-32** (solo en pruebas) | Graba 4 096 muestras a velocidad real y las envía con un código de control. | Demuestra que el hardware suena **exactamente** igual que el modelo del PC. |
| **Traza** (solo en pruebas) | Graba qué instrucción se ejecuta y qué valor deja en el acumulador. | Si el chip falla, dice en qué instrucción, para saber qué parte arreglar. |
| **Medidor de frecuencia** (solo en pruebas) | Cuenta ciclos de un reloj durante un segundo de otro. | Comprobó que el PLL y la frecuencia de muestreo son exactos. |

### La microSD (Fase 08, en curso)

| Componente | Qué hace, en sencillo | Qué aporta |
|---|---|---|
| **Controlador SD** (`sd_spi`) | Habla con la tarjeta por SPI: la arranca y lee bloques de 512 bytes. No escribe en ella. | Da acceso a la biblioteca de programas sin un sistema de ficheros, que sería caro y frágil. |
| **Cargador del banco** (`cargador`, `carga_sd`) | Lee una ranura de la tarjeta dos veces. La primera vez solo comprueba; la segunda escribe el programa en el núcleo. | Un programa dañado no se carga. Si la primera lectura falla, el núcleo sigue con el programa anterior. |
| **Prueba de la SD** (`prueba_sd`, solo en pruebas) | Carga ranuras a petición del PC y le dice qué leyó. | Comprueba que la tarjeta da los mismos datos que el modelo. Falta probarla con la tarjeta real. |

### Primitivas del chip (piezas físicas del GW5A)

| Primitiva | Cuántas usa | Para qué |
|---|---|---|
| BSRAM (bloques de 18 Kbit) | 48 de 56 en el núcleo | memoria de retardo y microcódigo |
| DSP (MULTALU27X18) | 2 de 28 | el multiplicador |
| PLLA | 1 de 6 | el reloj de 100 MHz |
| LUT4 y flip-flops | ~54 % y ~31 % (top de pruebas `hil_nucleo`) | toda la lógica, y las copias que dan margen de reloj |

## Herramientas de software

Todo se instala con `make install` (pip) y es software libre.

| Herramienta | Versión | Licencia | Qué hace |
|---|---|---|---|
| Yosys (YoWASP) | 0.69 | ISC | Traduce el Verilog a puertas lógicas (síntesis). |
| nextpnr-himbaechel-gowin (YoWASP) | 0.11.1 | ISC | Coloca y conecta esas puertas dentro del chip. |
| apicula | 0.32 | MIT | Genera el bitstream del GW5A. |
| openFPGALoader | 1.1.1 | Apache-2.0 | Carga el bitstream en la placa por USB. |
| verilator | 5.48 | LGPL-3.0 o Artistic-2.0 | Simula el Verilog. Solo se usa como herramienta; no se copia código (ADR 0002). |
| cocotb | 2.1 | BSD-3-Clause | Escribe las pruebas de simulación en Python. |
| pyserial | 3.5 | BSD-3-Clause | Habla con la UART de la placa. |
| soundfile | 0.12 | BSD-3-Clause | Escribe las demos en Ogg Vorbis. Usa libsndfile (LGPL-2.1) como biblioteca, sin copiar código (ADR 0002). Opcional: `pip install -e '.[demos]'`. |
| Python + numpy | 3.12+ / 2.x | PSF / BSD | El modelo bit-exact, que es la referencia de todo (ADR 0003). |

Las versiones mínimas están en `pyproject.toml`. Las trampas de cada herramienta están en `fails.md` y `rtl/AGENTS.md`.
