# ADR 0010 — Cada PR pasa una segunda vuelta de optimización

- **Estado:** Aceptado · 2026-10-07
- **Revisión prevista:** cuando la síntesis de los tops supere 60 s; entonces `optimizacion` pasa a compuerta de release y la segunda vuelta usa `make optimizacion`.

## Contexto

La primera versión de `hola_uart` (Fase 02) pasó todas las compuertas y funcionó en la placa, pero ocupaba 353 LUT4 y 146 ALU. Convertía a ASCII los ocho nibbles del contador con sumadores en paralelo y después elegía uno. Elegir primero el nibble y convertirlo una sola vez dejó el diseño en 207 LUT4 y 82 ALU. Nadie lo habría notado si la persona propietaria no hubiera preguntado.

Con el núcleo DSP (Fase 03) el área y el timing pasan a ser el límite real del proyecto: 23 040 LUT4, 56 BSRAM y 2 048 ciclos por muestra (ADR 0005). Lo que no se mira antes de fusionar acaba heredándose.

## Opciones evaluadas

1. Revisión manual, sin apoyo. Depende de que alguien pregunte.
2. Solo ratchets de recursos. Impiden empeorar, pero no ayudan a encontrar lo que sobra.
3. Una compuerta dura con tres piezas (timing, listones, pistas) y una segunda vuelta obligatoria en cada PR.

## Decisión

Opción 3.

- **Trabajo `optimizacion` (duro)**, en `scripts/check_optimizacion.py`. Sintetiza cada top de `rtl/top/tops.txt`:
  - **bloquea** si un reloj no alcanza su objetivo;
  - imprime **pistas** heurísticas, que no bloquean.
- **Pistas de hoy:**
  - más ALU que DFF: aritmética duplicada o calculada en paralelo;
  - más MUX2 anchos que media LUT4 por cada una: se elige entre resultados ya calculados;
  - timing cerrado con menos del 20 % de margen.

  Las dos primeras saltan con la versión inicial de `hola_uart` y no con la corregida.
- **Listones de recursos** en `docs/ratchets.yaml`, con medidas `recursos:<top>:<celda>`, que aplica `ratchets`. La síntesis es determinista, así que `aviso_holgura: 0`: cualquier mejora obliga a bajar el listón.
- **Segunda vuelta:** antes de abrir un PR se ejecuta `make optimizacion` y se rellena la sección «Segunda vuelta» de `.github/pull_request_template.md`. Cada pista se optimiza o se justifica, y se anota qué se miró, aunque no se cambie nada.
- `rtl/top/tops.txt` es la lista única de tops. La leen el Makefile, `scripts/ci_local.sh` y las dos comprobaciones.

## Consecuencias

- Cada push paga una síntesis por top: hoy 4 s.
- Las pistas pueden dar falsos positivos. Un diseño aritmético de verdad (el núcleo) tendrá más ALU que DFF. Si una pista se justifica en dos PRs seguidos, se afina su umbral con motivo y no se ignora.
- La segunda vuelta del modelo y de los scripts es revisión, no compuerta: tiempos (MED-01, MED-02) y código duplicado.

## Alternativas descartadas

- **Exigir un porcentaje de área fijo por top:** no hay referencia hasta que exista el núcleo, y un listón inventado contradice P9.
