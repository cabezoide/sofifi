# ADR 0009 — Una instrucción cabe en tres columnas de BSRAM (ISA de 54 bit)

- **Estado:** Aceptado · 2026-10-07
- **Revisión prevista:** cuando el RTL del núcleo sintetice. Si el decodificador o el CHO de 4 ciclos no cierran a 100 MHz, se revisa el formato.

## Contexto

El núcleo ejecuta programas tipo FV-1 (ADR 0006) con coeficientes de 18 bit y una memoria de 43 008 palabras (ADR 0008). Un campo de coeficiente de 18 bit más una dirección de 16 bit o más no caben en 36 bit (512×36). La BSRAM del GW5A se configura de forma natural en columnas de 18 bit.

## Opciones evaluadas

1. Palabra de 36 bit con coeficientes de 14 bit, como el FV-1. Pierde precisión en los coeficientes de decay y de filtros.
2. Palabra de 54 bit: tres columnas de 1K×18 por cada 1 024 instrucciones, es decir 6 bloques para 2 048 instrucciones.
3. Dos palabras por instrucción. Duplica los ciclos.

## Decisión

Opción 2, implementada en `model/sofifi/domain/isa.py`.

**Campos de la palabra**

| Campo | Bits |
|---|---|
| `op` | 6 |
| `reg` | 6 |
| `flags` | 6 |
| `coef` | 18 (S1.16) |
| `addr` | 18 (sin signo para memoria y saltos; S2.15 para el D de `SOF`) |

**Instrucciones (16)**
- Subconjunto del FV-1: `RDA`, `WRA`, `WRAP`, `RDAX`, `WRAX`, `RDFX`, `MAXX`, `MULX`, `SOF`, `SKP`, `LDAX`, `CLR`, `ABSA`, `NOP`.
- Extensiones:
  - `CLIP`: saturación suave entera.
  - `CHO`: lectura modulada con Hermite de 4 puntos. Opcionalmente aplica una ventana triangular y media fase, que son las piezas del pitch shifter de doble tap. Su sintaxis **no** es la del `CHO` del FV-1.

**Costes y límites**
- Cada instrucción cuesta 1 ciclo, salvo `CHO`, que cuesta 4 (cuatro lecturas de memoria).
- Un programa no supera 2 048 instrucciones ni 2 048 ciclos por muestra. Lo valida `Programa`.

**Por muestra**
- `ACC = 0` y `LR = 0` al empezar.
- Los LFO avanzan con los registros `lfoN_rate` y `lfoN_depth` de la muestra anterior.

**Registros (64)**
- `reg0`–`reg31` de propósito general.
- `adcl`, `adcr`, `pot0`–`pot5` y `sw`, de solo lectura.
- `dacl` y `dacr`.
- `lfoN_rate` y `lfoN_depth`.

**Despacho**
- Una tabla `Op → manejador` (`MANEJADORES` en `model/sofifi/domain/nucleo.py`).
- Un test-contrato comprueba que toda instrucción tiene manejador y coste.

## Consecuencias

- Los programas `.spn` sin `CHO` se ensamblan casi tal cual. Los que usan `CHO` hay que reescribirlos.
- La palabra de 54 bit deja 6 bloques de BSRAM para el microcódigo; es lo que ajustó la reserva del ADR 0004.

## Alternativas descartadas

- **36 bit:** los coeficientes de 14 bit limitan los decays largos (feedback ≈ 0,9999).
- **Dos palabras:** a la mitad de instrucciones por muestra no cabe una plate con shimmer.

## Actualización 2026-10-07 (alcance de CHO, Fase 04)

Un `CHO` sobre la dirección `a` lee entre `a − 1` y `a + alcance + 1`, por el Hermite de 4 puntos. El alcance es 2·E para SIN y RND, y W para RAMP. Desde ahora `Programa` exige que la última dirección quepa en la memoria declarada (`alcance_cho` en `isa.py`).

Con eso, la dirección relativa queda en [−1, P−1] y el RTL la reduce con una sola corrección de ±P (`rtl/nucleo/memoria_retardo.v`), sin el módulo general que hace el modelo. plate, shimmer y freeze ya cumplían la condición; el shimmer queda en el límite (41 537 frente a 41 539 palabras).

## Actualización 2026-10-07 (RDAA y WRAA, Fase 07)

La memoria circular no puede guardar un loop: su puntero avanza en cada muestra y lo grabado se aleja hasta desaparecer. El looper y el granular de la Fase 07 necesitan **direccionamiento absoluto**. Se añaden dos instrucciones (la ISA pasa de 16 a 18; el campo `op` tiene sitio para 64):

| Instrucción | Op | Qué hace |
|---|---|---|
| `RDAA reg, C` | 16 | v = lectura lineal en la región absoluta; LR = v; ACC += v·C |
| `WRAA reg, C` | 17 | M_abs[i] = a24; ACC = a24·C |

**Región absoluta:** 32 768 palabras (unos 0,67 s) detrás de la memoria circular del programa, en las direcciones físicas [P, P + 32 768). El puntero circular no la toca. Existe solo si el programa usa `RDAA` o `WRAA`, y entonces `Programa` exige P + 32 768 ≤ 43 008: quedan 10 240 palabras de memoria circular. Se borra al salir del reset, como la circular.

**Dirección:** el registro R da la posición, con 15 bit de entero y 8 de fracción: `pos = R & 0x7FFFFF`, `i = (addr + (pos >> 8)) & 0x7FFF`, `f = pos & 0xFF`. El campo `addr` (0 a 32 767) desplaza el origen. El tamaño es una potencia de 2 para que el desborde sea una máscara y no un módulo: el programa mueve R sin preocuparse del final de la región.

**Interpolación lineal en `RDAA`:** `v = M[i] + (((M[i+1] − M[i])·f) >> 8)`, con `i + 1` también enmascarado. `WRAA` no interpola: escribe en `i`.

**Por qué así:**
- Un registro como dirección hace falta: la posición de reproducción la calcula el programa (velocidad ½×, 2×, reverse, granos).
- Lineal y no Hermite: dos lecturas en lugar de cuatro, y la ventana de los granos y el loop toleran el paso bajo leve de la interpolación lineal.
- Una región fija de 32 768 palabras: el RTL calcula la dirección física con una suma (P + i), sin la lógica de módulo del puntero circular.

**Descartado:** una región de tamaño variable (`buf N`): el desborde pediría un módulo general en el RTL; y usar los 43 008 completos: no hay potencia de 2 que quepa con memoria circular al lado.
