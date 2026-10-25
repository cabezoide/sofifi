# Fase 13 — El pedal suena sin códec

> **En curso** (2026-10-24). No está en el control hasta cerrarse.
>
> **Hardware que hace falta:** dos resistencias, dos condensadores y un jack. Nada que haya que comprar como módulo.

## Objetivo

Oír en la placa cualquiera de los 86 programas, con una grabación de guitarra real, sin el códec I2S.

## Origen

- El criterio «suena con guitarra» de `docs/investigacion/ESTADO_DEL_ARTE_2026.md` sigue en «no», y las fases 09 a 11 esperan compras.
- Las pruebas acústicas de la Fase 06 encontraron cuatro fallos que ninguna huella vio (fails.md, F-18). Oír es una prueba.
- Meyer-Baese, *DSP with FPGAs*, §5.1 a §5.3: interpolación multitasa y filtros CIC de Hogenauer, sin multiplicadores.

## Diagnóstico

- **Se reutiliza:** el reloj de 100 MHz, que es 2 048 veces fs (ADR 0005); el núcleo; `rtl/sd/sd_spi.v`, que ya lee bloques con CMD17.
- **Falta:**
  - interpolador CIC y modulador sigma-delta, en el modelo y en el RTL;
  - formato de pista de audio en la microSD y la herramienta del PC que la escribe;
  - lector de pistas en RTL, con un búfer que absorba la latencia de la tarjeta;
  - top de audio y un pin de salida.

## El hallazgo que decide el diseño

El reloj es 2 048 veces fs. Con ese sobremuestreo, **un solo pin lleva audio** con más calidad de la que da el pin. La cadena correcta no es una PWM, porque su ruido queda en banda. Es una interpolación que aparta las imágenes y un modulador que aparta el ruido de cuantificación (ADR 0015).

El segundo hallazgo es de seguridad: con la entrada a escala plena, el modulador de segundo orden sale de su zona lineal. Un programa de la microSD puede saturar a ±1 (SECURITY.md). Por eso la entrada se recorta a ±13/16 **antes** del modulador, y no después.

## Diseño

- **Cadena** (ADR 0015): recorte → CIC `S = 2`, `R = 32` → mantenimiento ×64 → modulador de 2.º orden → 1 bit a 100 MHz.
- **Modelo:** `model/sofifi/domain/salida_1bit.py`. Es el oráculo (ADR 0003).
- **RTL:** `rtl/salida/cic_interp.v`, `rtl/salida/sigma_delta.v` y `rtl/salida/salida_1bit.v`.
- **Pista de audio en la tarjeta:** bloques crudos de 512 byte, como el banco de programas (Fase 08). Cabecera con magia, número de muestras y CRC-32; después, muestras de 16 bit con signo a fs. Sin sistema de ficheros y sin punteros escritos por terceros.
- **Filtro de salida:** dos secciones RC pasivas. Los valores van en `docs/audio_1bit.md` y en `BOM.md`, como material de laboratorio.

## Plan de PRs

| PR | Contenido | Estado |
|---|---|---|
| 1 | ADR 0015, modelo bit-exact de la cadena, RTL y testbench que compara el flujo de bits | en curso |
| 2 | Formato de pista, `sofifi pista`, lector en RTL con búfer y su testbench | pendiente |
| 3 | Top `audio_sd`, pin, filtro RC, guía de escucha y prueba en la placa | pendiente |

## Criterios de aceptación

| Criterio | Estado |
|---|---|
| El RTL da el mismo flujo de bits que el modelo, bit a bit. | pendiente |
| La relación señal/ruido en banda es de 100 dB o más entre −12 y −2 dBFS, medida en el modelo. | cumplido (ADR 0015) |
| Con la entrada a escala plena, los integradores del modulador no saturan. | cumplido (ADR 0015) |
| En la placa suena una pista de la microSD a través de un programa, sin cortes. | pendiente |
| El top cabe y cierra timing a 100 MHz, con su listón de recursos. | pendiente |

## Lo que NO entra

- La entrada de audio. Sin códec no hay entrada analógica; la fuente es la microSD. Una entrada por sigma-delta necesita su propio ADR.
- El limitador de seguridad, que es de la Fase 12.
- El estéreo. La salida de 1 bit es mono.
