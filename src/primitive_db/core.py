"""Основная бизнес-логика: таблицы и CRUD-операции."""

from prettytable import PrettyTable

from .constants import (
    ACTION_DELETE_ROWS,
    ACTION_DROP_TABLE,
    ID_COLUMN,
    ID_COLUMN_TYPE,
    TYPE_MAP,
    VALID_TYPES,
    table_exists_message,
    table_missing_message,
)
from .decorators import confirm_action, create_cacher, handle_db_errors, log_time
from .utils import load_table_data, save_table_data

cache_result = create_cacher()


def _select_cache_key(table_data, where_clause):
    """Строит хешируемый ключ кэша для select."""
    data_key = tuple(tuple(sorted(row.items())) for row in table_data)
    where_key = None
    if where_clause is not None:
        where_key = tuple(sorted(where_clause.items()))
    return (data_key, where_key)


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу с автоматическим столбцом ID."""
    if table_name in metadata:
        raise ValueError(table_exists_message(table_name))

    for column_name, column_type in columns:
        if column_type not in VALID_TYPES:
            raise ValueError(
                f"Недопустимый тип '{column_type}' у столбца {column_name}"
            )

    columns = [(ID_COLUMN, ID_COLUMN_TYPE)] + columns
    metadata[table_name] = columns
    return metadata


@handle_db_errors
@confirm_action(ACTION_DROP_TABLE)
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        raise ValueError(table_missing_message(table_name))

    del metadata[table_name]
    return metadata


def list_table(metadata):
    """Печатает имена существующих таблиц."""
    if not metadata:
        print("пусто")
    else:
        for key in metadata:
            print(f"- {key}")


def convert_value(raw, type_name):
    """Приводит строковое значение к типу столбца."""
    raw = str(raw).strip()
    python_type = TYPE_MAP.get(type_name)
    if python_type is None:
        raise ValueError(f"Недопустимый тип {type_name}")

    if type_name == "str":
        if len(raw) >= 2 and raw[0] in "'\"" and raw[-1] == raw[0]:
            raw = raw[1:-1]
        return raw

    if type_name == "int":
        return int(raw)

    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise ValueError("Тип данных не совпадает")


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Добавляет строку в таблицу и возвращает присвоенный ID."""
    if table_name not in metadata:
        raise ValueError(table_missing_message(table_name))
    if len(metadata[table_name]) != (len(values) + 1):
        raise ValueError(
            "Количество переданных значений не соответствует количеству столбцов"
        )

    cols = metadata[table_name][1:]
    converted = []
    for index, (column_name, type_name) in enumerate(cols):
        value = convert_value(values[index], type_name)
        if not isinstance(value, TYPE_MAP[type_name]):
            raise ValueError("Тип данных не совпадает")
        converted.append(value)

    data = load_table_data(table_name)
    new_id = max((row[ID_COLUMN] for row in data), default=0) + 1
    new_row = {ID_COLUMN: new_id}
    for index, (column_name, _type_name) in enumerate(cols):
        new_row[column_name] = converted[index]

    data.append(new_row)
    save_table_data(table_name, data)
    return new_id


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает строки таблицы с учётом условия where и кэша."""
    cache_key = _select_cache_key(table_data, where_clause)

    def compute():
        if where_clause is None:
            return table_data
        return [
            row
            for row in table_data
            if all(row[key] == value for key, value in where_clause.items())
        ]

    return cache_result(cache_key, compute)


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет строки, удовлетворяющие условию where."""
    if not where_clause:
        raise ValueError("update без условий запрещён")

    for row in table_data:
        for key in where_clause:
            if key not in row:
                raise KeyError(key)
        for column in set_clause:
            if column not in row:
                raise KeyError(column)

    for row in table_data:
        if all(row[key] == value for key, value in where_clause.items()):
            for column, new_value in set_clause.items():
                row[column] = new_value
    return table_data


@handle_db_errors
@confirm_action(ACTION_DELETE_ROWS)
def delete(table_data, where_clause):
    """Удаляет строки, удовлетворяющие условию where."""
    return [
        row
        for row in table_data
        if not all(row[key] == value for key, value in where_clause.items())
    ]


def print_table(rows, columns):
    """Выводит результат select в виде таблицы."""
    table = PrettyTable()
    table.field_names = columns
    for row in rows:
        table.add_row([row.get(column) for column in columns])
    print(table)
