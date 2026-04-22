PYTHON = uv run python
SCRIPT = src/__main__.py
MAP ?= maps/test.txt

.PHONY: install run viz debug clean lint lint-strict

install:
	@echo "Synchronisation de l'environnement avec uv..."
	uv sync
	@echo "Dependencies installed."

run:
	@echo "Starting simulation on $(MAP)..."
	$(PYTHON) -m fly_in $(MAP) || true

debug:
	$(PYTHON) -m pdb $(SCRIPT)

clean:
	rm -rf .venv
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleaned up cache files."

lint:
	uv run flake8
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8
	uv run mypy . --strict