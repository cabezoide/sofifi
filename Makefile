# SPDX-License-Identifier: MIT
# Puntos de entrada del proyecto. La compuerta es scripts/ci_local.sh (ADR 0001).
.PHONY: help install hooks ci ci-dura test sim docs synth optimizacion prog uart release-check esquematicos

VENV := .venv
PY := $(VENV)/bin/python

help:
	@echo "make install        crea .venv con el modelo, la compuerta y la cadena EDA"
	@echo "make hooks          instala los hooks versionados (core.hooksPath)"
	@echo "make ci             compuerta local completa (duras + blandas)"
	@echo "make ci-dura        solo las duras (lo que corre el pre-push)"
	@echo "make test           solo la suite del modelo"
	@echo "make sim            solo los testbenches cocotb del RTL"
	@echo "make docs           solo la coherencia de mapas, ADRs y registros"
	@echo "make synth          sintetiza TOP (por defecto hola_uart) en build/"
	@echo "make optimizacion   segunda vuelta: recursos, timing y pistas de cada top"
	@echo "make prog           carga build/TOP.fs en la SRAM de la placa"
	@echo "make uart           lee la UART de la placa y exige \"SOFIFI\""
	@echo "make release-check  compuerta de release: síntesis de los tops"
	@echo "make esquematicos   regenera schematics/ (PDF de cada módulo RTL, ADR 0012)"

install:
	python3 -m venv $(VENV)
	$(PY) -m pip install -q -e '.[dev,eda,demos]'

hooks:
	scripts/install_hooks.sh

ci:
	scripts/ci_local.sh

ci-dura:
	scripts/ci_local.sh --no-soft

test:
	scripts/ci_local.sh model

sim:
	scripts/ci_local.sh sim

docs:
	scripts/ci_local.sh docs

# Tops sintetizables y sus fuentes: lista única en rtl/top/tops.txt.
TOP ?= hola_uart
FUENTES = $(shell awk '$$1 == "$(TOP)" { $$1 = ""; print }' rtl/top/tops.txt)

synth:
	scripts/fpga.sh synth $(FUENTES)

optimizacion:
	scripts/ci_local.sh optimizacion ratchets

prog: synth
	scripts/fpga.sh prog build/$(TOP).fs

uart:
	$(PY) scripts/leer_uart.py

# La síntesis es compuerta de release, no del pre-push: tarda y no cambia con
# cada commit del modelo (Fase 02).
release-check:
	scripts/ci_local.sh optimizacion ratchets

esquematicos:
	cd herramientas/esquematicos && npm install --no-audit --no-fund
	$(PY) scripts/esquematicos.py
