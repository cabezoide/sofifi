# Fase 08 — Carga de programas desde la microSD

> **En curso** (2026-10-09). No está en el control hasta cerrarse. Los tres PRs del plan están hechos y probados en simulación. **Falta la prueba con la tarjeta real** (sección «Estado»).

## Objetivo

Que el pedal cargue el microcódigo de un banco de presets guardado en la microSD (ADR 0004) y lo valide con CRC antes de ejecutarlo (SECURITY.md).

## Origen

ADR 0004 (la microSD almacena) y el hueco de CUMPLIMIENTO.md: ficheros de la SD sin validar.

## Diagnóstico

- **Se reutiliza:** el puerto de escritura del microcódigo y `sofifi asm`.
- **Falta:**
  - controlador SD en modo SPI (inicialización CMD0/CMD8/ACMD41, lectura de bloques CMD17);
  - formato de banco;
  - herramienta del PC que escriba la imagen;
  - pines del PMOD TF.

## El hallazgo que decide el diseño

Un sistema de ficheros FAT en RTL es caro y su parser es superficie de ataque (CWE-20/787). La SD se usa en **bloques crudos** con un formato propio: cabecera, CRC32 por programa y longitudes acotadas. Se escribe desde el PC con `sofifi banco`, que comprueba los mismos límites que `Programa`. Un banco inválido no se carga, y el pedal sigue con el programa anterior.

## Diseño

- **Formato:** bloques crudos de 512 bytes, con **ranuras de tamaño fijo**.
  - Bloque 0: cabecera `SOFIFI` + versión + número de programas.
  - El programa *k* ocupa la ranura que empieza en el bloque `1 + 28·k`. Son 28 bloques:
    - 1 bloque de metadatos: nombre, número de instrucciones (≤ 2 048), memoria, LFOs y CRC32 de metadatos y microcódigo;
    - 27 bloques de microcódigo: 2 048 × 54 bit = 13 824 bytes, exactamente 27 bloques, con las palabras empaquetadas.
  - El cargador solo lee los bloques que ocupa el programa: el plate, de unas 100 instrucciones, cabe en 2 bloques de microcódigo.
  - La posición se deduce del índice y nunca se lee de la tarjeta. El cargador no sigue punteros escritos por terceros; solo comprueba `k < número de programas ≤ máximo` y la longitud declarada.
  - Capacidad: el banco admite hasta 1 024 programas (`MAX_PROGRAMAS`), unos 14 MB. Una tarjeta de 64 GB tendría sitio para unos 4 millones de ranuras: el límite de la biblioteca no es la tarjeta.
- **Herramienta:** `sofifi banco salida.img [NOMBRE...]`. Sin nombres, el banco lleva todos los programas y cadenas que caben. `sofifi banco --leer salida.img` comprueba una imagen. La guía para escribirla con `dd` está en `docs/microsd.md`.
- **RTL:**
  - `rtl/sd/sd_spi.v`: arranque SPI (CMD0, CMD8, ACMD41, CMD58) a 400 kHz y lectura de bloques con CMD17 a 12,5 MHz. Solo tarjetas de la versión 2.
  - `rtl/sd/cargador.v`: dos pasadas. La primera valida sin tocar el núcleo; la segunda para el núcleo, escribe y vuelve a comprobar el CRC.
  - `rtl/sd/carga_sd.v`: une los dos módulos.
  - `rtl/top/prueba_sd.v`: top de prueba sin el núcleo. Prueba las dos revisiones del PMOD TF (v2 y v1) y responde por la UART a `scripts/prueba_sd.py`.

## Plan de PRs

| PR | Contenido | Estado |
|---|---|---|
| 1 | Formato y herramienta en el modelo, con property tests de que un banco corrupto se rechaza | hecho (a668f59) |
| 2 | RTL SD SPI y cargador, con un modelo de tarjeta en cocotb (`sim/sd/tarjeta_sd.py`) | hecho (bdbf577) |
| 3 | Top `prueba_sd` para la tarjeta real en el PMOD TF (J6), con informe por la UART | hecho en simulación (1eef7de); falta la tarjeta real |

## Criterios de aceptación

| Criterio | Estado |
|---|---|
| Un banco corrupto (bit volteado o longitud fuera de rango) se rechaza en el modelo y en el RTL. | cumplido en el modelo y en la simulación del RTL |
| En la placa, el cargador lee la cabecera de la tarjeta real. | pendiente |

## Estado

Para cerrar la fase falta la prueba en la placa:

1. Escribir el banco en la microSD de 64 GB (`docs/microsd.md`).
2. Cargar el top con `make prog TOP=prueba_sd`.
3. Ejecutar `.venv/bin/python scripts/prueba_sd.py --imagen build/banco.img`.
4. Anotar el resultado: una medición en `docs/mediciones.yaml` y, si algo falla, una entrada en `fails.md`.

## Ampliaciones de la Fase 03

Punto 16 de la hoja de ruta (`docs/investigacion/ESTADO_DEL_ARTE_2026.md`, hoja de ruta): **presets de texto** en la microSD. Un preset guarda todo el estado: programa, mandos, segunda capa, rampas y asignación de expresión. El microcódigo sigue en el banco binario con CRC; el preset es un fichero aparte que se puede leer y compartir.

## Lo que NO entra

FAT, escritura en la SD, looper en streaming.
