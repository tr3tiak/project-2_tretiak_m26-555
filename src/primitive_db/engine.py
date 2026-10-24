'''Этот файл будет отвечать за запуск, игровой цикл и парсинг команд.'''

import prompt
import os
from .core import create_table, drop_table, list_table
from .utils import load_metadata, save_metadata
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
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(BASE_DIR, "../../db_meta.json")

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
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")