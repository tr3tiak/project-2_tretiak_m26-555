# primitive-db

Консольная «база данных»: метаданные таблиц в `db_meta.json`, строки — в `data/*.json`. CRUD в терминале, декораторы для ошибок, подтверждения удаления и замера времени, кэш результатов `select`.

## Установка и запуск

```bash
make install
make run
```

Эквивалент без Makefile:

```bash
uv sync --all-groups
uv pip install -e .
database
```

Линтер (как в автопроверке):

```bash
make lint
```

Команда `database` использует `db_meta.json` и каталог `data/` из **текущей рабочей директории**.

## Архитектура

| Модуль | Назначение |
|--------|------------|
| `main.py` | Точка входа |
| `engine.py` | Цикл `db >`, разбор команд |
| `core.py` | Таблицы и CRUD |
| `utils.py` | Чтение/запись JSON |
| `parser.py` | `where`, `set`, `values` |
| `decorators.py` | `handle_db_errors`, `confirm_action`, `log_time`, `create_cacher` |
| `constants.py` | `META_FILE`, `VALID_TYPES`, тексты подсказок |

## Дополнительные возможности

**`@handle_db_errors`** — единый вывод ошибок валидации и отсутствующих таблиц/столбцов.

**`@confirm_action`** — перед `drop_table` и `delete` запрос: `Вы уверены, что хотите выполнить "…"? [y/n]:` (только `y` выполняет действие).

**`@log_time`** — для `insert` и `select` печатается время выполнения; повторный `select` использует кэш из `create_cacher()`.

## Демонстрация (asciinema)

Полный сценарий в `demo.cast`: создание таблицы → insert → select → update → delete (с подтверждением) → drop_table → exit.

```bash
asciinema play demo.cast
```

Перезапись:

```bash
make record
```

