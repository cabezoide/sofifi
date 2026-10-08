# SPDX-License-Identifier: MIT
"""Compositor de cadenas: dos o más programas en un solo programa del núcleo (ADR 0013).

Una cadena une programas en serie (la salida de uno es la entrada del
siguiente) o en paralelo (todos oyen la entrada y la salida es la media). El
resultado es texto ``.sasm``: lo ensambla el ensamblador de siempre y el RTL
lo ejecuta como cualquier programa. No cambia la ISA ni el RTL.

Para cada programa, el compositor:

1. expande sus ``include`` (``ensamblador.expandir``);
2. antepone ``eN_`` a sus nombres (``equ``, ``mem``, etiquetas): no chocan;
3. le da registros generales y LFOs que no usa ningún otro programa;
4. cambia ``adcl``/``adcr`` y ``dacl``/``dacr`` por los registros que unen
   los programas, y cada ``potN`` por un pot físico o por una constante.

La memoria la sigue asignando el ensamblador, en el orden de los ``mem``. Por
eso, cuando la memoria tenga más de un espacio (SDRAM, ADR 0004), las cadenas
heredan el cambio sin tocar este fichero, salvo la regla de ``mem``.

**Propiedad:** en serie, la cadena da los mismos bits que procesar la entrada
con el primer programa y su salida con el segundo. Cada programa conserva sus
registros, sus LFOs (cada uno con su LFSR) y su zona de memoria. Lo comprueba
``model/tests/composicion_test.py``.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from fractions import Fraction

from sofifi.domain.cadena import Cadena, Eslabon, Modo, PotFisico, Recursos
from sofifi.domain.coste import CICLOS_FIJOS_RTL, ciclos_instruccion_rtl
from sofifi.domain.ensamblador import ErrorEnsamblado, Incluir, ensamblar, expandir, piezas
from sofifi.domain.isa import NOMBRES_REGISTRO, NUM_REGS_GENERALES, Programa
from sofifi.domain.lfo import NUM_LFOS
from sofifi.domain.renombre import LFO_REG, POT, REG, reescribir, uso


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
    for i, (e, ls, u) in enumerate(zip(cadena.eslabones, lineas, usos, strict=True), start=1):
        regs = {r: registro() for r in sorted(u.regs)}
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
    ciclos = CICLOS_FIJOS_RTL + sum(ciclos_instruccion_rtl(i) for i in p.instrucciones)
    return Recursos(
        len(p.instrucciones),
        ciclos,
        max(1, p.memoria_usada),
        plan.registros,
        plan.lfos,
        plan.absolutas,
    )
