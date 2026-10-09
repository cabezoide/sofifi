# Seguridad

## Modelo de amenazas (versión 0.7)

El pedal es un dispositivo **standalone, sin red**. Sus entradas no confiables son:

1. **Ficheros de la microSD:** presets, microcódigo y tablas. Puede escribirlos cualquiera que tenga la tarjeta.
2. **MIDI IN** (futuro).
3. **La señal de audio.** No es un vector de ataque, pero sí de daño: un feedback o un freeze descontrolado puede producir niveles peligrosos para el oído y el equipo.

## Controles

| Control | Estado |
|---|---|
| Saturación explícita en toda la aritmética DSP (ADR 0003, ADR 0008) | hecho |
| Banco de microcódigo en la microSD sin sistema de ficheros: bloques crudos, límites de cada campo y CRC-32 antes de cargar (`docs/microsd.md`) | hecho en el modelo y en el RTL; probado en simulación; falta la tarjeta real (Fase 08) |
| Carga en dos pasadas: el núcleo no se toca hasta validar toda la ranura | hecho, como el anterior |
| Parser de presets de texto con validación de longitud | previsto (Fase 08, punto 16 de la hoja de ruta) |
| Limitador de seguridad fijo en la salida, fuera del microcódigo programable | previsto (Fase 12) |

## Repositorio

- **Higiene de secretos:** `scripts/check_secrets_hygiene.sh` (compuerta dura).
- **Origen y licencia del código ajeno:** `docs/terceros.yaml` + `scripts/check_licenses.py`.

El mapeo completo, con los huecos primero, está en `docs/security/CUMPLIMIENTO.md`.

## Reportar un problema

Abrir un issue privado o escribir a la persona mantenedora del repositorio.
