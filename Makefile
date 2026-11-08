.PHONY: install run lint record

install:
	uv sync --all-groups
	uv pip install -e .

run:
	database

lint:
	uv run ruff check .

record:
	asciinema rec demo.cast --overwrite -c ./scripts/record_demo.sh
