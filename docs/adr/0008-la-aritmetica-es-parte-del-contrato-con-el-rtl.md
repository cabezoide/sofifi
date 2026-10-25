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

## Actualización 2026-10-07 (intérprete más rápido, Fase 06)

`saturar`, `saturar_acc` y `acc_a_dato` se escriben con comparaciones y constantes ya calculadas, no con `min`/`max` y llamadas encadenadas. El intérprete tarda la mitad: la biblioteca pasa de 30 programas y sus pruebas corren en cada push. **El contrato no cambia:** una prueba de propiedades (`model/tests/aritmetica_test.py`) exige que las versiones rápidas den lo mismo que la definición general, y las huellas de los 30 programas no cambian.

## Actualización 2026-10-25 (palabras de memoria de 12 bit, Fase 14)

Un programa puede pedir palabras de memoria de **12 bit** con la directiva `palabra 12`, y entonces tiene 64 512 palabras de retardo (1,32 s) en lugar de 43 008 (0,88 s). Sin la directiva, 18 bit: los 86 programas de hoy no cambian ni un bit.

El formato es **lineal**, no de coma flotante, y eso cambia el punto 14 de la hoja de ruta. Se midió en el modelo la relación señal/ruido de la salida de programas reales contra la referencia de 18 bit:

| Programa | 12 bit flotante | 12 bit lineal | 9 bit μ-law | 9 bit lineal |
|---|---|---|---|---|
| `plate` | 49,3 dB | 45,5 dB | 37,5 dB | 27,2 dB |
| `cinta` | 59,0 dB | **63,3 dB** | 47,8 dB | 45,2 dB |
| `hall` | 51,9 dB | 47,8 dB | 40,2 dB | 29,6 dB |

La coma flotante gana unos 4 dB en las reverbs y **pierde** 4 dB en la cinta, que es el caso de uso de una línea larga: su contenido es fuerte, y una mantisa de 8 bit es menos precisa que 12 bit lineales. Lineal, además, no cuesta ni una LUT: es el mismo redondeo y la misma saturación de hoy, con otro tamaño.

Reglas que se añaden al contrato:

- **`dato_a_memoria` acepta el tamaño de palabra** (18 por omisión). Redondea medio LSB hacia arriba y satura, como siempre, y devuelve el valor alineado a dato.
- **Todo el programa usa el mismo tamaño**, también la región absoluta (ADR 0009). Un solo mapa de memoria en el RTL.
- **El límite de palabras sale del tamaño:** 42 bloques de BSRAM dan 1 024 palabras de 18 bit o 1 536 de 12.
- **Tres muestras de 12 bit ocupan dos palabras de 18.** Por eso una escritura obliga a leer, modificar y escribir, y eso cuesta ciclos. El modelo de tiempos declara el coste como una cota hasta que la simulación lo mida (ADR 0014).

Las palabras de 9 bit se midieron y se descartan: 37 dB en un tanque de reverb se oyen.
