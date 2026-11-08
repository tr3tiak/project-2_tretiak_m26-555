#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

printf '%s\n' \
  'create_table demo name:str age:int is_active:bool' \
  'insert into demo values ("Sergei", 28, true)' \
  'select from demo' \
  'select from demo where age = 28' \
  'update demo set age = 29 where name = "Sergei"' \
  'select from demo where age = 29' \
  'delete from demo where ID = 1' \
  'y' \
  'drop_table demo' \
  'y' \
  'exit' \
| PYTHONPATH=src .venv/bin/python -c 'from primitive_db.main import main; main()'
