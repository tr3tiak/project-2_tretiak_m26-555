'''Для вспомогательных функций (например, работа с файлами).'''
import json

def load_metadata(filepath):
    try:
        file = open(filepath, "r")
        return json.load(file)
    except FileNotFoundError as e:
        print(f'Ошибка: {e}')
        return {}

def save_metadata(filepath, data):
    try:
        file = open(filepath, "w")
        json.dump(data, file, ensure_ascii=False, indent=4)
    except FileNotFoundError as e:
        print(f'Ошибка: {e}')