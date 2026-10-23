---
name: flask-patterns
description: Build and maintain Flask applications using factories, blueprints, explicit validation and secure request handling; apply to Flask-specific tasks.
---

# Flask

## Порядок роботи Codex

- Спочатку прочитай застосовні `AGENTS.md`, конфігурацію, залежності та сусідній код. Визнач фактичні версії й команди перевірки; не оновлюй стек без потреби задачі.
- Дотримуйся наявних домовленостей. Наведені нижче архітектурні підходи — рекомендовані рішення, а не вимога переписати проєкт.
- Зміни обмежуй запитом. Не читай і не виводь секрети; використовуй приклади зі штучними даними.
- Запусти доречні наявні перевірки; для зміни поведінки перевір успішні, помилкові й граничні сценарії. У звіті назви зміни, виконані перевірки та обмеження.


## Практики та архітектура

- Для застосунків, що ростуть, використовуй application factory `create_app`, Blueprints за предметною областю й extensions з `init_app`; не створюй циклічні імпорти через глобальний app.
- Орієнтовна структура: `app/__init__.py`, `app/extensions.py`, `app/invoices/routes.py`, `app/invoices/services.py`, `templates/`, `static/`, `migrations/`, `tests/`. Не розбивай маленьку програму механічно.
- Route відповідає за HTTP/validation, бізнес-логіка — за правила, шар даних — за запити та транзакції. Використовуй міграції й закривай DB-ресурси на teardown.

## Безпека

- Flask не надає автоматичного загального CSRF-захисту. Для cookie-auth форм і запитів зі зміною стану налаштуй Flask-WTF `CSRFProtect` або еквівалент, не вимикай його для зручності. GET не змінює стан.
- ORM/драйвер використовуй із параметрами; обмежуй дані поточним користувачем/tenant. Не передавай довільні поля запиту в модель.
- Залишай Jinja autoescape; не застосовуй `safe` до недовірених даних. Валідуй upload: розмір, тип, згенероване ім'я, зберігання поза виконуваним/public шляхом.
- SECRET_KEY — зі сховища секретів або середовища, без fallback у production; сесія Flask підписана, але не зашифрована. Не клади в неї секретні дані.
- Production: HTTPS, Secure/HttpOnly/SameSite cookies, DEBUG=False, перевірені hosts, ліміти запитів і налаштований WSGI server. ProxyFix довіряє лише відомій кількості проксі. SameSite не замінює CSRF.

## Приклад factory (Flask 3.1+, Flask-WTF)

```python
import os

from flask import Flask
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    )
    if test_config is None:
        app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    else:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY is required")
    csrf.init_app(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
```

Передумови: встановлені Flask та Flask-WTF. Для локального HTTP cookie Secure не надсилається — використовуй окрему dev/test конфігурацію. У звичайній Jinja POST-формі додай `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`; FlaskForm має власний helper. Інтеграційно перевір відхилення POST без токена та прийняття валідного токена, авторизацію, rollback і конфігурацію production.

## Джерела

- [Flask factories](https://flask.palletsprojects.com/en/stable/patterns/appfactories/)
- [Flask security](https://flask.palletsprojects.com/en/stable/web-security/)
- [Flask-WTF CSRF](https://flask-wtf.readthedocs.io/en/1.2.x/csrf/)
