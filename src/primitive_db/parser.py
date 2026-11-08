"""Разбор условий where, set и литералов значений."""

from .constants import SET_SEPARATOR, WHERE_SEPARATOR


def parse_value(raw: str):
    """Преобразует строковый литерал из команды в Python-значение."""
    raw = raw.strip()
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return int(raw)
    except ValueError:
        return raw


def parse_conditions(text: str, sep: str) -> dict:
    """Разбирает список условий вида key=value, разделённых sep."""
    result = {}
    for part in text.split(sep):
        key, value = part.split("=", 1)
        result[key.strip()] = parse_value(value)
    return result


def parse_where(text: str) -> dict:
    """Разбирает условие WHERE (части соединены AND)."""
    return parse_conditions(text, WHERE_SEPARATOR)


def parse_set(text: str) -> dict:
    """Разбирает список присваиваний SET (части через запятую)."""
    return parse_conditions(text, SET_SEPARATOR)


def parse_insert_values(values_part: str) -> list[str]:
    """Извлекает список значений из фрагмента values (...)."""
    if not (values_part.startswith("(") and values_part.endswith(")")):
        raise ValueError("значения должны быть в скобках")
    raw_values = values_part[1:-1].strip()
    if not raw_values:
        raise ValueError("список значений пуст")
    values = [value.strip() for value in raw_values.split(",")]
    if any(value == "" for value in values):
        raise ValueError("пустое значение в списке")
    return values
