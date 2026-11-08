"""Загрузка и сохранение метаданных и данных таблиц."""

import json
import os

from .constants import DATA_DIR, JSON_INDENT, META_FILE


def _table_data_path(table_name: str) -> str:
    """Возвращает путь к JSON-файлу данных таблицы."""
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_metadata(filepath: str = META_FILE) -> dict:
    """Читает описание таблиц из db_meta.json."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет описание таблиц в db_meta.json."""
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=JSON_INDENT)
    except FileNotFoundError as error:
        print(f"Ошибка: {error}")


def load_table_data(table_name: str) -> list:
    """Читает строки таблицы из data/<имя>.json."""
    try:
        with open(_table_data_path(table_name), encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list) -> None:
    """Записывает строки таблицы в data/<имя>.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(_table_data_path(table_name), "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=JSON_INDENT)
    except FileNotFoundError as error:
        print(f"Ошибка: {error}")
