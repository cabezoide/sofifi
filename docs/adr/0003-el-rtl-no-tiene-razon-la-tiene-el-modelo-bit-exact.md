# ADR 0003 — El RTL no tiene razón: la tiene el modelo bit-exact

- **Estado:** Aceptado · 2026-10-07
- **Revisión prevista:** si un bloque resulta imposible de modelar bit a bit (por ejemplo, la interfaz asíncrona con la SD).

## Contexto

Una reverb es un sistema con realimentación. Un error de un LSB en un redondeo no se ve en una prueba corta y diverge en la cola. Comparar el RTL contra un modelo en coma flotante con tolerancia no detecta esos errores: la diferencia legítima del redondeo tapa la del fallo.

## Opciones evaluadas

1. Modelo en float y comparación con tolerancia.
2. Modelo **bit-exact** en punto fijo y comparación con tolerancia cero.
3. Verificar a oído en hardware.

## Decisión

Opción 2. El modelo de `model/ambient/` reproduce la aritmética del hardware: formatos Q, saturación, redondeo y LFSR. Es el oráculo, y cada bloque RTL se compara muestra a muestra en `sim/`.

El modelo sigue arquitectura hexagonal: dominio, puertos, adaptadores, servicios y cli. Lo comprueba `model/tests/arquitectura_test.py`.

## Consecuencias

- Todo bloque DSP se escribe dos veces: primero el modelo, después el RTL.
- El modelo sirve también para **escuchar** los algoritmos con WAV de guitarra antes de tener el hardware.
- No hay frontend web, así que §6 de SPEC_RAIZ no aplica. Si la interfaz del pedal (OLED) llega a tener una capa propia, se le aplicarán las reglas de catálogos del ADR 0007.

## Alternativas descartadas

- **Float con tolerancia:** no detecta los errores de redondeo realimentados.
- **A oído:** no es reproducible y no sirve como compuerta.

## Actualización 2026-10-07 (nombre del proyecto)

El proyecto pasa a llamarse **SOFIFI** y el paquete del modelo se renombra de `ambient` a `sofifi` (`model/sofifi/`). La decisión no cambia; solo el nombre. Se hizo con el paquete aún vacío para que el cambio fuera barato.
