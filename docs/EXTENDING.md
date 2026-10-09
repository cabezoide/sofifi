# Cómo extender

Paso a paso para cada tipo de pieza. Si añadir algo obliga a tocar un sitio que
no está en esta lista, la lista está incompleta. Corregirla en el mismo PR.

## Un programa (un efecto)

Un efecto es un programa, no un módulo RTL (ADR 0006).

1. Si el programa viene de un tercero, añadir su entrada en `docs/terceros.yaml`.
   `uso: portado` solo vale con una licencia permisiva (ADR 0002).
2. Escribir `programas/<nombre>.sasm`. La cabecera lleva estas líneas:
   - `; familia:` y `; resumen:`;
   - `; resumen.en:`, `; resumen.zh-CN:` y `; resumen.ja:`, el resumen traducido;
   - `; potN = nombre`, una línea por mando.
3. Tomar los bloques que ya existen de `programas/comun/` con `include`.
4. Comprobar que cabe: `sofifi asm programas/<nombre>.sasm out/<nombre>` da los
   ciclos del RTL. Deben ser 2 048 o menos (`model/sofifi/domain/coste.py`).
5. Escribir la prueba de su propiedad acústica en `model/tests/`, en el fichero
   de su familia o en uno propio. Las medidas comunes están en `model/tests/acustica.py`.
6. Añadir su huella en `HUELLAS` (`model/tests/programas_test.py`). Las pruebas
   de «cabe», de huella y de igualdad con el RTL (`sim/nucleo/nucleo_test.py`)
   recorren todos los `.sasm` y fallan si falta algo.
7. Si un mando tiene un nombre nuevo, añadir su traducción en `MANDOS`
   (`model/sofifi/services/catalogo_textos.py`). `model/tests/catalogo_test.py` lo exige.
8. Añadir al menos 5 presets (sección «Un preset»).
9. Regenerar el catálogo en los cuatro idiomas con `sofifi catalogo`.
10. Añadir la demo en `DEMOS` (`scripts/generar_demos.py`). Ejecutar el script:
    escribe el `.ogg` y las guías `demo_examples/README*.md`.
11. Si el programa cabe en los 38 bloques de `hil_nucleo`, probarlo en la placa
    con `make hil HIL=<nombre>`.

## Un cambio en un programa que ya existe

> **Advertencia.** Un cambio en `programas/comun/` cambia todos los programas
> que lo incluyen. F-32 cambió las huellas de 74 programas.

1. Actualizar las huellas que cambian en `HUELLAS`.
2. Si cambian `plate`, `looper` o un bloque que incluyen, ejecutar `sofifi tablas`.
   Regenera las ROM `rtl/top/programa_plate.v` y `rtl/top/programa_looper.v`.
   `model/tests/tablas_test.py` lo exige.
3. Regenerar el catálogo con `sofifi catalogo`.
4. Regenerar las demos con `scripts/generar_demos.py`. Un `.ogg` solo se
   reescribe si su audio cambia.

## Un preset

Un preset es el mismo programa con otros mandos y un nombre.

1. Añadir una línea `"Nombre" = [pot0, pot1, …]` en la tabla del programa, en
   `presets/banco.toml`. Los valores van de 0 a 1; un mando sin usar vale 0.
2. Escuchar el preset: `sofifi render programas/<programa>.sasm entrada.wav salida.wav --preset "Nombre"`.
3. Regenerar el catálogo con `sofifi catalogo`: el catálogo cuenta los presets.
   `model/tests/presets_test.py` comprueba el programa, los mandos y los rangos.

## Una cadena (dos programas en uno)

Una cadena une programas que ya existen, sin cambiar el RTL (ADR 0013).

1. Ver con `sofifi cadenas` cuánto gasta una cadena parecida. Cada programa
   gasta sus propios registros y LFOs. El núcleo tiene 32 registros generales y 4 LFOs.
2. Añadir un `[[cadena]]` en `presets/cadenas.toml`:
   - en `mandos`, un número es un valor fijo y `"potN"` es el pot N del pedal;
   - `pots` da los seis pots al cargar la cadena.
3. Si a la cadena solo le falta memoria, poner `requiere = "sdram"`.
   `model/tests/cadenas_test.py` exige que cada cadena quepa o que solo le falte memoria.
4. Escuchar con `sofifi cadena NOMBRE entrada.wav salida.wav`. La prueba de
   volumen falla si la cadena suena más del doble que el plate.
5. Para ver el programa compuesto, ejecutar `sofifi componer NOMBRE salida.sasm`.
6. Regenerar el catálogo con `sofifi catalogo`. La simulación del RTL recorre
   las cadenas que caben.
7. Para una demo, añadir la cadena en `DEMOS_CADENAS` (`scripts/generar_demos.py`).
8. Si la cadena cabe en `hil_nucleo`, probarla en la placa con `make hil HIL="NOMBRE"`.

## Una instrucción del núcleo

Una instrucción nueva es una decisión estructural. `model/sofifi/domain/isa.py`
es sentinela: el cambio va con su ADR o con una actualización del ADR 0009.

1. Añadir el valor en `Op` y, si cuesta más de un ciclo, en `CICLOS` (`model/sofifi/domain/isa.py`).
2. Escribir el manejador en `model/sofifi/domain/nucleo.py` y registrarlo en `MANEJADORES`.
3. Añadir el mnemónico y sus operandos en `model/sofifi/domain/ensamblador.py`.
   Los contratos de `model/tests/nucleo_test.py` y `model/tests/ensamblador_test.py`
   fallan si falta uno de los tres pasos.
4. Añadir sus ciclos de ejecución en `DURACION` (`model/sofifi/domain/coste.py`).
5. Si la instrucción lee el ACC o el banco de registros, añadirla también a `LEE_ACC` o a `LEE_REGISTRO`.
6. Añadir una línea en `MUESTRA_COSTE` (`sim/nucleo/nucleo_test.py`). La
   simulación exige los mismos ciclos que el modelo de tiempos, sola y junto a
   cada instrucción (ADR 0014).

## Un módulo RTL

1. Escribir primero el modelo, en `model/sofifi/domain/`.
2. Escribir el RTL en `rtl/`, con cabecera SPDX.
3. Escribir el testbench en `sim/`. Compara con el modelo muestra a muestra.
4. Si el módulo fija pines, relojes o el mapa de memoria, escribir su ADR en el
   mismo PR. Esos ficheros son sentinelas (`docs/adr/sentinelas.txt`).
5. Regenerar su esquemático con `make esquematicos` (ADR 0012).
6. Poner al día `docs/arquitectura_fpga.md` y `SBOM.md`, con sus traducciones.

## Un top

Un top es un diseño completo para la placa: los pines, el PLL y los módulos.

1. Escribir `rtl/top/<top>.v`. Los pines están en `rtl/top/primer25k.cst`.
2. Añadir una línea en `rtl/top/tops.txt` con el top y sus fuentes. La primera
   fuente define el top. El Makefile y la compuerta leen esta lista.
3. Añadir los listones `recursos:<top>:LUT4` y `recursos:<top>:ALU` en
   `docs/ratchets.yaml`, donde se está (ADR 0010).
4. Sintetizar y cargar con `make prog TOP=<top>`.
5. Si el top envía por la UART, limitar el caudal: si no, se cuelga el puente
   del BL616 (`rtl/AGENTS.md`).
6. Medir el margen de reloj en la placa, no en nextpnr (ADR 0011).

## Una compuerta

> **Advertencia.** `scripts/ci_local.sh` es una sentinela: un cambio en él va
> con su ADR o con una actualización de un ADR.

1. Añadir el script en `scripts/`.
2. Añadir una línea `"nombre:dura|blanda|release"` en el array `JOBS` de
   `scripts/ci_local.sh`, y su rama en `run_job`. El hook no se toca.
3. Declarar la clase:
   - dura, solo si todo el mundo puede ejecutarla y arreglarla hoy (P1);
   - release, si es cara y solo corre al nombrarla (`make release-check`, `make optimizacion`);
   - blanda, en los demás casos.
4. Si la compuerta lanza herramientas EDA, ponerla dentro de `(ulimit -u "$TOPE_PROCESOS"; …)`.

## Un ADR

1. Crear `docs/adr/<NNNN>-<regla-en-kebab>.md` con la estructura de
   `docs/adr/0001-la-compuerta-vive-en-el-repositorio.md`.
2. Añadir su fila al índice `docs/adr/README.md`. La compuerta `docs` comprueba
   que coinciden.

## Una fase

1. Escribir la spec en `docs/fases/` con las secciones fijas (SPEC_RAIZ §2.5).
2. **No** añadir la fase al control hasta cerrarla.
3. Al cerrarla, añadir su fila en `docs/fases/estado_fases.csv`, con el hallazgo y las enmiendas.
4. Subir la versión de los cuatro README a `0.<fase>`.
5. En el mismo PR, poner al día toda la documentación y las infografías en los
   cuatro idiomas. Rehacer las capturas con `scripts/capturar_infografia.py --todas`.
   La compuerta `cierre` lo comprueba.
