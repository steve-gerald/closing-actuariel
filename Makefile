.PHONY: help install closing test figures excel docs clean all

PYTHON ?= python3

help:
	@echo "Commandes disponibles :"
	@echo "  make install     Installe le package en mode editable + deps de dev"
	@echo "  make closing     Execute le pipeline de cloture complet"
	@echo "  make figures     Genere les 5 figures matplotlib"
	@echo "  make excel       Genere le classeur Excel de pilotage"
	@echo "  make test        Lance les tests unitaires"
	@echo "  make all         Pipeline + figures + excel + tests"
	@echo "  make clean       Supprime les sorties generees"
	@echo ""
	@echo "  Le dashboard HTML est versionne dans dashboard/index.html."
	@echo "  Ouvrir directement dans un navigateur."

install:
	pip install -e ".[dev]"

closing:
	$(PYTHON) -m closing.run

test:
	pytest tests/ -v

figures:
	$(PYTHON) scripts/generer_figures.py

excel:
	$(PYTHON) scripts/generer_excel.py

all:
	@echo "=== Etape 1/4 : pipeline ==="
	-$(PYTHON) -m closing.run
	@echo ""
	@echo "=== Etape 2/4 : figures ==="
	$(PYTHON) scripts/generer_figures.py
	@echo ""
	@echo "=== Etape 3/4 : classeur Excel ==="
	$(PYTHON) scripts/generer_excel.py
	@echo ""
	@echo "=== Etape 4/4 : tests ==="
	pytest tests/ -q
	@echo ""
	@echo "Tous les livrables sont disponibles dans outputs/ et dashboard/."

clean:
	rm -rf data/raw/*.csv data/processed/*.csv
	rm -rf outputs/*.png outputs/*.xlsx
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
