# Scripts y CLI `sofifi`

Esta guía describe cada script de `scripts/` y cada orden de la CLI `sofifi`. Está organizada por tarea. Para cada herramienta dice qué hace, el comando típico, qué necesita y en qué compuerta o fase entra.

La cabecera o el docstring de cada script tiene el detalle completo. Los scripts de Python con argparse y la CLI `sofifi` también dan su ayuda con `--help`.

## Antes de empezar

- Ejecuta todo desde la raíz del repositorio. La CLI `sofifi` busca `programas/` y `presets/` en el directorio actual.
- Crea el entorno una vez con `make install`. El entorno instala el modelo, las herramientas de la compuerta y la cadena EDA en `.venv`.
- Instala el hook una vez con `make hooks`.
- Para trabajar con la placa, instala la regla udev de `scripts/udev/99-tang-primer-25k.rules`. Su cabecera da los comandos.

Códigos de salida comunes a casi todas las herramientas:

| Código | Significado |
|---|---|
| 0 | Bien: la comprobación pasa o el trabajo termina. |
| 1 | La comprobación falla, o la placa da otro resultado que el modelo. |
| 2 | Uso incorrecto: falta un argumento, o el trabajo no existe. |

## 1. Compuertas de la CI

La compuerta vive en el repositorio (ADR 0001). `scripts/ci_local.sh` es la única lista de trabajos. El hook `scripts/hooks/pre-push` la llama con `--no-soft` y no tiene lista propia.

### Trabajos de `scripts/ci_local.sh`

La tabla sigue el orden de ejecución de la lista `JOBS` de `scripts/ci_local.sh`.

| Trabajo | Clase | Qué comprueba | Script o comando |
|---|---|---|---|
| `tech-debt` | dura | Ningún comentario empieza por un marcador de deuda. | `scripts/check_tech_debt.sh` |
| `secrets` | dura | No hay ficheros prohibidos ni credenciales. Ningún fichero pasa de 1 MiB; una demo `.ogg`, de 4 MiB. | `scripts/check_secrets_hygiene.sh` |
| `licenses` | dura | Cada fuente tiene cabecera SPDX. El código ajeno está en `docs/terceros.yaml` (ADR 0002). | `scripts/check_licenses.py` |
| `adr-gate` | dura | Un diff que toca una sentinela de `docs/adr/sentinelas.txt` toca también un ADR. | `scripts/check_adr_gate.sh` |
| `docs` | dura | Las rutas, los objetivos de `make` y los ADR que citan los mapas existen. También fases, versión, hook y registros. | `scripts/check_docs.py` |
| `i18n` | dura | Cada traducción existe y su sello es honesto (ADR 0007). | `scripts/check_i18n.py` |
| `cierre` | dura | README e infografías declaran la versión, y las capturas están al día. | `scripts/check_cierre.py` |
| `model` | dura | Estilo, formato, tipos y pruebas del modelo. | `ruff check`, `ruff format --check`, `mypy` y `pytest -n auto` |
| `rtl-lint` | dura | Lint de cada top de `rtl/top/tops.txt` y de cada módulo de `rtl/comun/`, `rtl/primitivas/` y `rtl/nucleo/`. | `verilator --lint-only -Wall -DSIMULACION` |
| `sim` | dura | Los testbenches cocotb dan los mismos bits que el modelo (ADR 0003). | `pytest sim -n 4` |
| `ratchets` | dura | Ninguna medida de `docs/ratchets.yaml` empeora su listón. | `scripts/check_ratchets.py` |
| `shell-lint` | blanda | shellcheck sobre `scripts/*.sh` y `scripts/hooks/*`. | `shellcheck` |
| `esquematicos` | blanda | Cada PDF de `schematics/` corresponde a su fuente RTL (ADR 0012). | `scripts/esquematicos.py --comprobar` |
| `optimizacion` | release | Cada top sintetiza y cierra el reloj; imprime pistas (ADR 0010). | `scripts/check_optimizacion.py` |

Clases:

- **dura**: un fallo bloquea el push. El resumen dice `ROJO`.
- **blanda**: un fallo da `WARN` y no bloquea. Si falta la herramienta, el trabajo dice `NO CORRIÓ`. No lo presentes como verde.
- **release**: el trabajo solo corre si se nombra. Sintetiza todos los tops y tarda unos 3 minutos.

### Comandos

| Tarea | Comando |
|---|---|
| Duras y blandas | `make ci` |
| Solo duras (lo que corre el pre-push) | `make ci-dura` |
| Ver la lista de trabajos | `scripts/ci_local.sh --list` |
| Unos trabajos concretos | `scripts/ci_local.sh model docs` |
| Modelo | `make test` |
| Simulación del RTL | `make sim` |
| Mapas y registros | `make docs` |
| Segunda vuelta antes del PR | `make optimizacion` (trabajos `optimizacion` y `ratchets`) |

`scripts/ci_local.sh` añade una línea con su duración a `.ci_timing.log`. Ese fichero no está en git.

### Hook y escapes

| Herramienta | Qué hace | Cuándo |
|---|---|---|
| `scripts/install_hooks.sh` | Pone `core.hooksPath = scripts/hooks`. | Una vez, con `make hooks`. |
| `scripts/hooks/pre-push` | Ejecuta `scripts/ci_local.sh --no-soft`. | En cada `git push`. |

Escapes con nombre. Úsalos solo con un motivo:

| Variable o opción | Efecto |
|---|---|
| `ADR_GATE_ACK=1` | `adr-gate` acepta un diff sin ADR. Significa «revisé y ninguna decisión cambia». |
| `PREPUSH_SKIP=1` o `git push --no-verify` | El hook no ejecuta la compuerta. |

### Comprobaciones sueltas

Los scripts `check_*` no tienen opciones. Se ejecutan sin argumentos y no escriben ficheros, salvo `check_i18n.py --sellar`.

| Script | Comando típico |
|---|---|
| `scripts/check_docs.py` | `.venv/bin/python scripts/check_docs.py` |
| `scripts/check_i18n.py` | `.venv/bin/python scripts/check_i18n.py` |
| `scripts/check_i18n.py --sellar` | `.venv/bin/python scripts/check_i18n.py --sellar docs/EXTENDING.en.md` (un fichero por llamada) |
| `scripts/check_cierre.py` | `.venv/bin/python scripts/check_cierre.py` |
| `scripts/check_licenses.py` | `.venv/bin/python scripts/check_licenses.py` |
| `scripts/check_ratchets.py` | `.venv/bin/python scripts/check_ratchets.py` (después del trabajo `model`) |

## 2. Síntesis y placa

La placa es una Sipeed Tang Primer 25K. La cadena EDA es abierta y está en `.venv`: yowasp-yosys, yowasp-nextpnr-himbaechel-gowin, gowin_pack y openFPGALoader. La lista única de tops y sus fuentes está en `rtl/top/tops.txt`.

> **Advertencia.** Un top que envía a pleno caudal por la UART cuelga el puente BL616 si el PC deja de leer. Entonces hay que volver a conectar el USB. Limita el caudal de cada top nuevo (`rtl/AGENTS.md`, F-02 en `fails.md`).

| Herramienta | Qué hace | Comando típico | Necesita |
|---|---|---|---|
| `scripts/fpga.sh synth` | Sintetiza, coloca, ruta y empaqueta un top. Deja `build/<top>.fs` y `build/<top>_recursos.json`. | `make synth TOP=hil_nucleo` | `.venv` |
| `scripts/fpga.sh prog` | Carga el bitstream en la SRAM de la FPGA. Se pierde al apagar. | `make prog TOP=hil_nucleo` (sintetiza antes) | placa por USB |
| `scripts/informe_recursos.py` | Resume el informe de nextpnr: celdas usadas y MHz. | Lo llama `fpga.sh synth`. | informe de nextpnr |
| `scripts/check_optimizacion.py` | Sintetiza todos los tops, exige timing y da pistas `PISTA`. | `make optimizacion` | `.venv`; no necesita la placa |
| `scripts/leer_uart.py` | Lee la UART de la FPGA y exige un texto. | `make uart` | placa; `/dev/ttyUSB1` |

Variables de `scripts/fpga.sh`:

| Variable | Valor por defecto | Uso |
|---|---|---|
| `TOP` (Makefile) | `hola_uart` | Top de `rtl/top/tops.txt` para `make synth` y `make prog`. |
| `FREQ_MHZ` | 100 | Reloj objetivo para nextpnr (ADR 0005). |
| `SEMILLAS_PNR` | `2 3 4` | Semillas que nextpnr prueba si el reloj no cierra (F-33). |
| `SYNTH_OPCIONES` | vacía | Opciones extra para `synth_gowin`. |
| `CST` | `rtl/top/primer25k.cst` | Fichero de restricciones de pines. |

El depurador BL616 da dos puertos: `/dev/ttyUSB0` es JTAG y `/dev/ttyUSB1` es la UART de la FPGA, a 115 200 baudios.

## 3. Pruebas en la placa (HIL)

El modelo bit-exact tiene la razón (ADR 0003). El timing se mide en la placa (ADR 0011). Estas herramientas cargan un top, piden una captura por la UART y la comparan con el modelo.

| Herramienta | Qué hace | Comando típico | Salida |
|---|---|---|---|
| `make hil` | Escribe la ROM de un programa o una cadena, sintetiza `hil_programa`, lo carga y ejecuta `scripts/hil_nucleo.py`. | `make hil HIL=marea` | 0 si las 4 096 muestras coinciden |
| `scripts/hil_nucleo.py` | Compara 4 096 muestras y el CRC-32 de la placa con el modelo. Con `--traza K0`, busca la primera instrucción distinta. | `.venv/bin/python scripts/hil_nucleo.py --programa plate` | 0 si todo coincide |
| `scripts/hil_lote.py` | Ejecuta `make hil` para varios nombres y escribe build/hil_lote.csv. Tarda unos 4 minutos por nombre. | `.venv/bin/python scripts/hil_lote.py --todos` | 0 si todos coinciden |
| `scripts/margen_reloj.py` | Cambia solo el divisor del PLL del diseño ya rutado y repite la captura a cada frecuencia. | `.venv/bin/python scripts/margen_reloj.py --divisores 8 7 6` | 0 si 100 MHz pasa siempre |
| `scripts/verificar_primitivas.py` | Comprueba los tops de prueba de las primitivas: `dsp`, `bsram`, `pll` y `fs`. | `.venv/bin/python scripts/verificar_primitivas.py dsp` | 0 si todas las líneas son correctas |

Qué top carga cada prueba:

| Prueba | Top | Script |
|---|---|---|
| Núcleo con `plate` | `make prog TOP=hil_nucleo` | `scripts/hil_nucleo.py` |
| Looper | `make prog TOP=hil_looper` | `scripts/hil_nucleo.py --programa looper` |
| Cualquier programa o cadena | `make hil HIL=NOMBRE` | `scripts/hil_nucleo.py --programa NOMBRE` (lo llama `make hil`) |
| Margen de reloj | `make synth TOP=hil_nucleo` y `make synth TOP=prueba_pll` | `scripts/margen_reloj.py` (`--base hil_looper --programa looper` para el looper) |
| Multiplicador DSP | `make prog TOP=prueba_dsp` | `scripts/verificar_primitivas.py dsp` |
| BSRAM | `make prog TOP=prueba_bsram` | `scripts/verificar_primitivas.py bsram` |
| PLL | `make prog TOP=prueba_pll` | `scripts/verificar_primitivas.py pll` |
| Frecuencia de muestreo y UART RX | `make prog TOP=prueba_fs` | `scripts/verificar_primitivas.py fs` |
| MicroSD | `make prog TOP=prueba_sd` | `scripts/prueba_sd.py` (sección 4) |

Notas:

- `make hil` acepta un programa o una cadena que cabe en la memoria de `hil_nucleo`: 38 912 palabras. `sofifi rom` rechaza los demás.
- `scripts/margen_reloj.py` necesita `build/<base>.pnr.json` y build/prueba_pll.fs. Al terminar carga `prueba_pll`, que envía poco por la UART.
- Todas estas herramientas leen `/dev/ttyUSB1` por defecto. Cambia el puerto con `--puerto`.

## 4. MicroSD

La microSD almacena programas; no retarda audio (ADR 0004). El procedimiento completo, con la advertencia sobre `dd`, está en [microsd.md](microsd.md).

| Herramienta | Qué hace | Comando típico | Necesita |
|---|---|---|---|
| `sofifi banco` | Escribe la imagen del banco. Sin nombres, lleva todo lo que cabe. | `.venv/bin/sofifi banco build/banco.img` | nada |
| `sofifi banco --leer` | Comprueba el CRC y los límites de cada ranura y la lista. | `.venv/bin/sofifi banco --leer build/banco.img` | nada |
| `scripts/prueba_sd.py` | Pide a `prueba_sd` que cargue cada ranura y la compara con el modelo. | `.venv/bin/python scripts/prueba_sd.py --imagen build/banco.img` | placa, PMOD TF en J6, tarjeta escrita, `/dev/ttyUSB1` |

Fase 08: `scripts/prueba_sd.py` todavía no se probó con una tarjeta real.

## 5. Documentación y medios

| Herramienta | Qué hace | Comando típico | Cuándo |
|---|---|---|---|
| `scripts/check_i18n.py --sellar` | Pone al día el sello de una traducción. | `.venv/bin/python scripts/check_i18n.py --sellar README.en.md` | Después de actualizar cada traducción (ADR 0007). |
| `scripts/capturar_infografia.py` | Captura las secciones de las infografías como PNG y anota su huella en `docs/img/capturas.json`. | `.venv/bin/python scripts/capturar_infografia.py --todas` | Al cerrar una fase (compuerta `cierre`). |
| `scripts/esquematicos.py` | Genera un PDF por módulo RTL en `schematics/`. | `make esquematicos` | Después de cambiar un módulo RTL (ADR 0012). |
| `scripts/generar_demos.py` | Regenera las demos Ogg de `demo_examples/` y sus guías. | `.venv/bin/python scripts/generar_demos.py` | Después de cambiar un programa con demo. |
| `sofifi catalogo` | Regenera `docs/programas.md` y sus traducciones. | `.venv/bin/sofifi catalogo` | Después de cambiar un programa, un preset o una cadena. |

Necesidades:

- `scripts/capturar_infografia.py` y `scripts/esquematicos.py` necesitan chrome-headless-shell de la caché de Playwright (`~/.cache/ms-playwright`).
- `scripts/esquematicos.py` necesita también netlistsvg: `make esquematicos` ejecuta antes `npm install` en `herramientas/esquematicos/`. La opción `--comprobar` no necesita ninguno de los dos.
- `scripts/generar_demos.py` necesita el extra `demos` (`make install` lo instala). Tarda unos 2 minutos en 8 núcleos. Solo reescribe un `.ogg` si su audio cambia.

## 6. Modelo y programas: la CLI `sofifi`

La CLI `sofifi` es la entrada al modelo bit-exact. Se instala en `.venv/bin/sofifi` con `make install`. Cada orden da su ayuda con `sofifi ORDEN --help`.

| Orden | Qué hace | Ejemplo | Escribe |
|---|---|---|---|
| `asm` | Ensambla un programa y da sus ciclos del RTL de 2 048 (ADR 0005). | `sofifi asm programas/plate.sasm build/plate` | build/plate.hex y build/plate.json |
| `tablas` | Regenera la tabla Hermite y los programas en ROM del RTL. | `sofifi tablas` | ficheros `.v` de `rtl/` |
| `catalogo` | Regenera el catálogo de programas, presets y cadenas. | `sofifi catalogo` | `docs/programas.md` y sus traducciones |
| `render` | Procesa un WAV con un programa. | `sofifi render programas/plate.sasm seca.wav plate.wav --preset 'Placa corta'` | el WAV de salida |
| `presets` | Lista los presets de `presets/banco.toml`. | `sofifi presets plate` | nada |
| `cadenas` | Lista las cadenas con su coste y dice si caben (ADR 0013). | `sofifi cadenas` | nada |
| `componer` | Escribe una cadena como un solo programa. | `sofifi componer "Eco y muelle" build/eco.sasm` | el `.sasm` de salida |
| `cadena` | Procesa un WAV con una cadena. | `sofifi cadena "Eco y muelle" seca.wav eco.wav` | el WAV de salida |
| `rom` | Escribe la ROM `programa_hil` de un programa o una cadena. | `sofifi rom marea build/programa_hil.v` | el `.v` de salida |
| `banco` | Escribe o comprueba la imagen de la microSD. | `sofifi banco build/banco.img` | la imagen |

Opciones de `render` y `cadena`:

| Opción | Efecto |
|---|---|
| `--pot potN=V` | Pone el mando N en el valor V, de 0 a 1. Se puede repetir. |
| `--freeze INICIO:FIN` | Pulsa el pulsador entre esos segundos. Se puede repetir. |
| `--cola S` | Añade S segundos de silencio al final. |
| `--preset NOMBRE` | Solo `render`: parte de los mandos de un preset. Después se aplica cada `--pot`. |

Una cadena parte de las posiciones de mandos de `presets/cadenas.toml`.

Para añadir un programa, un módulo RTL o una compuerta, lee [EXTENDING.md](EXTENDING.md).

### Prueba de aceptación del núcleo

`sim/nucleo/nucleo_test.py` compara el núcleo RTL con el modelo. La compuerta `sim` usa 1 000 muestras. Para la aceptación completa:

```sh
SOFIFI_MUESTRAS=4883 .venv/bin/python -m pytest sim/nucleo/nucleo_test.py
```

## Comportamientos que conviene conocer

- `scripts/generar_demos.py` no tiene `--help`. Un argumento distinto de `--readme` regenera todas las demos.
- Los scripts `check_*` no leen argumentos. `scripts/check_optimizacion.py --help` sintetiza todos los tops.
- `scripts/informe_recursos.py` necesita la ruta del informe de nextpnr. Sin ella, falla.
- `scripts/capturar_infografia.py` imprime su ayuda y sale con 1 si los argumentos no son correctos o si falta chrome-headless-shell.
- `scripts/ci_local.sh --help` y `scripts/fpga.sh` sin orden imprimen su cabecera.
