# ADR 0001 — La compuerta vive en el repositorio: `ci_local.sh` + pre-push versionado

- **Estado:** Aceptado · 2026-10-07
- **Revisión prevista:** cuando el repositorio tenga CI remota gratuita suficiente para la síntesis, o protección de rama.

## Contexto

El repositorio es privado en GitHub (plan gratuito): no hay protección de rama y los minutos de Actions son limitados. Además, la síntesis FPGA necesita herramientas (Gowin EDA, apicula) que no todo el mundo tiene instaladas. Sin una compuerta que viaje con el repositorio, la disciplina de `docs/SPEC_RAIZ.md` queda en buenas intenciones.

## Opciones evaluadas

1. GitHub Actions como única compuerta.
2. `scripts/ci_local.sh` + hook `pre-push` versionado, instalado con `core.hooksPath`.
3. Las dos cosas.

## Decisión

Opción 2. `scripts/ci_local.sh` es **la única definición** de qué trabajo es duro y cuál es blando. El hook delega con `--no-soft` y no tiene lista propia; lo comprueba `scripts/check_docs.py`.

Trabajos del día 0:

| Clase | Trabajos |
|---|---|
| Duros | `tech-debt`, `secrets`, `licenses`, `adr-gate`, `docs`, `i18n`, `model`, `ratchets` |
| Blandos | `rtl-lint` (verilator), `shell-lint` (shellcheck) |
| De release | síntesis con informe de recursos; aún no existe y `make release-check` falla a propósito |

## Consecuencias

- Cada push paga el coste de los trabajos duros. Se mide en `.ci_timing.log`, que no se versiona.
- Hay tres escapes, todos con nombre: `git push --no-verify`, `PREPUSH_SKIP=1` y `ADR_GATE_ACK=1`.

## Alternativas descartadas

- **Solo Actions:** sin protección de rama no bloquea nada, y la síntesis no cabe en el plan gratuito.

## Actualización 2026-10-07 (demos de audio versionadas)

La persona propietaria pide versionar las demos de audio en `demo_examples/`. La regla de `scripts/check_secrets_hygiene.sh` («ningún fichero de más de 1 MiB: los binarios van a releases») se mueve, con motivo, solo para esa carpeta: hasta 4 MiB por WAV y 16 MiB en total.

Las demos no son binarios huérfanos: `scripts/generar_demos.py` las regenera byte a byte, porque el núcleo es bit-exact y la guitarra sintética tiene semilla fija.

Si `demo_examples/` necesita superar los 16 MiB, las demos pasan a assets de release en lugar de subir el techo.

## Actualización 2026-10-07 (PRs apilados)

Con PRs apilados, GitHub solo reapunta la base del siguiente si se borra la rama base al fusionar. En la Fase 01, los PRs #2, #3 y #4 se fusionaron en sus ramas base y no en `main`, y hubo que llevarlos con el #5.

Desde ahora se cumplen tres reglas:
- se fusiona con `--delete-branch`;
- antes de fusionar se comprueba que la base sea `main`;
- `gh pr edit --base` falla por la deprecación de Projects classic, así que la base se cambia con `gh api -X PATCH repos/<dueño>/<repo>/pulls/N -f base=main`.

## Actualización 2026-10-07 (cadena EDA por pip, Fase 02)

Toda la cadena EDA abierta se instala con `make install` (extra `eda` de `pyproject.toml`): yowasp-yosys, yowasp-nextpnr-himbaechel-gowin, apycula, openfpgaloader, verilator y cocotb. Como ya no depende de lo que tenga instalado cada persona, cambian las clases:

| Clase | Cambio |
|---|---|
| Duros | `rtl-lint` pasa de blando a duro; entra `sim` (testbenches cocotb sobre verilator) |
| De release | entra `synth`, clase `release`: solo corre si se nombra (`make release-check`) y escribe `build/<top>_recursos.json` |

`shell-lint` sigue blando: shellcheck no se instala con pip.

Los trabajos que lanzan herramientas EDA corren con `ulimit -u` acotado. El mismo día, un enlace `.venv/bin/verilator -> verilator-cli` hizo que el envoltorio de pip se relanzara a sí mismo en bucle y la máquina cayó dos veces por OOM. La compuerta llama al binario del paquete con `VERILATOR_ROOT`, nunca al envoltorio.

## Actualización 2026-10-07 (primitivas Gowin, Fase 03)

- `rtl-lint` hace un lint por top de `rtl/top/tops.txt`, porque varios tops juntos dan `MULTITOP`. Define `SIMULACION`, que elige el modelo de comportamiento de las primitivas Gowin. La rama de síntesis la comprueba `optimizacion`.
- `mypy_path` incluye `scripts`, para que un script importe a otro (`verificar_primitivas.py` usa `leer_uart.py`).
- `scripts/fpga.sh` pone 100 MHz de objetivo de timing a todos los relojes, porque nextpnr no deduce la salida del PLL.

## Actualización 2026-10-07 (lint por módulo, Fase 04)

`rtl-lint` también hace un lint de cada módulo de `rtl/comun`, `rtl/primitivas` y `rtl/nucleo` por separado. Los módulos del núcleo se escriben antes de que exista un top que los use, y sin esto quedarían fuera del lint.

## Actualización 2026-10-07 (síntesis fuera del pre-push, Fase 04)

`optimizacion` pasa de dura a `release` (ADR 0010, revisión prevista) y desaparece `synth`. El pre-push queda en lint, simulación y modelo; la síntesis corre en `make optimizacion` y en `make release-check`.

## Actualización 2026-10-07 (demos sin límite total, Fase 06)

A petición de la persona propietaria, `secrets` ya no limita el total de `demo_examples/`. Cada programa tiene su demo y la biblioteca crece. Esto sustituye a la regla anterior («si pasan de 16 MiB, van a assets de release»): la persona propietaria prefiere tenerlas en el repositorio.

- Se mantiene el límite de 4 MiB por demo: evita subir un WAV enorme por error.
- Las demos están en PCM de 16 bit.
- Cada regeneración de las demos aumenta el historial de git. Si el repositorio crece demasiado, la alternativa es MP3. Para eso hace falta un codificador (LAME es LGPL) y un ADR propio.

## Actualización 2026-10-07 (demos en Ogg Vorbis, Fase 06)

La persona propietaria elige comprimir las demos. Pasan de WAV a **Ogg Vorbis**: 1,7 MB en lugar de 15,2 MB.

- Opus no sirve: solo admite 8, 12, 16, 24 y 48 kHz, y SOFIFI trabaja a 48 828 Hz (ADR 0005). Vorbis admite cualquier frecuencia.
- El codificador es `soundfile` (BSD) sobre libsndfile (LGPL-2.1), libvorbis y libogg (BSD). Se usan como bibliotecas desde un script y no se copian (ADR 0002). Van en el grupo opcional `demos` de `pyproject.toml`.
- Dos codificaciones dan el mismo audio, pero el fichero cambia en el número de serie de Ogg. `scripts/generar_demos.py` solo reescribe un `.ogg` si su audio cambia.
- `secrets` admite `.ogg` de hasta 4 MiB en `demo_examples/`.

## Actualización 2026-10-07 (pruebas del modelo en paralelo, Fase 06)

El trabajo `model` corre `pytest -n auto` (`pytest-xdist`, MIT). La biblioteca de programas va a crecer a unos 40, y cada programa añade unos segundos de pruebas acústicas. En serie, la suite del modelo tardaba unos 50 s con 9 programas; en paralelo, 18 s en 8 núcleos. La cobertura se sigue midiendo.

El trabajo `sim` corre `pytest sim -n 4`. La prueba del núcleo se parte en una prueba por programa, más otra con las pruebas que no dependen del programa (reset, saltos y coste de cada instrucción). Cada proceso compila el núcleo una vez. Con 9 programas, `sim` baja de 176 s a 111 s. Con 8 procesos tarda 122 s: pesan más las compilaciones.

## Actualización 2026-10-08 (compuerta de cierre de fase, Fase 07)

A petición de la persona propietaria, cerrar una fase exige poner al día **toda** la documentación y **todas** las infografías en los cuatro idiomas (ADR 0007). Lo comprueba el trabajo nuevo `cierre` (`scripts/check_cierre.py`), de clase dura: solo lee ficheros y git.

Siempre comprueba:

1. Los README de los cuatro idiomas declaran la versión de la última fase cerrada.
2. Las infografías `sofifi` de los cuatro idiomas declaran esa versión.
3. Cada captura de `docs/img/` sale de la infografía actual. `scripts/capturar_infografia.py` anota la huella del HTML en `docs/img/capturas.json`.

En la rama que cierra una fase (cambia `docs/fases/estado_fases.csv` respecto de `origin/main`), además:

4. Ninguna traducción va `desactualizada`. Entre cierres, el estado `desactualizada` sigue permitido (ADR 0007).
5. `docs/arquitectura_fpga.md` tiene la sección de la fase.
6. La spec de la fase dice «Cerrada el …».

La compuerta no juzga si el contenido es correcto: comprueba que nada queda atrás. Revisar el contenido sigue siendo trabajo del PR de cierre.
