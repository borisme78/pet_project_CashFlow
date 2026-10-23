---
name: sql-postgresql
description: Design, review and optimize PostgreSQL schemas, ANSI-oriented SQL queries and database migrations; distinguish portable SQL from PostgreSQL extensions.
---

# SQL: PostgreSQL та переносимий SQL

## Порядок роботи Codex

- Спочатку прочитай застосовні `AGENTS.md`, конфігурацію, залежності та сусідній код. Визнач фактичні версії й команди перевірки; не оновлюй стек без потреби задачі.
- Дотримуйся наявних домовленостей. Наведені нижче архітектурні підходи — рекомендовані рішення, а не вимога переписати проєкт.
- Зміни обмежуй запитом. Не читай і не виводь секрети; використовуй приклади зі штучними даними.
- Запусти доречні наявні перевірки; для зміни поведінки перевір успішні, помилкові й граничні сценарії. У звіті назви зміни, виконані перевірки та обмеження.


## Практики та архітектура

- Розрізняй ANSI/ISO SQL і PostgreSQL-специфічні можливості. Не називай `ILIKE`, `JSONB`, `RETURNING` чи параметри драйвера переносимим ANSI SQL.
- Починай із нормалізованої моделі (зазвичай 3НФ): одна сутність на таблицю, ключі й залежності явні. Денормалізуй лише за виміряної потреби та визнач механізм узгодження.
- Інваріанти даних закріплюй `NOT NULL`, `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `CHECK`. Для грошей використовуй `NUMERIC` або ціле число мінімальних одиниць з валютою; для часових моментів PostgreSQL — `TIMESTAMPTZ`.
- Явно називай колонки й умови JOIN; уникай `SELECT *` у контрактах застосунку. Враховуй `NULL`, кратність JOIN, стабільний порядок сортування та межі пагінації.
- Міграції версіонуй; оцінюй блокування, сумісність старого/нового коду та відновлення. Для великих таблиць розділяй додавання схеми, backfill і введення обмежень.

## Безпека та продуктивність

- Значення передавай через bind parameters драйвера; SQL-ідентифікатори — через безпечний composition API та allowlist. Не використовуй f-рядки для SQL.
- Роль застосунку має мінімальні права; міграції виконує окрема роль. У багатокористувацьких системах авторизація/tenant filter обов'язкові незалежно від параметризації.
- Перевіряй план `EXPLAIN`; `EXPLAIN (ANALYZE, BUFFERS)` фактично виконує запит, тому застосовуй на безпечному середовищі з репрезентативними даними. Rollback не скасовує всі можливі зовнішні ефекти.
- Індекси добирай за WHERE/JOIN/ORDER BY і вимірами; вони коштують місця та сповільнюють запис. PostgreSQL не створює індекс на referencing FK автоматично. Не вважай sequential scan помилкою сам по собі.
- Групу пов'язаних змін виконуй у транзакції. Для read-modify-write використовуй атомарний UPDATE або належні блокування; враховуй deadlock і обмежений retry всієї транзакції.

## Приклад

```sql
CREATE TABLE invoice (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customer (id),
    amount NUMERIC(14, 2) NOT NULL CHECK (amount >= 0),
    issued_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX invoice_customer_issued_idx
    ON invoice (customer_id, issued_at DESC, id DESC);
```

Передумова: таблиця `customer(id)` вже існує. Параметризація через Psycopg 3 (це Python API, `%s` не є ANSI SQL):

```python
with connection.cursor() as cursor:
    cursor.execute(
        "SELECT id, amount FROM invoice WHERE customer_id = %s "
        "ORDER BY issued_at DESC, id DESC LIMIT %s",
        (customer_id, 50),
    )
    invoices = cursor.fetchall()
```

## Джерела

- [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [PostgreSQL EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
- [Psycopg parameters](https://www.psycopg.org/psycopg3/docs/basic/params.html)
