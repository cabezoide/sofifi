# Cómo extender

Paso a paso para cada tipo de pieza. Si añadir algo obliga a tocar un sitio que
no está en esta lista, la lista está incompleta: se corrige en el mismo PR.

## Un algoritmo DSP (efecto)

1. Si viene de un tercero, se añade la entrada en `docs/terceros.yaml`. `uso: portado`
   solo vale con licencia permisiva (ADR 0002).
2. Se escribe el modelo bit-exact en `model/sofifi/domain/`, con pruebas en
   `model/tests/`.
3. Mientras no exista el núcleo microcodificado (ADR 0006), el efecto se queda
   en el modelo. Cuando exista, el efecto será un programa del núcleo con su
   prueba de equivalencia.

## Un módulo RTL

1. Primero el modelo, en `model/sofifi/domain/`.
2. El RTL va en `rtl/`, con cabecera SPDX.
3. El testbench va en `sim/` y compara muestra a muestra.
4. Si fija pines, relojes o el mapa de memoria, va con su ADR: esos ficheros son
   sentinelas (`docs/adr/sentinelas.txt`).

## Una compuerta

1. Se añade el script en `scripts/` y una línea `"nombre:dura|blanda"` en el array
   `JOBS` de `scripts/ci_local.sh`, más su rama en `run_job`. El hook no se toca.
2. La clase se declara: dura solo si todo el mundo puede correrla y arreglarla
   hoy (P1).
3. Tocar `scripts/ci_local.sh` es una sentinela, así que va con su ADR o
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
