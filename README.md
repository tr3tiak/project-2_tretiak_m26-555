# primitive-db

Консольная база данных на JSON: описание таблиц хранится в `db_meta.json`, строки — в каталоге `data/`. Программа принимает SQL-подобные команды в терминале (`db >`), поддерживает создание и удаление таблиц, CRUD, декораторы для обработки ошибок, подтверждения опасных операций и замера времени, а также кэширование результатов `select`.

## Установка и запуск

**Makefile:**

```bash
make install
make run
```

**Poetry:**

```bash
poetry install
poetry run database
```

**uv (альтернатива):**

```bash
uv sync --all-groups
uv pip install -e .
database
```

Проверка стиля:

```bash
make lint
```

Команда `database` использует `db_meta.json` и `data/` в **текущей рабочей директории**.

## Управление таблицами

| Команда | Описание |
|--------|----------|
| `create_table <имя> <столбец:тип> ...` | Создать таблицу (столбец `ID:int` добавляется автоматически) |
| `list_tables` | Список таблиц |
| `drop_table <имя>` | Удалить таблицу (подтверждение `y`) |
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

## CRUD-операции

| Команда | Описание |
|--------|----------|
| `insert into <таблица> values (...)` | Добавить строку |
| `select from <таблица>` | Все записи |
| `select from <таблица> where ...` | Выборка с условием |
| `update <таблица> set ... where ...` | Обновление |
| `delete from <таблица> where ...` | Удаление (подтверждение `y`) |

Пример:

```text
db > insert into users values ("Sergei", 28, true)
Функция insert выполнилась за 0.002 секунд.
Запись с ID=1 успешно добавлена в таблицу "users".

db > select from users where age = 28
Функция select выполнилась за 0.001 секунд.

db > update users set age = 29 where name = "Sergei"
Запись с ID=1 в таблице "users" успешно обновлена.

db > delete from users where ID = 1
Вы уверены, что хотите выполнить "удаление записей"? [y/n]: y
Запись с ID=1 успешно удалена из таблицы "users".
```

## Новые возможности (декораторы)

- **`@handle_db_errors`** — понятные сообщения при ошибках валидации и отсутствующих таблицах/столбцах.
- **`@confirm_action`** — подтверждение перед `drop_table` и `delete`.
- **`@log_time`** — время выполнения `insert` и `select`.
- **`create_cacher()`** — кэш повторяющихся `select`.

## Демонстрация

Полный сценарий работы с БД (установка, таблицы, CRUD, декораторы):

[![asciicast](https://asciinema.org/a/haPGQrmLNmnY9qjM.svg)](https://asciinema.org/a/haPGQrmLNmnY9qjM)

Запись вручную: `asciinema rec`, затем `make install`, `database`, команды в терминале, `asciinema upload`.
