"""Декораторы обработки ошибок, подтверждения, замера времени и кэширования."""

import time

from .constants import CONFIRM_YES, is_table_status_error


def handle_db_errors(func):
    """Перехватывает типовые ошибки БД и печатает понятное сообщение."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            message = str(error)
            if is_table_status_error(message):
                print(f"Ошибка: {message}")
            else:
                print(f"Ошибка валидации: {message}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")

    return wrapper


def confirm_action(action_name):
    """Запрашивает подтверждение перед опасной операцией."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            prompt = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            confirmation = input(prompt)
            if confirmation == CONFIRM_YES:
                return func(*args, **kwargs)
            print("Операция отменена.")
            return None

        return wrapper

    return decorator


def log_time(func):
    """Печатает время выполнения обёрнутой функции."""

    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start_time
            print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")

    return wrapper


def create_cacher():
    """Возвращает функцию cache_result с кэшем в замыкании."""

    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        value = value_func()
        cache[key] = value
        return value

    return cache_result
