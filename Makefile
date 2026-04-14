PYTHON = uv run python
SCRIPT = src/__main__.py

.PHONY: install run debug clean lint lint-strict

install:
	@echo "Synchronisation de l'environnement avec uv..."
	uv sync
	@echo "\nDependencies installed."

run:
	$(PYTHON) -m src || true

debug:
	$(PYTHON) -m pdb $(SCRIPT)

clean:
	rm -rf .venv
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleaned up cache files."

lint:
	uv run flake8 src/
	uv run mypy src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 src/
	uv run mypy src/ --strict