# primitive-db

Консольная база данных на JSON: описание таблиц хранится в `db_meta.json`, строки — в каталоге `data/`. Программа принимает SQL-подобные команды в терминале (`db >`), поддерживает создание и удаление таблиц, CRUD, декораторы для обработки ошибок, подтверждения опасных операций и замера времени, а также кэширование результатов `select`.

## Установка и запуск

**Рекомендуемый способ (Makefile):**

```bash
make install
make run
```

**Poetry (если используете его в курсе):**

```bash
poetry install
poetry run database
```

**Альтернатива через uv:**

```bash
uv sync --all-groups
uv pip install -e .
database
```

Проверка стиля кода:

```bash
make lint
# или: poetry run ruff check .
```

Команда `database` читает и пишет `db_meta.json` и `data/` в **текущей рабочей директории**.

## Управление таблицами

Команды для работы со схемой:

| Команда | Описание |
|--------|----------|
| `create_table <имя> <столбец:тип> ...` | Создать таблицу (столбец `ID:int` добавляется автоматически) |
| `list_tables` | Список таблиц |
| `drop_table <имя>` | Удалить таблицу (требует подтверждения `y`) |
| `info <имя>` | Схема и число записей |
| `help` | Справка |
| `exit` | Выход |

Пример:

```text
db > create_table users name:str age:int is_active:bool
Таблица users успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

db > list_tables
users

db > create_table users name:str
Ошибка валидации: Таблица 'users' уже существует

db > drop_table users
Вы уверены, что хотите выполнить "удаление таблицы"? [y/n]: n
Операция отменена.
```

**Запись:** установка, запуск, создание, список, ошибка, отмена удаления:

[![asciicast](https://asciinema.org/a/N4lwuzOTBvMQuR4Z.svg)](https://asciinema.org/a/N4lwuzOTBvMQuR4Z)

```bash
asciinema play install_tables.cast
```

## CRUD-операции

| Команда | Описание |
|--------|----------|
| `insert into <таблица> values (...)` | Добавить строку |
| `select from <таблица>` | Все записи |
| `select from <таблица> where <столбец> = <значение> [AND ...]` | Выборка с условием |
| `update <таблица> set <столбец> = <значение>, ... where ...` | Обновление |
| `delete from <таблица> where ...` | Удаление строк (подтверждение `y`) |

Пример:

```text
db > insert into users values ("Sergei", 28, true)
Функция insert выполнилась за 0.002 секунд.
Запись с ID=1 успешно добавлена в таблицу "users".

db > select from users where age = 28
Функция select выполнилась за 0.001 секунд.
+----+--------+-----+-----------+
| ID |  name  | age | is_active |
+----+--------+-----+-----------+
| 1  | Sergei |  28 |    True   |
+----+--------+-----+-----------+

db > update users set age = 29 where name = "Sergei"
Запись с ID=1 в таблице "users" успешно обновлена.

db > delete from users where ID = 1
Вы уверены, что хотите выполнить "удаление записей"? [y/n]: y
Запись с ID=1 успешно удалена из таблицы "users".
```

**Запись:** полный CRUD:

[![asciicast](https://asciinema.org/a/rQtJ6WVeCS7ax3QO.svg)](https://asciinema.org/a/rQtJ6WVeCS7ax3QO)

```bash
asciinema play crud.cast
```

## Новые возможности (декораторы)

- **`@handle_db_errors`** — перехват `ValueError`, `KeyError`, `FileNotFoundError` и вывод понятных сообщений вместо падения программы.
- **`@confirm_action`** — перед `drop_table` и `delete` запрос: `Вы уверены, что хотите выполнить "…"? [y/n]:`; только `y` выполняет действие.
- **`@log_time`** — для `insert` и `select` выводится `Функция <имя> выполнилась за X.XXX секунд.`
- **`create_cacher()`** — кэш повторяющихся `select` с теми же данными и условием.

Модули: `engine.py` (цикл), `core.py` (логика), `utils.py` (файлы), `parser.py` (разбор команд), `decorators.py`, `constants.py`.

## Демонстрация (asciinema)

### Основная запись курса

[![asciicast](https://asciinema.org/a/haPGQrmLNmnY9qjM.svg)](https://asciinema.org/a/haPGQrmLNmnY9qjM)

### Установка и управление таблицами

Полный сценарий от `make install` до создания, проверки и попытки удаления таблицы:

```bash
asciinema play install_tables.cast
```

### CRUD-операции

```bash
asciinema play crud.cast
```

### Финальная запись (декораторы и полный цикл)

От создания таблицы до insert/select/update/delete/drop с подтверждениями, ошибкой валидации и повторным `select` (кэш / `log_time`):

[![asciicast](https://asciinema.org/a/Tg9O3oXFnGr6tMGb.svg)](https://asciinema.org/a/Tg9O3oXFnGr6tMGb)

```bash
asciinema play demo.cast
```

Перезапись локальных файлов:

```bash
./scripts/record_install_and_tables.sh   # или asciinema rec install_tables.cast -c ...
./scripts/record_crud.sh
make record   # demo.cast = scripts/record_final.sh
asciinema upload demo.cast   # обновить запись на asciinema.org
```
