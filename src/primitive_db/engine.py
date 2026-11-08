"""Основной цикл приложения и разбор пользовательских команд."""

import shlex

import prompt

from .constants import (
    CREATE_TABLE_USAGE,
    DELETE_USAGE,
    DROP_TABLE_USAGE,
    INFO_USAGE,
    META_FILE,
    PROMPT,
    SELECT_USAGE,
    UPDATE_USAGE,
)
from .core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_table,
    print_table,
    select,
    update,
)
from .parser import parse_insert_values, parse_set, parse_where
from .utils import load_metadata, load_table_data, save_metadata, save_table_data


def welcome():
    """Приветственный режим первого запуска (демо)."""
    name = prompt.string(""" Первая попытка запустить проект!
***
<command> exit - выйти из программы
<command> help - справочная информация
Введите команду: """)
    if name == "exit":
        print("Выход из программы")
    elif name == "help":
        print("Справочная информация")


def run():
    """Запускает интерактивную сессию базы данных."""
    filepath = META_FILE

    while True:
        metadata = load_metadata(filepath)

        try:
            user_input = prompt.string(PROMPT)
            args = shlex.split(user_input)
        except ValueError as error:
            print(f"Ошибка разбора команды: {error}")
            continue

        if not args:
            continue

        command = args[0]

        if command in ("exit", "quit"):
            break

        if command == "create_table":
            if len(args) < 2:
                print(CREATE_TABLE_USAGE)
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
                column_desc = ", ".join(
                    ":".join(column) for column in metadata[table_name]
                )
                print(
                    f"Таблица {table_name} успешно создана со столбцами: {column_desc}"
                )

        elif command == "drop_table":
            if len(args) != 2:
                print(DROP_TABLE_USAGE)
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
            try:
                values = parse_insert_values(values_part)
            except ValueError as error:
                print(f"Error: {error}")
                continue

            new_id = insert(metadata, table_name, values)
            if new_id is None:
                continue
            print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')

        elif command == "select":
            if len(args) < 3:
                print(SELECT_USAGE)
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
                    print(SELECT_USAGE)
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
            column_names = [column[0] for column in metadata[table_name]]
            selected_data = select(data, where_clause)
            if selected_data is None:
                continue
            print_table(selected_data, column_names)

        elif command == "delete":
            if len(args) < 5:
                print(DELETE_USAGE)
                continue
            if args[1].lower() != "from":
                print("Error: ожидается 'delete from'")
                continue
            table_name = args[2]
            if table_name not in metadata:
                print(f"Ошибка: таблица {table_name} не существует")
                continue
            if args[3].lower() != "where":
                print(DELETE_USAGE)
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
                row
                for row in data
                if all(row.get(key) == value for key, value in where_clause.items())
            ]
            remaining = delete(data, where_clause)
            if remaining is None:
                continue
            save_table_data(table_name, remaining)
            if not deleted_rows:
                print("Записи для удаления не найдены.")
            else:
                for row in deleted_rows:
                    row_id = row["ID"]
                    print(
                        f"Запись с ID={row_id} успешно удалена "
                        f'из таблицы "{table_name}".'
                    )

        elif command == "update":
            if len(args) < 6:
                print(UPDATE_USAGE)
                continue

            table_name = args[1]
            if table_name not in metadata:
                print(f"Ошибка: таблица {table_name} не существует")
                continue
            if args[2].lower() != "set":
                print("Error: ожидается 'update <имя_таблицы> set'")
                continue

            where_idx = None
            for index, token in enumerate(args[3:], start=3):
                if token.lower() == "where":
                    where_idx = index
                    break
            if where_idx is None:
                print("Ошибка: update без условий запрещён")
                continue

            set_text = " ".join(args[3:where_idx])
            where_text = " ".join(args[where_idx + 1 :])
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

            matched_rows = [
                row
                for row in data
                if all(row.get(key) == value for key, value in where_clause.items())
            ]
            updated = update(data, set_clause, where_clause)
            if updated is None:
                continue

            save_table_data(table_name, data)
            if not matched_rows:
                print("Записи для обновления не найдены.")
            else:
                for row in matched_rows:
                    row_id = row["ID"]
                    print(
                        f'Запись с ID={row_id} в таблице "{table_name}" '
                        "успешно обновлена."
                    )

        elif command == "info":
            if len(args) != 2:
                print(INFO_USAGE)
                continue
            table_name = args[1]
            if table_name not in metadata:
                print(f"Ошибка: таблица {table_name} не существует")
                continue
            data = load_table_data(table_name)
            columns = metadata[table_name]
            column_desc = ", ".join(":".join(column) for column in columns)
            print(f"Таблица: {table_name}")
            print(f"Столбцы: {column_desc}")
            print(f"Количество записей: {len(data) if isinstance(data, list) else 0}")

        elif command == "help":
            print_help()

        else:
            print(f"Неизвестная команда: {command}")


def print_help():
    """Печатает справку по доступным командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")
