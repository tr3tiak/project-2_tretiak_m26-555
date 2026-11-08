.PHONY: install run lint record

install:
	uv sync --all-groups
	uv pip install -e .

run:
	database

lint:
	uv run ruff check .

record:
	asciinema rec demo.cast --overwrite -c ./scripts/record_final.sh

record-all:
	asciinema rec install_tables.cast --overwrite -c ./scripts/record_install_and_tables.sh
	asciinema rec crud.cast --overwrite -c ./scripts/record_crud.sh
	asciinema rec demo.cast --overwrite -c ./scripts/record_final.sh
