# sim/AGENTS.md — testbenches (tiene precedencia en esta carpeta)

Testbenches cocotb (Python) sobre Verilator. Cada uno alimenta el RTL con un
estímulo y lo compara **muestra a muestra** con el modelo de `model/sofifi/`
(ADR 0003).

| Carpeta | Qué prueba |
|---|---|
| `sim/nucleo/` | el núcleo y sus bloques; `sim/nucleo/nucleo_test.py` recorre todos los programas y las cadenas que caben |
| `sim/sd/` | el controlador SD y el cargador, con un modelo de tarjeta (`sim/sd/tarjeta_sd.py`) |
| `sim/top/` | los tops `hil_nucleo` y `prueba_sd` |
| `sim/comun/`, `sim/primitivas/` | UART, medidor de frecuencia y primitivas |

`make sim` ejecuta todo. La prueba de aceptación del núcleo usa más muestras:
`SOFIFI_MUESTRAS=4883 pytest sim/nucleo/nucleo_test.py`.

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
- El filtro `testcase` de cocotb es una expresión regular que busca en el nombre.
  `igual_al_modelo` elige también `absoluta_igual_al_modelo`. Ningún nombre de
  prueba contiene el de otra (fails.md, F-20).
