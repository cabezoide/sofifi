# SPDX-License-Identifier: MIT
"""Compositor de cadenas: dos o más programas en un solo programa del núcleo (ADR 0013).

Una cadena une programas en serie (la salida de uno es la entrada del
siguiente) o en paralelo (todos oyen la entrada y la salida es la media). El
resultado es texto ``.sasm``: lo ensambla el ensamblador de siempre y el RTL
lo ejecuta como cualquier programa. No cambia la ISA ni el RTL.

Para cada programa, el compositor:

1. expande sus ``include`` (``ensamblador.expandir``);
2. antepone ``eN_`` a sus nombres (``equ``, ``mem``, etiquetas): no chocan;
3. le da LFOs que no usa ningún otro programa, y registros generales propios
   para los que guardan algo de una muestra a la siguiente (persistentes). Los
   temporales, que el programa escribe antes de leer en cada muestra, se
   comparten entre los programas (``registros_temporales``);
4. cambia ``adcl``/``adcr`` y ``dacl``/``dacr`` por los registros que unen
   los programas, y cada ``potN`` por un pot físico o por una constante.

La memoria la sigue asignando el ensamblador, en el orden de los ``mem``. Por
eso, cuando la memoria tenga más de un espacio (SDRAM, ADR 0004), las cadenas
heredan el cambio sin tocar este fichero, salvo la regla de ``mem``.

**Propiedad:** en serie, la cadena da los mismos bits que procesar la entrada
con el primer programa y su salida con el segundo. Cada programa conserva sus
registros persistentes, sus LFOs (cada uno con su LFSR) y su zona de memoria.
Un registro temporal compartido no lleva nada de un programa a otro: cada
programa lo escribe antes de leerlo. Lo comprueba ``model/tests/composicion_test.py``.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction

from sofifi.domain.cadena import Cadena, Eslabon, Modo, PotFisico, Recursos
from sofifi.domain.coste import ciclos_secuencia
from sofifi.domain.ensamblador import ErrorEnsamblado, Incluir, ensamblar, expandir, piezas
from sofifi.domain.isa import NOMBRES_REGISTRO, NUM_REGS_GENERALES, Instruccion, Op, Programa
from sofifi.domain.lfo import NUM_LFOS
from sofifi.domain.renombre import LFO_REG, POT, REG, reescribir, uso

# Instrucciones que leen el registro de su campo `reg` (en RDAA y WRAA, R da la posición).
LEEN_REGISTRO = frozenset({Op.RDAX, Op.RDFX, Op.MAXX, Op.MULX, Op.LDAX, Op.RDAA, Op.WRAA})


def registros_temporales(instrucciones: Sequence[Instruccion]) -> frozenset[int]:
    """Registros generales que el programa escribe antes de leer, en todos los caminos.

    Un registro así no guarda nada de una muestra a la siguiente: otro programa
    de la cadena puede usarlo en su turno. Los saltos (``SKP``) solo van hacia
    delante, así que basta una pasada: a cada instrucción llega la intersección
    de lo escrito en todos los caminos que llevan a ella.
    """
    n = len(instrucciones)
    escritos: list[frozenset[int] | None] = [frozenset()] + [None] * n
    leidos_antes: set[int] = set()
    usados: set[int] = set()
    for k, ins in enumerate(instrucciones):
        llega = escritos[k]
        if llega is None:  # ningún camino llega aquí
            continue
        general = ins.reg < NUM_REGS_GENERALES
        sale = llega
        if ins.op in LEEN_REGISTRO and general:
            usados.add(ins.reg)
            if ins.reg not in llega:
                leidos_antes.add(ins.reg)
        if ins.op is Op.WRAX and general:
            usados.add(ins.reg)
            sale = llega | {ins.reg}
        destinos = [k + 1] + ([k + 1 + ins.addr] if ins.op is Op.SKP else [])
        for d in destinos:
            d = min(d, n)
            previo = escritos[d]
            escritos[d] = sale if previo is None else previo & sale
    return frozenset(usados - leidos_antes)


@dataclass(frozen=True)
class _Plan:
    texto: str
    registros: int
    lfos: int
    absolutas: int


def _nombrador(
    i: int, e: Eslabon, regs: dict[int, str], lfos: dict[int, int], entrada: bool, salida: bool
) -> Callable[[str], str]:
    """Nombre nuevo de cada nombre del programa ``i``.

    Los nombres propios llevan el prefijo ``eN_``. Los registros generales y los
    LFOs van a los que se le asignaron. ``adcl``/``adcr`` leen la salida del
    programa anterior si ``entrada`` es False; ``dacl``/``dacr`` escriben en el
    registro de unión si ``salida`` es False. Un pot va al pot físico o a su
    constante.
    """

    def nombre(t: str) -> str:
        if t not in NOMBRES_REGISTRO:
            return f"e{i}_{t}"
        if m := REG.fullmatch(t):
            return regs[int(m.group(1))]
        if m := POT.fullmatch(t):
            mando = e.mando(int(m.group(1)))
            return f"pot{mando.indice}" if isinstance(mando, PotFisico) else f"e{i}_{t}"
        if m := LFO_REG.fullmatch(t):
            return f"lfo{lfos[int(m.group(1))]}_{m.group(2)}"
        if t in ("adcl", "adcr") and not entrada:
            return f"cad_{t[-1]}{i - 1}"
        if t in ("dacl", "dacr") and not salida:
            return f"cad_{t[-1]}{i}"
        return t

    return nombre


def _plan(
    cadena: Cadena, textos: Mapping[str, str], incluir: Incluir | None, contar: bool
) -> _Plan:
    """Texto de la cadena. Con ``contar``, todo va a reg0 y al LFO 0: solo sirve para medir."""
    n = len(cadena.eslabones)
    lineas = [expandir(textos[e.programa], incluir) for e in cadena.eslabones]
    usos = [uso(ls) for ls in lineas]
    temporales = [
        registros_temporales(piezas(textos[e.programa], incluir).instrucciones)
        for e in cadena.eslabones
    ]
    libres = iter(range(NUM_REGS_GENERALES)) if not contar else None
    asignados = 0

    def registro() -> str:
        nonlocal asignados
        asignados += 1
        if libres is None:
            return "reg0"
        try:
            return f"reg{next(libres)}"
        except StopIteration:
            raise ErrorEnsamblado(0, f"cadena '{cadena.nombre}': no hay registros libres") from None

    cabecera = [f"; GENERADO por el compositor (ADR 0013): {cadena.nombre}"]
    # Registros que unen los programas: en serie, entre cada par; en paralelo, uno por programa.
    union = range(1, n) if cadena.modo is Modo.SERIE else range(1, n + 1)
    for i in union:
        cabecera += [f"equ  cad_l{i}  {registro()}", f"equ  cad_r{i}  {registro()}"]
    constantes: list[tuple[str, Fraction]] = []
    for i, (e, u) in enumerate(zip(cadena.eslabones, usos, strict=True), start=1):
        for k in sorted(u.pots):
            m = e.mando(k)
            if isinstance(m, Fraction):
                cabecera.append(f"equ  e{i}_pot{k}  {registro()}")
                constantes.append((f"e{i}_pot{k}", m))
    cuerpo: list[str] = []
    if constantes:
        cuerpo.append("        skp  run, cad_arranque")
        for nombre_k, valor in constantes:
            cuerpo += [f"        sof  0, {valor}", f"        wrax  {nombre_k}, 0"]
        cuerpo.append("cad_arranque:")
    lfo_libre = 0
    compartidos: list[str] = []  # registros temporales, comunes a todos los programas

    def compartido(k: int) -> str:
        while len(compartidos) <= k:
            compartidos.append(registro())
        return compartidos[k]

    for i, (e, ls, u, t) in enumerate(
        zip(cadena.eslabones, lineas, usos, temporales, strict=True), start=1
    ):
        orden_t = sorted(t & u.regs)
        regs = {
            r: compartido(orden_t.index(r)) if r in orden_t else registro() for r in sorted(u.regs)
        }
        lfos: dict[int, int] = {}
        for k in sorted(u.lfos):
            lfos[k] = 0 if contar else lfo_libre
            lfo_libre += 1
        if lfo_libre > NUM_LFOS and not contar:
            raise ErrorEnsamblado(0, f"cadena '{cadena.nombre}': más de {NUM_LFOS} LFOs")
        entrada = cadena.modo is Modo.PARALELO or i == 1
        salida = cadena.modo is Modo.SERIE and i == n
        nombre = _nombrador(i, e, regs, lfos, entrada, salida)
        if i > 1:
            cuerpo.append("        clr")  # ACC = 0, como al empezar la muestra
        cuerpo.append(f"; ── {i}. {e.programa} ──")
        cuerpo += reescribir(ls, nombre, lfos.__getitem__)
    if cadena.modo is Modo.PARALELO:
        cuerpo.append("        clr")
        for lado in ("l", "r"):
            cuerpo += [f"        rdax  cad_{lado}{k}, 1/{n}" for k in range(1, n + 1)]
            cuerpo.append(f"        wrax  dac{lado}, 0")
    return _Plan(
        "\n".join(cabecera + cuerpo) + "\n",
        asignados,
        sum(len(u.lfos) for u in usos),
        sum(u.absoluta for u in usos),
    )


def componer(cadena: Cadena, textos: Mapping[str, str], incluir: Incluir | None = None) -> str:
    """Texto ``.sasm`` de la cadena. Falla si no hay registros o LFOs para todos."""
    return _plan(cadena, textos, incluir, contar=False).texto


def ensamblar_cadena(
    cadena: Cadena, textos: Mapping[str, str], incluir: Incluir | None = None
) -> Programa:
    """La cadena como un programa más: lo que ejecutan el modelo y el RTL."""
    return ensamblar(componer(cadena, textos, incluir), nombre_programa(cadena), incluir)


def nombre_programa(cadena: Cadena) -> str:
    """«Eco y muelle» → «cadena_eco_y_muelle»: un nombre que vale como fichero."""
    plano = unicodedata.normalize("NFKD", cadena.nombre.lower()).encode("ascii", "ignore").decode()
    return "cadena_" + re.sub(r"[^a-z0-9]+", "_", plano).strip("_")


def recursos(cadena: Cadena, textos: Mapping[str, str], incluir: Incluir | None = None) -> Recursos:
    """Lo que gasta la cadena, aunque no quepa en el núcleo."""
    plan = _plan(cadena, textos, incluir, contar=True)
    p = piezas(plan.texto)
    ciclos = ciclos_secuencia(p.instrucciones, p.lfos)
    return Recursos(
        len(p.instrucciones),
        ciclos,
        max(1, p.memoria_usada),
        plan.registros,
        plan.lfos,
        plan.absolutas,
    )
