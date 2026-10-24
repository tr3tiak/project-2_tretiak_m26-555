''' Здесь будет основная логика работы с таблицами и данными.'''

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