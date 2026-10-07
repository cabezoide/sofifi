# Fase 09 — Interfaz trilingüe en OLED

> Planificada: no está en el control hasta cerrarse.
>
> **Hardware que falta:** el módulo OLED SSD1306. La fase va al final del plan para avanzar antes en todo lo que no lo necesita; lo que dependa de él se declara `no_verificada`.

## Objetivo

Mostrar el preset, los parámetros y el estado en una OLED SSD1306 de 128×64, en español, inglés y chino simplificado. Así se cumple la parte de producto del ADR 0007.

## Origen

ADR 0007 (catálogos espejados y fuente CJK reducida).

## Diagnóstico

- **Se reutiliza:** controles (Fase 08) y nombres de presets (Fase 07).
- **Falta:**
  - catálogo de textos por idioma;
  - generador de la fuente de mapa de bits;
  - controlador I2C/SPI de la SSD1306;
  - test-contrato de que los catálogos tienen las mismas claves.

## El hallazgo que decide el diseño

Una fuente CJK completa no cabe en BSRAM: unos 7 000 glifos de 16×16 dan 1,8 Mbit. Pero la interfaz usa solo los caracteres de su catálogo, unos 100. El generador extrae **exactamente esos glifos** a una ROM pequeña. Si alguien añade texto chino nuevo, la compuerta exige regenerar la fuente; si no se regenera, sale rojo. Las fuentes de los glifos deben tener licencia libre: GNU Unifont tiene excepción de fuente y Zpix es OFL; se declaran en `docs/terceros.yaml`.

## Diseño

- **Catálogos:** `ui/catalogo.yaml`, con claves y textos `es` / `en` / `zh-CN`.
- **Generador:** `sofifi fuente`, que genera la ROM de glifos usados (8×16 latín, 16×16 CJK) más el índice.
- **RTL:**
  - `rtl/ui/ssd1306.v`, con el framebuffer en BSRAM (1 KB);
  - un "pintor" de texto que lee el catálogo en ROM.
- **Pruebas:**
  - contrato de claves espejadas;
  - contrato de que todo glifo usado está en la ROM;
  - render del framebuffer a PNG en el modelo, para revisarlo.

## Plan de PRs

1. Catálogo, contratos, generador de fuente y render a PNG.
2. RTL SSD1306 y pintor, con testbench.

## Criterios de aceptación

- Las tres pantallas de ejemplo se renderizan a PNG en los tres idiomas.
- Los contratos están en verde.
- El RTL coincide con el framebuffer del modelo.

## Lo que NO entra

Menús complejos, edición de presets en el pedal.
