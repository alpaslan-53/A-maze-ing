PYTHON = python3
MAIN = a_maze_ing.py
CONFIG = config.txt
MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict test

# Bagimliliklari yukler
install:
	$(PYTHON) -m pip install -r requirements.txt

# Ana programi calistirir
run:
	$(PYTHON) $(MAIN) $(CONFIG)

# Python hata ayiklayicisi (pdb) ile calistirir
debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

# Gecici dosyalari ve onbellekleri temizler
clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache .pytest_cache build dist *.egg-info

# Zorunlu linter denetimi: flake8 ve PDF bayraklariyla mypy
lint:
	flake8 .
	mypy . $(MYPY_FLAGS)

# Istege bagli siki tip denetimi
lint-strict:
	flake8 .
	mypy . --strict

# Birim testleri calistirir
test:
	$(PYTHON) -m pytest -q
