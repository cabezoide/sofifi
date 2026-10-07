# Cómo extender

Paso a paso para cada tipo de pieza. Si añadir algo obliga a tocar un sitio que
no está en esta lista, la lista está incompleta: se corrige en el mismo PR.

## Un efecto (programa del núcleo)

Un efecto es un programa, no un módulo RTL (ADR 0006).

1. Si viene de un tercero, se añade la entrada en `docs/terceros.yaml`. `uso: portado`
   solo vale con licencia permisiva (ADR 0002).
2. Se escribe `programas/<nombre>.sasm`. La cabecera lleva `; familia:`,
   `; resumen:` y una línea `; potN = nombre` por mando. Los bloques que ya
   existen se toman de `programas/comun/` con `include`.
3. Se comprueba que cabe: `sofifi asm` da los ciclos del RTL, que deben ser
   2 048 o menos (`model/sofifi/domain/coste.py`).
4. Se escribe la prueba de su propiedad acústica en el fichero de su familia
   (`model/tests/programas_<familia>_test.py`). Las medidas comunes están en
   `model/tests/acustica.py`.
5. Se añade su huella en `HUELLAS` (`model/tests/programas_test.py`). Las
   pruebas de «cabe», de huella y de igualdad con el RTL (`sim/nucleo/nucleo_test.py`)
   recorren todos los `.sasm`: fallan si falta algo.
6. Se regenera el catálogo con `sofifi catalogo`.
7. Se añade la demo en `DEMOS` (`scripts/generar_demos.py`) y en
   `demo_examples/README.md`.

## Una instrucción del núcleo

Es una decisión estructural: `model/sofifi/domain/isa.py` es sentinela, así que va con su ADR o con una actualización del ADR 0009.

1. Se añade el valor en `Op` y, si cuesta más de un ciclo, en `CICLOS` (`model/sofifi/domain/isa.py`).
2. Se escribe el manejador en `model/sofifi/domain/nucleo.py` y se registra en `MANEJADORES`.
3. Se añade el mnemónico y sus operandos en `model/sofifi/domain/ensamblador.py`.
4. Los contratos de `model/tests/nucleo_test.py` y `model/tests/ensamblador_test.py` fallan si falta cualquiera de los tres pasos.
5. Se añade su coste en ciclos del RTL en `CICLOS_RTL` (`model/sofifi/domain/coste.py`) y una línea en `MUESTRA_COSTE` (`sim/nucleo/nucleo_test.py`). La simulación mide el coste y lo compara con la tabla.

## Un módulo RTL

1. Primero el modelo, en `model/sofifi/domain/`.
2. El RTL va en `rtl/`, con cabecera SPDX.
3. El testbench va en `sim/` y compara muestra a muestra.
4. Si es un top, va en `rtl/top/tops.txt` con sus fuentes y lleva listones
   `recursos:<top>:LUT4` y `recursos:<top>:ALU` en `docs/ratchets.yaml`, puestos
   donde se está (ADR 0010).
5. Si fija pines, relojes o el mapa de memoria, va con su ADR: esos ficheros son
   sentinelas (`docs/adr/sentinelas.txt`).

## Una compuerta

1. Se añade el script en `scripts/` y una línea `"nombre:dura|blanda|release"` en
   el array `JOBS` de `scripts/ci_local.sh`, más su rama en `run_job`. El hook no
   se toca.
2. La clase se declara: dura solo si todo el mundo puede correrla y arreglarla
   hoy (P1); release si es cara y solo corre al nombrarla (`make release-check`,
   `make optimizacion`).
3. Si lanza herramientas EDA, va dentro de `(ulimit -u "$TOPE_PROCESOS"; …)`.
4. Tocar `scripts/ci_local.sh` es una sentinela, así que va con su ADR o
   actualización de ADR.

## Un ADR

1. Se crea `docs/adr/<NNNN>-<regla-en-kebab>.md` a partir de la estructura de
   `docs/adr/0001-la-compuerta-vive-en-el-repositorio.md`.
2. Se añade la fila al índice `docs/adr/README.md`. La compuerta `docs` comprueba
   que coinciden.

## Una fase

1. Se escribe la spec en `docs/fases/` con las secciones fijas (SPEC_RAIZ §2.5).
2. **No** se añade al control hasta cerrarla. Al cerrar: fila en
   `docs/fases/estado_fases.csv` con el hallazgo y las enmiendas, y se sube la
   versión del README a `0.<fase>`.
