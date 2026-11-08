"""Именованные константы приложения."""

META_FILE = "db_meta.json"
DATA_DIR = "data"
ID_COLUMN = "ID"
ID_COLUMN_TYPE = "int"
VALID_TYPES = frozenset({"int", "str", "bool"})
TYPE_MAP = {"int": int, "str": str, "bool": bool}
PROMPT = "db > "
CONFIRM_YES = "y"
WHERE_SEPARATOR = " AND "
SET_SEPARATOR = ","
JSON_INDENT = 4

CREATE_TABLE_USAGE = "Использование: create_table <имя> [столбец:тип ...]"
DROP_TABLE_USAGE = "Использование: drop_table <имя>"
SELECT_USAGE = (
    "Использование: select from <имя_таблицы> [where столбец = значение AND ...]"
)
DELETE_USAGE = (
    "Использование: delete from <имя_таблицы> where столбец = значение AND ..."
)
UPDATE_USAGE = (
    "Использование: update <имя_таблицы> set столбец = значение, ... "
    "where столбец = значение AND ..."
)
INFO_USAGE = "Использование: info <имя_таблицы>"

ACTION_DROP_TABLE = "удаление таблицы"
ACTION_DELETE_ROWS = "удаление записей"
