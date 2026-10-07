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
