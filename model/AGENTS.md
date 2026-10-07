# model/AGENTS.md — modelo de referencia (tiene precedencia en esta carpeta)

El modelo Python es el **oráculo bit-exact** del RTL (ADR 0003). Si el RTL y el
modelo discrepan, el que se corrige es el RTL, salvo que se demuestre que el
modelo no reproduce la aritmética del hardware. En ese caso se arregla el modelo
y se dice en el PR.

## Capas (`model/sofifi/`)

| Capa | Puede importar | No puede |
|---|---|---|
| `sofifi/domain/` | stdlib pura, numpy | I/O (`os`, `pathlib`, `wave`…), cualquier otra capa |
| `sofifi/ports/` | `domain` | adaptadores, servicios, cli |
| `sofifi/adapters/` | `domain`, `ports` | servicios, cli |
| `sofifi/services/` | `domain`, `ports` | adaptadores, cli (los recibe inyectados) |
| `cli` | todo | — es la raíz de composición |

Lo comprueba `model/tests/arquitectura_test.py`.

## Reglas de esta capa

- **Punto fijo explícito.** Cada señal declara su formato Q; la saturación y el
  redondeo son los del hardware, no los de numpy por defecto.
- **Determinismo.** El ruido y los LFO aleatorios salen de un LFSR del dominio con
  semilla, nunca de `random`. Dos ejecuciones producen el mismo WAV byte a byte.
- **Las pruebas viven en `model/tests/`** con sufijo `_test.py`, y nunca escriben en
  el árbol de fuentes: siempre en `tmp_path`.

## Trampas

- `numpy` hace *wrap* silencioso en enteros. Toda suma que pueda desbordar se
  satura de forma explícita.
- Interpolar en float y luego cuantizar no es lo mismo que interpolar en punto fijo.
  El modelo hace lo segundo.
