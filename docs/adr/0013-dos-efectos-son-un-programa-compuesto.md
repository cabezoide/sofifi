# ADR 0013 — Dos efectos a la vez son un programa compuesto, no un segundo núcleo

- **Estado:** Aceptado · 2026-10-08
- **Revisión prevista:** al llegar la SDRAM (punto 24 de la hoja de ruta), o si el proyecto cambia a una FPGA más grande.

## Contexto

La persona propietaria quiere dos efectos a la vez, como el H90 (`docs/investigacion/ESTADO_DEL_ARTE_2026.md`). Un programa usa de 300 a 1 900 de los 2 048 ciclos por muestra, así que muchas parejas caben en ciclos. La pregunta es dónde se unen: en el hardware (otro núcleo) o en el programa.

Se midió el coste de más núcleos con la cadena de síntesis del proyecto (ADR 0011). Los tops de medida instancian el núcleo de `nucleo_placa` varias veces. Cada copia recibe el reset y el tick con un ciclo más de retraso, para que yosys no fusione su control.

| Núcleos | Retardo por núcleo | LUT4 antes de colocar | Flip-flops | BSRAM | Resultado de nextpnr |
|---|---|---|---|---|---|
| 1 (`nucleo_placa`) | 42 bloques | 7 186 (11 097 celdas tras empaquetar, RAT-11) | 6 565 | 48 de 56 | cabe; 125 MHz medidos en la placa |
| 2 | 22 bloques | 13 112 | 9 928 | 56 de 56 | **no se puede colocar** |
| 2 | 16 bloques | 12 877 | 8 968 | 44 de 56 | **no se puede colocar** |
| 3 | 12 bloques | 19 046 | 12 615 | 54 de 56 | **no se puede colocar** |

Con 2 núcleos falla también con la BSRAM al 78 %: el límite es la lógica. Cada núcleo empaqueta unas 11 000 celdas de las 23 040; dos llegan al 96 % antes de añadir la microSD, el códec, los mandos, la OLED y el controlador de SDRAM (Fases 08 a 12).

## Opciones evaluadas

1. **Segundo núcleo.** No cabe (tabla). Además, la memoria de retardo se reparte entre los dos, y la memoria es lo que limita las parejas más pedidas (delay y luego reverb).
2. **Tercer núcleo.** Necesitaría unas 33 000 celdas, un 144 % del chip [INF, por extrapolación de la tabla].
3. **Quitar las esperas del núcleo** (`docs/arquitectura_fpga.md`, «Próximo cambio previsto»). Casi duplicaría los ciclos útiles sin otra copia del núcleo. Es un cambio grande del RTL, con su ADR.
4. **Programa compuesto.** Un compositor une dos o más programas en un solo `.sasm`. No cambia la ISA ni el RTL.

## Decisión

Opción 4 ahora; la opción 3, después, si las cadenas piden más ciclos.

- `model/sofifi/domain/composicion.py` une programas en serie o en paralelo. A cada programa le da registros y LFOs propios y antepone `eN_` a sus nombres. Los mandos van a un pot físico o a una constante.
- **Contrato:** una cadena en serie da los mismos bits que procesar con el primer programa y después con el segundo (`model/tests/composicion_test.py`).
- Las cadenas están en `presets/cadenas.toml`. La simulación RTL recorre las que caben, como cualquier programa.
- La memoria la asigna el ensamblador en el orden de los `mem`. Cuando llegue la SDRAM y `mem` tenga un espacio de memoria, el compositor solo cambia en la regla de `mem`.
- Una cadena que hoy no cabe solo por memoria lleva `requiere = "sdram"`. La prueba exige que solo le falte memoria. Así el banco ya sabe qué cadenas abre la SDRAM.

## Consecuencias

- Los límites de una cadena son los de un programa: 2 048 ciclos, 43 008 palabras, 32 registros y 4 LFOs. Los LFOs y los registros también limitan: `chorus` y `plate` no caben juntos porque suman 5 LFOs.
- Hoy caben 213 de las parejas en serie medidas; delay y luego reverb casi nunca, por memoria. Esa pareja espera a la SDRAM.
- Una cadena sube el riesgo de saltos de volumen (fails.md, F-23). Toda cadena pasa una prueba de nivel frente al plate.
- Un segundo núcleo vuelve a estudiarse solo con una FPGA más grande. Su ventaja real no es el cálculo: es cambiar de preset sin cortes.

## Actualización 2026-10-08 · Registros temporales compartidos

- **Medida:** de las 2 550 parejas en serie de los 51 programas, 904 no cabían por registros. El 61 % de los registros de los programas (326 de 530) son temporales: el programa los escribe antes de leerlos en cada muestra.
- **Cambio:** el compositor ya no da registros propios a todo. Cada programa conserva sus registros persistentes. Los temporales salen de un grupo común a todos los programas de la cadena (`registros_temporales` en `composicion.py`).
- **Por qué es seguro:** los programas de una cadena corren uno detrás de otro. Un registro temporal no lleva nada de un programa al siguiente, porque cada uno lo escribe antes de leerlo. El análisis sigue todos los caminos de los `SKP`: si un salto puede evitar la escritura, el registro es persistente.
- **Contrato:** no cambia. En serie, la cadena da los mismos bits que dos pasadas; la prueba añade dos parejas con muchos temporales (`filtro` y luego `resonador`, `compresor` y luego `freeze_givens`).
- **Resultado:** las parejas que no caben por registros bajan de 904 a 300.

## Actualización 2026-10-09 · La opción 3 ya está hecha

- **Qué cambió:** la opción 3 (quitar las esperas del núcleo) es el ADR 0014, aceptado el 2026-10-09. El núcleo solo espera cuando una instrucción depende de otra.
- **Efecto en las cadenas:** con los 51 programas de entonces, las parejas en serie que caben pasaron de 790 a 1 312 de 2 550 (ADR 0014).
- **Medida de hoy (86 programas):** caben 2 611 de las 7 310 parejas en serie. Una pareja puede pasarse en varios límites a la vez:

  | Límite que se pasa | Parejas |
  |---|---|
  | memoria | 3 590 |
  | ciclos | 1 684 |
  | registros | 1 616 |
  | LFOs | 1 200 |
  | región absoluta | 156 |

- **Consecuencia:** la memoria limita más que los ciclos. La palanca siguiente es la SDRAM (punto 24 de la hoja de ruta), no otro cambio del núcleo.
- **La decisión no cambia:** dos efectos a la vez siguen siendo un programa compuesto. El segundo núcleo sigue descartado en la 25K: la persona propietaria lo confirmó el 2026-10-08.
- **Cómo se midió:** cada pareja ordenada de programas distintos, en serie, con `recursos()` de `model/sofifi/domain/composicion.py` y los mandos en los pots físicos.
