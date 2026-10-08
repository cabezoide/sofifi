# ADR 0014 — El núcleo solo espera cuando una instrucción depende de otra

- **Estado:** Propuesto · 2026-10-08
- **Revisión prevista:** si un programa necesita más ciclos de los que da este diseño, o si se baja la latencia del multiplicador (`LAT`).

## Contexto

Hasta la Fase 07, cada instrucción esperaba a su resultado antes de empezar la siguiente. Un `RDAX` gastaba 10 ciclos, aunque el multiplicador solo tarda 5 (`LAT`). Los programas grandes usaban hasta 1 942 de los 2 048 ciclos por muestra. Así, casi ninguna cadena de dos efectos grandes cabía en ciclos (ADR 0013).

El ADR 0013 dejó una opción para después: quitar las esperas del núcleo. Un segundo núcleo no cabe en la 25K.

Se midió primero con un modelo de tiempos (fuera del repositorio) qué ganancia da cada diseño. Los programas tienen muchas cadenas de dependencias (`rda` y luego `wrap`), así que la ganancia está limitada por la latencia:

| Diseño | Ciclos, en media (todos los programas y cadenas) |
|---|---|
| Multiciclo (hasta la Fase 07) | 1× |
| Retiro desacoplado, sin cola de búsqueda | 1,37× menos |
| Retiro desacoplado y cola de búsqueda | 1,62× menos |
| Lo mismo y lectura de memoria adelantada | 1,75× menos |
| Lo mismo y `LAT` = 3 | 2,08× menos |

## Opciones evaluadas

1. **Seguir multiciclo.** Sin riesgo de timing, pero las cadenas grandes no caben.
2. **Segmentado en orden con retiro desacoplado y cola de búsqueda.** La instrucción deja su producto en una línea de retiro y no espera. El ACC se escribe en el orden del programa. Solo espera la instrucción que lee el ACC o un registro recién escrito.
3. **Lo mismo y lectura de memoria adelantada.** La lectura de un `RDA` empezaría antes de su turno. Hay que comparar direcciones con las escrituras pendientes. Gana un 8 % más con bastante más lógica de control.
4. **Bajar `LAT` a 3.** El multiplicador perdería registros. Con el historial de timing del GW5A (fails.md, F-11), el riesgo es alto.

## Decisión

Opción 2.

- **Línea de retiro:** la instrucción que presenta su último producto lo marca. Su código, un operando (LR en `WRAP`, D en `SOF`, R en las demás) y el pc llegan a la ALU junto al producto. La ALU escribe el ACC un ciclo después.
- **Orden del ACC:** las escrituras del ACC van siempre en el orden del programa. La saturación no es asociativa, así que el orden es parte del contrato (ADR 0008).
- **Acumulación sin espera:** `RDA`, `RDAX`, `CHO` y `RDAA` toman el ACC en la segunda etapa de la ALU. Dos retiros seguidos ven el ACC al día.
- **Dependencias:** una instrucción que lee el ACC o `a24` no se decodifica hasta que el retiro está vacío. Una que lee el banco espera 3 ciclos tras un `WRAX`.
- **Cola de búsqueda:** el microcódigo se pide sin parar. Una cola de 4 palabras y una cabeza registrada dan la instrucción siguiente. Un `SKP` que salta vacía la cola.
- **El modelo de tiempos es exacto:** `model/sofifi/domain/coste.py` reproduce el secuenciador. La simulación exige el mismo número de ciclos que el RTL en cada programa sin `SKP`, en cada instrucción y en cada pareja de instrucciones. Con `SKP`, el modelo es una cota.

## Consecuencias

- En media, los programas gastan 1,6 veces menos ciclos que con el diseño multiciclo (simulación RTL de los 51 programas y las 18 cadenas que caben). El hall baja de 1 578 a 856 ciclos.
- La salida no cambia: es la misma del modelo bit-exact en todos los programas (ADR 0003).
- Parejas en serie de los 51 programas que caben (ADR 0013): de 790 a 1 050 de 2 550. Las parejas que no caben por ciclos bajan de 1 474 a 315. Ahora limitan más la memoria (1 046 parejas) y los registros (904).
- Coste en el top `hil_nucleo`: +559 LUT4 (+4,7 %) y +432 flip-flops, sobre todo por la cola y la línea de retiro.
- El coste de una instrucción depende de las anteriores. Para ahorrar ciclos, un programa agrupa las instrucciones que no leen el ACC (`rdax`, `rda`) antes de la que lo lee (`wrax`, `wrap`).
- La traza del HIL da el pc de la instrucción siguiente a la que escribió el ACC. El significado es el mismo que antes.
- El margen de reloj se mide en la placa antes de aceptar (ADR 0011).
