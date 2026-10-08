# SPDX-License-Identifier: MIT
"""ISA del núcleo SOFIFI: superconjunto de la del FV-1 (ADR 0006, ADR 0009).

Palabra de 54 bit (tres columnas de BSRAM de 18 bit)::

    53..48  op     (6)   código de operación
    47..42  reg    (6)   registro, o índice de LFO en CHO
    41..36  flags  (6)   condiciones de SKP / modificadores de CHO
    35..18  coef   (18)  coeficiente S1.16 (complemento a dos)
    17..0   addr   (18)  dirección de memoria, D de SOF (S2.15) o salto de SKP

Notación en las descripciones: ``a24`` = ACC redondeado y saturado a dato;
``R`` = registro; ``M[a]`` = memoria; ``LR`` = último valor leído de memoria.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, IntFlag

from sofifi.domain.aritmetica import CICLOS_POR_MUESTRA
from sofifi.domain.lfo import NUM_LFOS, ConfigLfo, TipoLfo
from sofifi.domain.memoria import PALABRAS_ABSOLUTAS, PALABRAS_MAX


class Op(IntEnum):
    NOP = 0  # no hace nada
    RDA = 1  # ACC += M[a]·C ; LR = M[a]
    WRA = 2  # M[a] = a24 ; ACC = a24·C
    WRAP = 3  # M[a] = a24 ; ACC = a24·C + LR      (allpass)
    RDAX = 4  # ACC += R·C
    WRAX = 5  # R = a24 ; ACC = a24·C
    RDFX = 6  # ACC = (a24 − R)·C + R              (filtro de un polo)
    MAXX = 7  # ACC = max(|ACC|, |R·C|)
    MULX = 8  # ACC = (a24·R) >> 7
    SOF = 9  # ACC = a24·C + D
    CLIP = 10  # ACC = curva_suave(a24)              (extensión SOFIFI)
    SKP = 11  # si alguna condición: saltar N instrucciones
    CHO = 12  # v = Hermite(M[a + LFO]) [·ventana] ; LR = v ; ACC += v·C (extensión)
    LDAX = 13  # ACC = R
    CLR = 14  # ACC = 0
    ABSA = 15  # ACC = |ACC|
    RDAA = 16  # v = lineal(M_abs[addr + R]) ; LR = v ; ACC += v·C   (región absoluta, Fase 07)
    WRAA = 17  # M_abs[addr + R] = a24 ; ACC = a24·C


class Skp(IntFlag):
    RUN = 1  # no es la primera muestra desde el arranque
    ZRO = 2  # ACC == 0
    GEZ = 4  # ACC >= 0
    NEG = 8  # ACC < 0


class Cho(IntFlag):
    NA = 1  # multiplicar por la ventana triangular del LFO (pitch shift)
    MEDIA = 2  # usar el LFO desfasado media vuelta


CICLOS: dict[Op, int] = {op: 1 for op in Op} | {Op.CHO: 4}

MAX_INSTRUCCIONES = 2048

# Mapa de registros (6 bit).
NUM_REGS_GENERALES = 32
ADCL, ADCR, DACL, DACR = 32, 33, 34, 35
POT_BASE, NUM_POTS = 36, 6
LFO_BASE = 42  # lfoN_rate = LFO_BASE + 2N ; lfoN_depth = LFO_BASE + 2N + 1
SW = 50
NUM_REGISTROS = 64

NOMBRES_REGISTRO: dict[str, int] = (
    {f"reg{i}": i for i in range(NUM_REGS_GENERALES)}
    | {"adcl": ADCL, "adcr": ADCR, "dacl": DACL, "dacr": DACR, "sw": SW}
    | {f"pot{i}": POT_BASE + i for i in range(NUM_POTS)}
    | {f"lfo{n}_rate": LFO_BASE + 2 * n for n in range(NUM_LFOS)}
    | {f"lfo{n}_depth": LFO_BASE + 2 * n + 1 for n in range(NUM_LFOS)}
)
SOLO_LECTURA = frozenset({ADCL, ADCR, SW, *range(POT_BASE, POT_BASE + NUM_POTS)})

CAMPOS = (("op", 6), ("reg", 6), ("flags", 6), ("coef", 18), ("addr", 18))
BITS_PALABRA = sum(b for _, b in CAMPOS)


@dataclass(frozen=True, slots=True)
class Instruccion:
    op: Op
    reg: int = 0
    flags: int = 0
    coef: int = 0
    addr: int = 0


def codificar(ins: Instruccion) -> int:
    palabra = 0
    for nombre, bits in CAMPOS:
        valor = int(getattr(ins, nombre))
        if nombre in ("coef", "addr"):
            # coef es S1.16 estricto; addr admite sin signo (memoria, salto) o S2.15 (D).
            tope = (1 << (bits - 1)) if nombre == "coef" else (1 << bits)
            if not -(1 << (bits - 1)) <= valor < tope:
                raise ValueError(f"{nombre}={valor} no cabe en {bits} bit")
            valor &= (1 << bits) - 1
        elif not 0 <= valor < (1 << bits):
            raise ValueError(f"{nombre}={valor} no cabe en {bits} bit")
        palabra = (palabra << bits) | valor
    return palabra


def decodificar(palabra: int) -> Instruccion:
    valores: dict[str, int] = {}
    for nombre, bits in reversed(CAMPOS):
        valores[nombre] = palabra & ((1 << bits) - 1)
        palabra >>= bits
    coef = valores["coef"]
    if coef >= 1 << 17:
        coef -= 1 << 18
    return Instruccion(Op(valores["op"]), valores["reg"], valores["flags"], coef, valores["addr"])


def alcance_cho(config: ConfigLfo | None, addr: int) -> int:
    """Última dirección que puede leer un ``CHO`` sobre ``addr`` (Hermite: +2).

    SIN y RND desplazan hasta 2·E muestras; RAMP, hasta W. El programa debe
    declarar memoria para todo el tramo: así el RTL reduce la dirección con una
    sola corrección de ±P en lugar de un módulo general (ADR 0009).
    """
    if config is None:
        return addr
    extra = config.excursion if config.tipo is TipoLfo.RAMP else 2 * config.excursion
    return addr + extra + 1


def addr_con_signo(addr: int) -> int:
    """Interpreta el campo ``addr`` como S2.15 (operando D de ``SOF``)."""
    addr &= (1 << 18) - 1
    return addr - (1 << 18) if addr >= 1 << 17 else addr


@dataclass(frozen=True)
class Programa:
    nombre: str
    instrucciones: tuple[Instruccion, ...]
    palabras_memoria: int
    lfos: tuple[ConfigLfo | None, ...] = field(default=(None,) * NUM_LFOS)

    def __post_init__(self) -> None:
        errores = self.errores()
        if errores:
            raise ValueError(f"programa '{self.nombre}' inválido: " + "; ".join(errores))

    @property
    def usa_absoluta(self) -> bool:
        """True si el programa usa la región absoluta (RDAA, WRAA; ADR 0009)."""
        return any(i.op in (Op.RDAA, Op.WRAA) for i in self.instrucciones)

    @property
    def ciclos(self) -> int:
        return sum(CICLOS[i.op] for i in self.instrucciones)

    def errores(self) -> list[str]:
        e: list[str] = []
        n = len(self.instrucciones)
        if n > MAX_INSTRUCCIONES:
            e.append(f"{n} instrucciones > {MAX_INSTRUCCIONES}")
        if self.ciclos > CICLOS_POR_MUESTRA:
            e.append(f"{self.ciclos} ciclos > {CICLOS_POR_MUESTRA} por muestra")
        if self.usa_absoluta and self.palabras_memoria + PALABRAS_ABSOLUTAS > PALABRAS_MAX:
            e.append(
                f"memoria {self.palabras_memoria} + región absoluta {PALABRAS_ABSOLUTAS}"
                f" > {PALABRAS_MAX} palabras"
            )
        if not 1 <= self.palabras_memoria <= PALABRAS_MAX:
            e.append(f"memoria {self.palabras_memoria} fuera de [1, {PALABRAS_MAX}]")
        if len(self.lfos) != NUM_LFOS:
            e.append(f"se esperaban {NUM_LFOS} ranuras de LFO")
        for pc, ins in enumerate(self.instrucciones):
            if ins.op is Op.WRAX and ins.reg in SOLO_LECTURA:
                e.append(f"[{pc}] WRAX escribe un registro de solo lectura ({ins.reg})")
            if ins.op is Op.SKP and pc + 1 + ins.addr > n:
                e.append(f"[{pc}] SKP salta fuera del programa")
            if ins.op is Op.CHO and (ins.reg >= NUM_LFOS or self.lfos[ins.reg] is None):
                e.append(f"[{pc}] CHO usa el LFO {ins.reg}, que no está declarado")
            elif ins.op is Op.CHO:
                fin = alcance_cho(self.lfos[ins.reg], ins.addr)
                if fin >= self.palabras_memoria:
                    e.append(
                        f"[{pc}] CHO lee hasta la dirección {fin}, fuera de la memoria"
                        f" declarada ({self.palabras_memoria} palabras)"
                    )
            if ins.op in (Op.RDAA, Op.WRAA) and ins.addr >= PALABRAS_ABSOLUTAS:
                e.append(f"[{pc}] origen {ins.addr} fuera de la región absoluta")
            if ins.op in (Op.RDA, Op.WRA, Op.WRAP, Op.CHO) and ins.addr >= self.palabras_memoria:
                e.append(f"[{pc}] dirección {ins.addr} fuera de la memoria declarada")
        return e
