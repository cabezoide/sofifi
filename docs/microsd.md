# Banco de programas en la microSD

El pedal carga sus programas desde la microSD (Fase 08, ADR 0004). La tarjeta no lleva sistema de ficheros: guarda un banco de bloques crudos que escribe `sofifi banco`. El formato está en `model/sofifi/domain/banco.py`.

> **Estado (2026-10-09).** El banco, el controlador SD y el top de prueba funcionan en simulación. Falta la prueba con una tarjeta real.

| Dato del banco | Valor |
|---|---|
| Tamaño de bloque | 512 bytes |
| Bloque 0 | cabecera: magia, versión, número de programas y CRC-32 |
| Ranura *k* | empieza en el bloque 1 + 28·*k*: 1 bloque de metadatos y 27 de microcódigo |
| Programas por banco | como máximo 1 024 (unos 14 MB de la tarjeta) |

## Lo que hace falta

- Una microSD o microSDHC/SDXC. Las tarjetas de la versión 1 (anteriores a 2006) no funcionan.
- Un lector de tarjetas en el PC.
- El módulo Sipeed PMOD TF en el conector J6 del Dock. El top de prueba reconoce las dos revisiones del módulo.

## Escribir el banco

> **Advertencia.** El paso 4 borra **todo** lo que hay en la tarjeta, también sus particiones. Si escribes en un dispositivo equivocado, borras ese disco. Comprueba el dispositivo dos veces antes del paso 4.

1. Genera la imagen:

   ```sh
   .venv/bin/sofifi banco build/banco.img
   ```

   Sin nombres, el banco lleva todos los programas y cadenas que caben. Para elegir, añade sus nombres: `sofifi banco build/banco.img plate hall "Eco y muelle"`.

2. Comprueba la imagen:

   ```sh
   .venv/bin/sofifi banco --leer build/banco.img
   ```

3. Mete la tarjeta en el lector del PC y busca su dispositivo:

   ```sh
   lsblk -o NAME,SIZE,MODEL,TRAN
   ```

   La tarjeta es el dispositivo con su tamaño (por ejemplo, 59,5 G para una de 64 GB) y `TRAN` igual a `usb` o `mmc`. Si el sistema montó alguna partición de la tarjeta, desmóntala con `umount`.

4. Escribe la imagen. Cambia `/dev/sdX` por el dispositivo del paso 3, **sin número de partición**:

   ```sh
   sudo dd if=build/banco.img of=/dev/sdX bs=512 conv=fsync status=progress
   ```

5. Saca la tarjeta del PC y ponla en el PMOD TF.

## Probar la tarjeta en la placa

1. Carga el top de prueba:

   ```sh
   make prog TOP=prueba_sd
   ```

2. Compara cada ranura con el modelo:

   ```sh
   .venv/bin/python scripts/prueba_sd.py --imagen build/banco.img
   ```

   El script dice qué revisión del PMOD TF respondió. Para cada ranura dice `igual` o `DISTINTO`. Con `--ranuras 0 3` prueba solo esas ranuras; con `--puerto`, otro puerto serie.

## Si algo falla

| Mensaje | Causa probable |
|---|---|
| `revisión del PMOD TF ninguna`, error `CMD0` | No hay tarjeta, el módulo no está en J6 o un contacto está mal. |
| error `CMD8` | La tarjeta es de la versión 1. Usa una microSDHC o microSDXC. |
| motivo `cabecera` | La tarjeta no tiene un banco: repite «Escribir el banco». |
| error `CMD17` o `token de datos` | La tarjeta no entrega el bloque. Comprueba los contactos y prueba otra tarjeta. |
| motivo `ranura fuera del banco` | Pediste una ranura que el banco no tiene. Con `--leer`, `sofifi banco` lista las ranuras. |
| motivo `CRC` | La tarjeta o la imagen están dañadas: vuelve a escribir la imagen. |
| motivo `CRC en la escritura` | La tarjeta dio otros datos en la segunda lectura. El núcleo queda parado. Repite la carga. |
