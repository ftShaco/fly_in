PYTHON = uv run python
SCRIPT = fly_in.py
MAP ?= maps/challenger/01_the_impossible_dream.txt
FLAGS ?=

export PYGAME_HIDE_SUPPORT_PROMPT=hide

.PHONY: install run debug clean lint lint-strict

install:
	@echo "environment synchronized with uv..."
	uv sync
	@echo "Dependencies installed."

run:
	@echo "Starting simulation on $(MAP)..."
	$(PYTHON) -m fly_in $(MAP) $(FLAGS) || true

debug:
	$(PYTHON) -m pdb $(SCRIPT)

clean:
	rm -rf .venv
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleaned up cache files."

lint:
	uv run flake8 --exclude=.venv
	uv run mypy . --exclude '\.venv' --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 --exclude=.venv
	uv run mypy . --exclude '\.venv' --strict
