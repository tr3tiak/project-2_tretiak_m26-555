''' Здесь будет основная логика работы с таблицами и данными.'''

from .utils import load_table_data, save_table_data
from prettytable import PrettyTable

def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f"Ошибка: таблица {table_name} уже существует")
        return metadata

    allowed_types = {"int", "str", "bool"}

    for column_name, column_type in columns:
        if column_type not in allowed_types:
            print(f"Ошибка: {column_name} недопустимый тип {column_type}")
            return metadata

    columns = [("ID", "int")] + columns

    metadata[table_name] = columns

    return metadata



def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f"Ошибка: таблица {table_name} не существует")
        return metadata

    del metadata[table_name]

    return metadata

def list_table(metadata):
    if not metadata:
        print('пусто')
    else:
        for key in metadata.keys():
            print(key)


TYPE_MAP = {"int": int, "str": str, "bool": bool}


def convert_value(raw, type_name):
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


def insert(metadata, table_name, values):
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")
    if len(metadata[table_name]) != (len(values) + 1):
        raise ValueError("Количество переданных значений соответствует количеству столбцов")
    
    cols = metadata[table_name][1:]
    converted = []
    for i in range(len(cols)):
        type_name = cols[i][1]
        try:
            value = convert_value(values[i], type_name)
        except (ValueError, TypeError):
            raise ValueError("Тип данных не совпадает")
        if not isinstance(value, TYPE_MAP[type_name]):
            raise ValueError("Тип данных не совпадает")
        converted.append(value)

    data = load_table_data(table_name)
    # if not isinstance(data, list):
    #     data = []

    new_id = max((row["ID"] for row in data), default=0) + 1
    new_row = {"ID": new_id}
    for i in range(len(cols)):
        new_row[cols[i][0]] = converted[i]

    data.append(new_row)
    save_table_data(table_name, data)
    return new_id



def select(table_data, where_clause=None):
    
    if where_clause is None:
        return table_data

    return [
        row for row in table_data
        if all(row[k] == v for k, v in where_clause.items())
    ]

def update(table_data, set_clause, where_clause):
    if not where_clause:
        raise ValueError("update без условий запрещён")

    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            for col, new_value in set_clause.items():
                row[col] = new_value
    return table_data

def delete(table_data, where_clause):
    result = [
        row for row in table_data
        if not all(row[k] == v for k, v in where_clause.items())
    ]
    return result


def print_table(rows, columns):
    table = PrettyTable()
    table.field_names = columns
    for row in rows:
        table.add_row([row.get(col) for col in columns])
    print(table)