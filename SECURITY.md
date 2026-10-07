# Seguridad

## Modelo de amenazas (versión 0.0)

El pedal es un dispositivo **standalone, sin red**. Sus entradas no confiables son:

1. **Ficheros de la microSD:** presets, microcódigo y tablas. Puede escribirlos cualquiera que tenga la tarjeta.
2. **MIDI IN** (futuro).
3. **La señal de audio.** No es un vector de ataque, pero sí de daño: un feedback o un freeze descontrolado puede producir niveles peligrosos para el oído y el equipo.

## Controles previstos

- Parsers de presets y microcódigo con validación de longitud y CRC antes de cargar.
- Limitador de seguridad fijo en la salida, fuera del microcódigo programable.
- Saturación explícita en toda la aritmética DSP (ADR 0003).

## Repositorio

- **Higiene de secretos:** `scripts/check_secrets_hygiene.sh` (compuerta dura).
- **Origen y licencia del código ajeno:** `docs/terceros.yaml` + `scripts/check_licenses.py`.

El mapeo completo, con los huecos primero, está en `docs/security/CUMPLIMIENTO.md`.

## Reportar un problema

Abrir un issue privado o escribir a la persona mantenedora del repositorio.
