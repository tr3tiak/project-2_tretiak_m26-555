.PHONY: install run lint

install:
	uv sync --all-groups
	uv pip install -e .

run:
	database

lint:
	uv run ruff check .
