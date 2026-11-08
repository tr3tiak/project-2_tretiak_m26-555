#!/usr/bin/env bash
# Демо: все CRUD-операции (таблица users должна существовать)
set -euo pipefail
cd "$(dirname "$0")/.."

printf '%s\n' \
  'create_table users name:str age:int is_active:bool' \
  'insert into users values ("Sergei", 28, true)' \
  'select from users' \
  'select from users where age = 28' \
  'update users set age = 29 where name = "Sergei"' \
  'select from users where age = 29' \
  'info users' \
  'exit' \
| database
