# Fase 07 — Carga de programas desde la microSD

> Planificada: no está en el control hasta cerrarse.

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
  - Capacidad: unos 4 millones de ranuras en 64 GB. El límite de la biblioteca no es la tarjeta.
- **Herramienta:** `sofifi banco programas/*.sasm salida.img`, y una guía para escribir la imagen con `dd`.
- **RTL:** `rtl/sd/sd_spi.v` y `rtl/sd/cargador.v`, que verifica antes de escribir.

## Plan de PRs

1. Formato y herramienta en el modelo, con property tests de que un banco corrupto se rechaza.
2. RTL SD SPI con un modelo de tarjeta en cocotb.
3. Prueba en hardware con la microSD de 64 GB, informando por UART.

## Criterios de aceptación

- Un banco corrupto (bit volteado o longitud fuera de rango) se rechaza en el modelo y en el RTL.
- En la placa, el cargador lee la cabecera de la tarjeta real.

## Lo que NO entra

FAT, escritura en la SD, looper en streaming.
