---
name: python-quality
description: Write and refactor Python modules, scripts and tests using idiomatic typing, resource management and explicit error handling; follow the repository Python version.
---

# Python: якість та межі відповідальності

## Порядок роботи Codex

- Спочатку прочитай застосовні `AGENTS.md`, конфігурацію, залежності та сусідній код. Визнач фактичні версії й команди перевірки; не оновлюй стек без потреби задачі.
- Дотримуйся наявних домовленостей. Наведені нижче архітектурні підходи — рекомендовані рішення, а не вимога переписати проєкт.
- Зміни обмежуй запитом. Не читай і не виводь секрети; використовуй приклади зі штучними даними.
- Запусти доречні наявні перевірки; для зміни поведінки перевір успішні, помилкові й граничні сценарії. У звіті назви зміни, виконані перевірки та обмеження.


## Практики та стандарти

- Орієнтуйся на PEP 8, PEP 257 і наявний formatter; 4 пробіли, `snake_case` для функцій/змінних, `PascalCase` для класів. PEP 8 рекомендує 79 символів; 88 у Black — інша домовленість, не вимога Python.
- Додавай type hints до публічних меж; вони не замінюють runtime validation. Не використовуй синтаксис новіший за цільовий Python.
- Ізолюй середовище через `venv`, декларації залежностей зберігай у форматі проєкту; для відтворюваності використовуй підтримуваний lock/constraints механізм. Ruff/Black/mypy/pytest — можливі інструменти, а не обов'язковий стандарт.
- Відокремлюй обчислення від I/O; використовуй невеликі функції, явні залежності та контекстні менеджери. Не додавай service/repository шари до простого скрипта без потреби.

## Безпека та помилки

- Перехоплюй конкретні винятки, зберігай причину через `raise ... from ...`; не приховуй помилки `except: pass`.
- Не завантажуй недовірений `pickle`, не виконуй `eval`/`exec` з введенням користувача. Для subprocess передавай список аргументів без shell; перевіряй також небезпечні аргументи цільової команди.
- Встановлюй timeout для зовнішніх операцій, закривай ресурси; не журналюй токени чи персональні дані. Для шляхів перевіряй дозволений корінь і traversal.
- Для фінансів — `Decimal` зі строкового введення; перевіряй скінченність, діапазон і бізнес-правила округлення.

## Приклад (Python 3.10+)

```python
from decimal import Decimal, InvalidOperation


def parse_amount(raw: str) -> Decimal:
    """Parse a finite, non-negative amount with at most two decimals."""
    try:
        amount = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError("Invalid amount") from exc
    if not amount.is_finite() or not Decimal("0") <= amount <= Decimal("999999999999.99"):
        raise ValueError("Amount out of range")
    if amount != amount.quantize(Decimal("0.01")):
        raise ValueError("At most two decimal places are allowed")
    return amount.quantize(Decimal("0.01"))
```

Перевір `0`, `12.50`, від'ємне число, `NaN`, `Infinity`, надмірну точність і неправильний текст. Межа суми тут — приклад бізнес-правила.

## Джерела

- [PEP 8](https://peps.python.org/pep-0008/)
- [venv](https://docs.python.org/3/library/venv.html)
