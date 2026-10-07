# SPDX-License-Identifier: MIT
# Puntos de entrada del proyecto. La compuerta es scripts/ci_local.sh (ADR 0001).
.PHONY: help install hooks ci ci-dura test docs release-check

VENV := .venv
PY := $(VENV)/bin/python

help:
	@echo "make install        crea .venv con numpy, pytest, ruff, mypy, pyyaml"
	@echo "make hooks          instala los hooks versionados (core.hooksPath)"
	@echo "make ci             compuerta local completa (duras + blandas)"
	@echo "make ci-dura        solo las duras (lo que corre el pre-push)"
	@echo "make test           solo la suite del modelo"
	@echo "make docs           solo la coherencia de mapas, ADRs y registros"
	@echo "make release-check  compuerta de release (aún no existe: falla a propósito)"

install:
	python3 -m venv $(VENV)
	$(PY) -m pip install -q -e '.[dev]'

hooks:
	scripts/install_hooks.sh

ci:
	scripts/ci_local.sh

ci-dura:
	scripts/ci_local.sh --no-soft

test:
	scripts/ci_local.sh model

docs:
	scripts/ci_local.sh docs

release-check:
	@echo "No hay compuerta de release todavía: llega con la primera síntesis (ver docs/fases/)."
	@echo "Se declara el hueco en lugar de fingir un verde (SPEC_RAIZ P2)."
	@exit 1
