# ADR 0007 — El español es la fuente; las traducciones llevan sello

- **Estado:** Aceptado · 2026-10-07
- **Revisión prevista:** cuando la interfaz del pedal (OLED) tenga textos. Se añadirá la compuerta de catálogos espejados.

## Contexto

La persona propietaria pide el proyecto en tres idiomas: español, inglés y chino simplificado. Dos documentos que cuentan lo mismo divergen solos, y el que se queda atrás miente con toda la confianza del mundo (SPEC_RAIZ P8). A la vez, una compuerta que exige escribir chino a quien no lo sabe es inarreglable (P1).

## Opciones evaluadas

1. Traducciones libres sin control.
2. Compuerta que exige las tres versiones al día en cada cambio.
3. Una fuente canónica más traducciones selladas con el hash de la fuente que traducen.

## Decisión

Opción 3.

**Documentos**
- El español es canónico.
- Cada traducción (`<doc>.en.md`, `<doc>.zh-CN.md`) empieza con un sello: `<!-- i18n: fuente=<ruta> sha=<12 hex> estado=al_dia|desactualizada -->`.
- `scripts/check_i18n.py` (compuerta dura) bloquea solo **la mentira**: `estado=al_dia` con un `sha` que ya no coincide con la fuente.
- Una traducción marcada `desactualizada` pasa, y la portada lo muestra.
- `scripts/check_i18n.py --sellar <traducción>` vuelve a sellar tras actualizarla.

**Alcance**
- Se traducen los documentos de portada: el README.
- Los ADR, las specs de fase y los mapas para agentes se quedan en español, y se declara así.

**Producto**
- Los textos de la interfaz se definirán por clave en un catálogo por idioma (`es`, `en`, `zh-CN`).
- Habrá un test-contrato que compruebe que las tres tienen las mismas claves (SPEC_RAIZ §4.3 n.º 5).
- El chino en una OLED de 128×64 necesita una fuente de mapa de bits CJK reducida a los glifos usados, generada desde el catálogo.

## Consecuencias

- Cambiar el README obliga a decidir en el mismo PR: actualizar las traducciones y resellarlas, o marcarlas `desactualizada`.
- El coste de añadir un idioma es una traducción sellada más su código en `scripts/check_i18n.py`.

## Alternativas descartadas

- **Sin control:** la traducción envejece en silencio.
- **Todo al día obligatorio:** es inarreglable para quien no escribe chino, y acabaría desactivándose.
