# SPDX-License-Identifier: MIT
"""Aritmética de punto fijo del núcleo (ADR 0008): es parte del contrato con el RTL.

Formatos (convención FV-1: ``S<enteros>.<fraccionarios>``, el signo aparte):

========  ======  ==============  ==========================================
Señal     Bits    Formato         Notas
========  ======  ==============  ==========================================
dato      24      S.23            muestras y registros, rango [-1, 1)
coef      18      S1.16           rango [-2, 2); entra en el puerto de 18 bit
acc       48      S8.39           producto dato x coef sin pérdida (f23+f16)
memoria   18      S.17            líneas de retardo en BSRAM; alineado a dato
========  ======  ==============  ==========================================

Reglas de redondeo, todas con enteros de Python (sin *wrap* silencioso):

- desplazamiento a la derecha = *floor* (lo que hace el hardware gratis);
- ``redondear`` = sumar medio LSB y desplazar (*round half up*);
- toda escritura a 24 o 18 bit redondea y luego **satura**; nunca envuelve.
"""

from __future__ import annotations

from fractions import Fraction

DATO_BITS = 24
DATO_FRAC = 23
COEF_BITS = 18
COEF_FRAC = 16
ACC_BITS = 48
ACC_FRAC = DATO_FRAC + COEF_FRAC
MEM_BITS = 18

DATO_MAX = (1 << (DATO_BITS - 1)) - 1
DATO_MIN = -(1 << (DATO_BITS - 1))
UNO = 1 << DATO_FRAC  # 1.0 en S.23 (no representable: satura a DATO_MAX)

# Reloj (ADR 0005): 100 MHz / 2048 ciclos = 48 828,125 Hz exactos.
RELOJ_HZ = 100_000_000
CICLOS_POR_MUESTRA = 2048
FS_EXACTA = Fraction(RELOJ_HZ, CICLOS_POR_MUESTRA)
FS_WAV = 48828  # la cabecera WAV solo admite enteros


def saturar(valor: int, bits: int) -> int:
    """Recorta ``valor`` al rango con signo de ``bits`` bits.

    Con comparaciones y no con ``min``/``max``: el intérprete la llama millones
    de veces y así tarda la mitad. El resultado es el mismo.
    """
    maximo = (1 << (bits - 1)) - 1
    if valor > maximo:
        return maximo
    minimo = -1 - maximo
    return minimo if valor < minimo else valor


def redondear(valor: int, desplazamiento: int) -> int:
    """Desplaza a la derecha redondeando medio LSB hacia arriba."""
    if desplazamiento <= 0:
        return valor << -desplazamiento
    return (valor + (1 << (desplazamiento - 1))) >> desplazamiento


_MEDIO_COEF = 1 << (COEF_FRAC - 1)
ACC_MAX = (1 << (ACC_BITS - 1)) - 1
ACC_MIN = -(1 << (ACC_BITS - 1))


def acc_a_dato(acc: int) -> int:
    """ACC (S8.39) → dato (S.23): redondea y satura. Lo que ve un ``WRAX``.

    Es ``saturar(redondear(acc, COEF_FRAC), DATO_BITS)`` con las constantes ya
    calculadas: el intérprete la llama en casi cada instrucción.
    """
    v = (acc + _MEDIO_COEF) >> COEF_FRAC
    return DATO_MAX if v > DATO_MAX else (DATO_MIN if v < DATO_MIN else v)


def dato_a_acc(dato: int) -> int:
    """Dato (S.23) → ACC (S8.39) sin pérdida."""
    return dato << COEF_FRAC


def saturar_acc(acc: int) -> int:
    """``saturar(acc, ACC_BITS)`` con las constantes ya calculadas."""
    return ACC_MAX if acc > ACC_MAX else (ACC_MIN if acc < ACC_MIN else acc)


def mac(acc: int, dato: int, coef: int) -> int:
    """``acc + dato * coef`` con saturación del acumulador."""
    return saturar_acc(acc + dato * coef)


def dato_a_memoria(dato: int) -> int:
    """Dato de 24 bit → palabra de 18 bit, devuelta alineada a dato (6 LSB a cero)."""
    perdida = DATO_BITS - MEM_BITS
    return saturar(redondear(dato, perdida), MEM_BITS) << perdida


def cuantizar(valor: Fraction, frac: int, bits: int, que: str) -> int:
    """Fracción exacta → entero de punto fijo, redondeando al más cercano.

    Fuera de rango es un error, no una saturación: lo usa el ensamblador, y un
    coeficiente fuera de rango es un fallo del programa que hay que ver.
    """
    escalado = valor * (1 << frac)
    entero = (escalado.numerator * 2 + escalado.denominator) // (2 * escalado.denominator)
    if not (-(1 << (bits - 1)) <= entero <= (1 << (bits - 1)) - 1):
        limite = Fraction(1 << (bits - 1), 1 << frac)
        raise ValueError(f"{que} {float(valor)} fuera de rango [-{limite}, {limite})")
    return entero


def coef(valor: Fraction | int | str) -> int:
    """Coeficiente S1.16 desde un valor exacto (o su texto decimal)."""
    return cuantizar(Fraction(valor), COEF_FRAC, COEF_BITS, "coeficiente")


def dato(valor: Fraction | int | str) -> int:
    """Dato S.23 desde un valor exacto, saturando 1.0 a ``DATO_MAX``."""
    escalado = Fraction(valor) * UNO
    entero = (escalado.numerator * 2 + escalado.denominator) // (2 * escalado.denominator)
    return saturar(entero, DATO_BITS)


def curva_suave(x: int) -> int:
    """Saturación suave cúbica ``y = (3x - x³) / 2`` sobre un dato S.23.

    Es monótona en [-1, 1], vale ±1 en los extremos y tiene pendiente 1,5 en
    el origen. Solo enteros: dos productos y desplazamientos *floor*. La usan
    la instrucción ``CLIP`` (limitador del freeze) y el LFO senoidal.
    """
    x2 = (x * x) >> DATO_FRAC
    x3 = (x2 * x) >> DATO_FRAC
    return saturar((3 * x - x3) >> 1, DATO_BITS)
