# SPDX-License-Identifier: MIT
"""Modelo de referencia bit-exact de SOFIFI (ADR 0003).

Capas (las dependencias apuntan hacia adentro; lo comprueba
``model/tests/arquitectura_test.py``):

- ``domain``: DSP puro en punto fijo, sin I/O.
- ``ports``: protocolos pequeños (fuente/sumidero de audio, parámetros).
- ``adapters``: implementaciones de los puertos (WAV, volcados para el RTL).
- ``services``: casos de uso que componen dominio y puertos.
- ``cli``: entrada; único sitio que elige adaptadores (raíz de composición).
"""
