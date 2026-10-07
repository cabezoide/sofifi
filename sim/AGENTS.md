# sim/AGENTS.md — testbenches (tiene precedencia en esta carpeta)

Vacío en la versión 0.0. Aquí irán los testbenches cocotb (Python) sobre Verilator
o Icarus. Cada uno alimenta el RTL con un estímulo y compara **muestra a muestra**
contra el modelo de `model/sofifi/` (ADR 0003).

## Reglas

- Un testbench importa el modelo por su API de servicios, no por sus internos de
  dominio.
- **Igualdad exacta**: tolerancia cero salvo que un ADR diga lo contrario.
- Los WAV y los volcados generados van a un directorio temporal o al directorio out/, que
  está ignorado por git.

## Trampas

- Verilator viene del paquete pip `verilator`. `sim/conftest.py` pone en PATH su
  binario real con `VERILATOR_ROOT`; nunca se enlaza `verilator -> verilator-cli`,
  porque se relanzaría en bucle hasta agotar la memoria.
- Los bancos que no son DSP (UART, controles) se validan contra el protocolo, no
  contra el modelo: ADR 0003 solo obliga a los bloques DSP.
