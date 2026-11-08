#!/usr/bin/env bash
# Демо: установка, запуск, управление таблицами
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== make install (uv sync + editable install) ==="
make install >/dev/null 2>&1 || true
echo "=== make run → database ==="
printf '%s\n' \
  'create_table users name:str age:int is_active:bool' \
  'list_tables' \
  'create_table users name:str' \
  'info users' \
  'drop_table users' \
  'n' \
  'exit' \
| database
