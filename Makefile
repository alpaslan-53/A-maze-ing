PYTHON = python3
MAIN = a_maze_ing.py
CONFIG = config.txt
MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache .pytest_cache build dist *.egg-info

lint:
	flake8 .
	mypy . $(MYPY_FLAGS)

lint-strict:
	flake8 .
	mypy . --strict
	
build:
	$(PYTHON) -m build --wheel
