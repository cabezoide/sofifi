# Fase 01 — Modelo de referencia bit-exact del núcleo DSP

> Planificada: no está en el control hasta cerrarse.

## Objetivo

Tener un modelo Python bit-exact del núcleo microcodificado (ADR 0006), con su ensamblador y tres programas que se puedan escuchar con WAV de guitarra:

- un plate de Dattorro;
- un shimmer de doble tap;
- un freeze con limitador.

## Origen

ADR 0003 (el modelo es el oráculo), ADR 0004 (presupuesto de BSRAM), ADR 0005 (fs = 48 828 Hz) y ADR 0006 (núcleo tipo FV-1).

## Diagnóstico

- **Se reutiliza:**
  - las capas vacías de `model/sofifi/` y sus contratos;
  - las referencias de `docs/terceros.yaml` (T-003 Dattorro, T-004 FV-1, T-005 asfv1).
- **Falta:**
  - tipos de punto fijo;
  - memoria de delay con direccionamiento circular;
  - LFO y LFSR;
  - ISA y ensamblador;
  - adaptador WAV;
  - CLI de render.

## El hallazgo que decide el diseño

Un modelo en coma flotante no sirve de oráculo. En una reverb, el error de un LSB en el redondeo se realimenta y la cola diverge, así que el RTL nunca coincidiría y la comparación con tolerancia ocultaría los fallos reales. Por eso el modelo **ejecuta la ISA** con la aritmética exacta del hardware (Q, saturación, redondeo) en lugar de implementar cada efecto directamente.

## Diseño

1. **`domain`:**
   - formatos Q: datos s1.23, coeficientes s1.16 y acumulador de 48 bit;
   - saturación y redondeo;
   - memoria circular;
   - LFSR;
   - ISA (enum + tabla de despacho, con test-contrato de que cada instrucción tiene manejador);
   - intérprete.
2. **`ports`:** `FuenteAudio`, `SumideroAudio` y `FuenteParametros`.
3. **`adapters`:** WAV de 24 bit y volcado hex del microcódigo para el RTL.
4. **`services`:** procesar un fichero con un programa.
5. **`cli`:** `sofifi render --programa plate.asm entrada.wav salida.wav`.
6. **Ensamblador** con sintaxis compatible con `.spn` donde sea posible.

## Plan de PRs

0. Foto: tiempos de render y longitudes de delay reescaladas a 48 828 Hz.
1. Punto fijo + memoria circular + LFSR (dominio).
2. ISA + intérprete + contrato de despacho.
3. Ensamblador + adaptadores WAV y hex.
4. Programas plate, shimmer y freeze + CLI.
5. Documentación, registros (madurez M-03) y ADR si la ISA cambia lo decidido.

## Criterios de aceptación

- Dos ejecuciones producen el mismo WAV byte a byte.
- Un programa `.spn` sencillo del FV-1 ensambla y suena equivalente.
- Ningún programa supera 2 048 instrucciones ni las 45 056 palabras de delay.

## Lo que NO entra

RTL, granular, interfaz, microSD y SDRAM.
