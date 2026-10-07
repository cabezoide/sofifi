# ADR 0008 — La aritmética es parte del contrato con el RTL

- **Estado:** Aceptado · 2026-10-07
- **Revisión prevista:** con la primera síntesis del núcleo. Hay que confirmar que el redondeo y la saturación cierran timing a 100 MHz sin ciclos extra.

## Contexto

El modelo es el oráculo bit-exact del RTL (ADR 0003). Para que el RTL pueda coincidir con tolerancia cero, cada redondeo, cada saturación y cada tabla tienen que estar definidos como contrato. Si se dejan al criterio de numpy, de la libm o de quien escriba el Verilog, no hay oráculo posible.

## Opciones evaluadas

1. Formatos del FV-1 tal cual: ACC de 24 bit saturando en cada operación y coeficientes S1.14.
2. Formatos ajustados a los bloques DSP del GW5A (27×18 con ALU de 48 bit) y a la BSRAM (1K×18).

## Decisión

Opción 2, implementada en `model/sofifi/domain/aritmetica.py`.

**Formatos**

| Señal | Bits | Formato |
|---|---|---|
| Dato | 24 | S.23 |
| Coeficiente | 18 | S1.16 |
| ACC | 48 | S8.39: el producto dato × coeficiente entra sin pérdida y queda un margen de ±256 |

**Redondeo y saturación**
- Desplazamiento a la derecha: *floor*.
- Escrituras a 24 o 18 bit: redondeo *half up* y después saturación. Nunca hay *wrap*.

**Memoria de retardo**
- Palabras de 18 bit (S.17), alineadas a dato.
- **42 bloques = 43 008 palabras.**

**Tablas y fuentes deterministas**
- Hermite de 4 puntos y 256 fracciones, calculada con `Fraction` (exacta). Es ROM de un bloque.
- Saturación suave entera `y = (3x − x³)/2`, sin `tanh` de libm.
- Ruido: LFSR Galois de 32 bit (máscara `0xD0000001`), con semilla fija.
- LFO: fase de 24 bit. SIN = triángulo suavizado. RND = objetivo del LFSR con suavizado `>> 6`. RAMP = diente de sierra con ventana triangular.

## Consecuencias

- Los programas del FV-1 se ensamblan con más precisión. Los que dependen de saturar el ACC a 24 bit en pasos intermedios suenan distinto en sobrecarga. Está aceptado y documentado.
- Las pruebas property-based (hypothesis) son compuerta dura sobre estas reglas.
- `aritmetica.py` pasa a ser sentinela: cambiarlo cambia el contrato con el RTL.

## Alternativas descartadas

- **ACC de 24 bit del FV-1:** desperdicia la ALU de 48 bit y obliga a escalar a mano cada suma de taps.
- **`tanh` y `sin` de libm para las tablas:** no es portable bit a bit.
