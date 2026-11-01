'''Для вспомогательных функций (например, работа с файлами).'''
import json
import os


def load_metadata(filepath):
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError as e:
        print(f'Ошибка: {e}')
        return {}

def save_metadata(filepath, data):
    try:
        with open(filepath, "w") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except FileNotFoundError as e:
        print(f'Ошибка: {e}')


def load_table_data(table_name):
    try:
        with open(f'data/{table_name}.json', "r") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    
def save_table_data(table_name, data):
    os.makedirs("data", exist_ok=True)
    try:
        with open(f'data/{table_name}.json', "w") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except FileNotFoundError as e:
        print(f'Ошибка: {e}')