# Fase 11 — Integración del pedal y limitador de seguridad

> Planificada: no está en el control hasta cerrarse.

## Objetivo

Integrar todo en un único top para la placa:
- audio I2S → núcleo → limitador de seguridad fijo → DAC;
- controles, presets desde SD, OLED y bypass.

Ha de caber, cerrar timing y tener su compuerta de release.

## Origen

SECURITY.md (limitador de salida fuera del microcódigo) y todas las fases anteriores.

## Diagnóstico

- **Se reutiliza:** todos los bloques de las fases 02 a 10.
- **Falta:**
  - top integrado;
  - limitador fijo;
  - lógica de bypass y *trails*;
  - compuerta de release `make release-check` (síntesis + timing + recursos dentro de los ratchets);
  - guía de montaje del hardware.

## El hallazgo que decide el diseño

El microcódigo lo escribe cualquiera que tenga la SD (SECURITY.md), así que **ningún programa puede ser lo último antes del DAC**. Un limitador fijo en RTL, con techo y velocidad de ataque no programables, es la única garantía contra un feedback que dañe oídos o equipo. Se verifica con pruebas de **rechazo**: un programa malicioso que satura a ±1 no supera el techo.

## Diseño

- **`rtl/top/sofifi.v`:**
  - I2S → núcleo → `limitador.v` → I2S;
  - bypass con *crossfade* de 10 ms;
  - SD → cargador; controles → registros; OLED.
- **Recursos:** ratchets de LUT, DSP y BSRAM leídos del informe de síntesis.
- **`make release-check`:** síntesis, timing a 100 MHz, ratchets, HIL del núcleo por UART (si la placa está conectada) y compuerta dura completa.

## Plan de PRs

1. Limitador en modelo y RTL, con pruebas de rechazo.
2. Top integrado y bypass.
3. Release-check, guía de hardware y ratchets de recursos.

## Criterios de aceptación

- La síntesis del top cabe en la GW5A-25 con margen declarado.
- Timing a 100 MHz.
- El limitador no supera su techo con ningún programa.
- `make release-check` existe y pasa con la placa conectada.

## Lo que NO entra

PCB y caja: se planificarán en una fase posterior con el front-end analógico.
