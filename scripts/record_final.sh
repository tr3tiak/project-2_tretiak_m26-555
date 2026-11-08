#!/usr/bin/env bash
# Финальное демо: полный сценарий + декораторы (подтверждение, ошибки, log_time)
set -euo pipefail
cd "$(dirname "$0")/.."

printf '%s\n' \
  'create_table demo name:str age:int is_active:bool' \
  'insert into demo values ("Sergei", 28, true)' \
  'select from demo' \
  'select from demo' \
  'create_table demo name:str' \
  'delete from demo where ID = 1' \
  'n' \
  'delete from demo where ID = 1' \
  'y' \
  'drop_table demo' \
  'y' \
  'exit' \
| database
