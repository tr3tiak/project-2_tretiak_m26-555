'''Этот файл будет отвечать за запуск, игровой цикл и парсинг команд.'''

import prompt
from .core import create_table, drop_table, list_table, insert, select, delete, update, print_table
from .utils import load_metadata, save_metadata, load_table_data, save_table_data
import shlex

def welcome():
    name = prompt.string(''' Первая попытка запустить проект!
***
<command> exit - выйти из программы
<command> help - справочная информация
Введите команду: ''')
    if name == "exit":
        print("Выход из программы")
    elif name == "help":
        print("Справочная информация")
        

def run():
    filepath = "db_meta.json"

    while True:
        metadata = load_metadata(filepath)

        try:
            user_input = prompt.string("db > ")
            args = shlex.split(user_input)
        except ValueError as e:
            print(f"Ошибка разбора команды: {e}")
            continue

        if not args:
            continue

        command = args[0]

        if command in ("exit", "quit"):
            break

        if command == "create_table":
            if len(args) < 2:
                print("Использование: create_table <имя> [столбец:тип ...]")
                continue

            table_name = args[1]

            try:
                columns = []
                for item in args[2:]:
                    column_name, column_type = item.split(":", 1)
                    columns.append((column_name, column_type))
            except ValueError:
                print("Ошибка: формат столбца должен быть имя:тип")
                continue

            previous_metadata = metadata.copy()
            create_table(metadata, table_name, columns)

            

            if metadata != previous_metadata:
                save_metadata(filepath, metadata)
                s = ", ".join(":".join(cols) for cols in metadata[table_name])
                print(f"Таблица {table_name} успешно создана со столбцами: {s}")

        elif command == "drop_table":
            if len(args) != 2:
                print("Использование: drop_table <имя>")
                continue

            table_name = args[1]
            previous_metadata = metadata.copy()

            drop_table(metadata, table_name)

            if metadata != previous_metadata:
                save_metadata(filepath, metadata)
                print(f"Таблица {table_name} удалена")
        elif command == "list_tables":
            list_table(metadata)
        elif command == "insert":
            if len(args) < 5:
                print("Error: недостаточно аргументов")
                continue
            if args[0].lower() != "insert" or args[1].lower() != "into":
                print("Error: ожидается 'insert into'")
                continue
            if args[3].lower() != "values":
                print("Error: ожидается ключевое слово 'values'")
                continue
            table_name = args[2]
            values_part = " ".join(args[4:]) 
            if not (values_part.startswith("(") and values_part.endswith(")")):
                print("Error: значения должны быть в скобках")
                continue
            raw_values = values_part[1:-1].strip()
            if not raw_values:
                print("Error: список значений пуст")
                continue
            values = [v.strip() for v in raw_values.split(",")]
            if any(v == "" for v in values):
                print("Error: пустое значение в списке")
                continue
            try:
                new_id = insert(metadata, table_name, values)
            except ValueError as e:
                print(f'{e}')
            else:
                print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')

                
        elif command == "select":
            if len(args) < 3:
                print("Использование: select from <имя_таблицы> [where столбец = значение AND ...]")
                continue
            if args[1].lower() != "from":
                print("Error: ожидается 'select from'")
                continue
            table_name = args[2]
            if table_name not in metadata:
                print(f"Ошибка: таблица {table_name} не существует")
                continue
            where_clause = None
            if len(args) > 3:
                if args[3].lower() != "where":
                    print("Использование: select from <имя_таблицы> [where столбец = значение AND ...]")
                    continue
                where_text = " ".join(args[4:])
                if not where_text:
                    print("Ошибка: после where нет условий")
                    continue
                try:
                    where_clause = parse_where(where_text)
                except (ValueError, IndexError):
                    print("Ошибка: некорректное условие where")
                    continue
            data = load_table_data(table_name)
            if not isinstance(data, list):
                print("Ошибка: данные таблицы должны быть списком строк")
                continue
            column_names = [col[0] for col in metadata[table_name]]
            selected_data = select(data, where_clause)
            print_table(selected_data, column_names)

        elif command == "delete":
            if len(args) < 5:
                print("Использование: delete from <имя_таблицы> where столбец = значение AND ...")
                continue
            if args[1].lower() != "from":
                print("Error: ожидается 'delete from'")
                continue
            table_name = args[2]
            if table_name not in metadata:
                print(f"Ошибка: таблица {table_name} не существует")
                continue
            if args[3].lower() != "where":
                print("Использование: delete from <имя_таблицы> where столбец = значение AND ...")
                continue
            where_text = " ".join(args[4:])
            if not where_text:
                print("Ошибка: после where нет условий")
                continue
            try:
                where_clause = parse_where(where_text)
            except (ValueError, IndexError):
                print("Ошибка: некорректное условие where")
                continue
            if not where_clause:
                print("Ошибка: delete без условий запрещён")
                continue

            data = load_table_data(table_name)
            if not isinstance(data, list):
                print("Ошибка: данные таблицы должны быть списком строк")
                continue

            deleted_rows = [
                row for row in data
                if all(row.get(k) == v for k, v in where_clause.items())
            ]
            remaining = delete(data, where_clause)
            save_table_data(table_name, remaining)
            if not deleted_rows:
                print("Записи для удаления не найдены.")
            else:
                for row in deleted_rows:
                    print(
                        f'Запись с ID={row["ID"]} успешно удалена из таблицы "{table_name}".'
                    )

        elif command == "update":
            usage = "Использование: update <имя_таблицы> set столбец = значение, ... where столбец = значение AND ..."
            if len(args) < 6:
                print(usage)
                continue

            table_name = args[1]
            if table_name not in metadata:
                print(f"Ошибка: таблица {table_name} не существует")
                continue
            if args[2].lower() != "set":
                print("Error: ожидается 'update <имя_таблицы> set'")
                continue

            where_idx = None
            for i, token in enumerate(args[3:], start=3):
                if token.lower() == "where":
                    where_idx = i
                    break
            if where_idx is None:
                print("Ошибка: update без условий запрещён")
                continue

            set_text = " ".join(args[3:where_idx])
            where_text = " ".join(args[where_idx + 1:])
            if not set_text:
                print("Ошибка: после set нет значений")
                continue
            if not where_text:
                print("Ошибка: после where нет условий")
                continue

            try:
                set_clause = parse_set(set_text)
                where_clause = parse_where(where_text)
            except (ValueError, IndexError):
                print("Ошибка: некорректные условия set/where")
                continue
            if not set_clause:
                print("Ошибка: после set нет значений")
                continue
            if not where_clause:
                print("Ошибка: update без условий запрещён")
                continue

            data = load_table_data(table_name)
            if not isinstance(data, list):
                print("Ошибка: данные таблицы должны быть списком строк")
                continue

            try:
                matched_rows = [
                    row for row in data
                    if all(row.get(k) == v for k, v in where_clause.items())
                ]
                update(data, set_clause, where_clause)
            except ValueError as e:
                print(e)
                continue

            save_table_data(table_name, data)
            if not matched_rows:
                print("Записи для обновления не найдены.")
            else:
                for row in matched_rows:
                    print(
                        f'Запись с ID={row["ID"]} в таблице "{table_name}" успешно обновлена.'
                    )

        elif command == "info":
            if len(args) != 2:
                print("Использование: info <имя_таблицы>")
                continue
            table_name = args[1]
            if table_name not in metadata:
                print(f"Ошибка: таблица {table_name} не существует")
                continue
            data = load_table_data(table_name)
            columns = metadata[table_name]
            s = ", ".join(":".join(col) for col in columns)
            print(f"Таблица: {table_name}")
            print(f"Столбцы: {s}")
            print(f"Количество записей: {len(data) if isinstance(data, list) else 0}")

        elif command == "help":
            print_help()

        else:
            print(f"Неизвестная команда: {command}")



# src/primitive_db/engine.py
def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def parse_value(s):
    s = s.strip()

    lowered = s.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return int(s)
    except ValueError:
        return s

def parse_conditions(text, sep):
    result = {}
    for part in text.split(sep):
        key, value = part.split("=")
        result[key.strip()] = parse_value(value)

    return result

def parse_where(text):
    return parse_conditions(text, " AND ")

def parse_set(text):
    return parse_conditions(text, ",")


