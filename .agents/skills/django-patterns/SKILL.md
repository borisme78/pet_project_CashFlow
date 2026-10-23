---
name: django-patterns
description: Build and maintain Django apps, models, views, forms and migrations with ORM safety, CSRF protection and object-level authorization.
---

# Django

## Порядок роботи Codex

- Спочатку прочитай застосовні `AGENTS.md`, конфігурацію, залежності та сусідній код. Визнач фактичні версії й команди перевірки; не оновлюй стек без потреби задачі.
- Дотримуйся наявних домовленостей. Наведені нижче архітектурні підходи — рекомендовані рішення, а не вимога переписати проєкт.
- Зміни обмежуй запитом. Не читай і не виводь секрети; використовуй приклади зі штучними даними.
- Запусти доречні наявні перевірки; для зміни поведінки перевір успішні, помилкові й граничні сценарії. У звіті назви зміни, виконані перевірки та обмеження.


## Практики та архітектура

- Визнач встановлену версію Django і використовуй документацію для неї; не впроваджуй API новішого релізу без погодженого оновлення.
- Project містить settings/urls/asgi/wsgi; apps розділяй за предметними областями, не за типами файлів. Views координують HTTP, Forms/ModelForms перевіряють введення, models/constraints зберігають інваріанти. Окремий service layer додавай для складних операцій.
- У ModelForm задавай явний `fields`; міграції перевіряй і версіонуй. `save()` сам по собі не викликає `full_clean()`.
- Усувай виміряні N+1 через `select_related` / `prefetch_related`; додавай пагінацію. Для групи записів — `transaction.atomic`, для конкурентного read-modify-write — `F()` або належні блокування. Зовнішні події відправляй після commit; для гарантованої доставки розглянь outbox.

## Безпека

- Зберігай SecurityMiddleware та CsrfViewMiddleware; у POST-формах `{% csrf_token %}`. `csrf_exempt` не є звичайним виправленням помилки токена; для webhook потрібна окрема перевірка автентичності.
- ORM параметризує значення; raw SQL теж має використовувати params. Динамічні назви полів/сортування обмежуй allowlist.
- Автентифікація не означає право на кожний об'єкт: фільтруй queryset за користувачем/tenant перед читанням чи зміною. Не довіряй owner_id з POST.
- Не вимикай template autoescape для недовірених даних. Для passwords використовуй Django auth/hashers; upload і media обслуговуй без можливості виконання.
- Production: DEBUG=False, явні ALLOWED_HOSTS, секрети поза репозиторієм, HTTPS і secure cookies. HSTS вмикай після перевірки HTTPS та піддоменів. `CSRF_TRUSTED_ORIGINS` задавай лише для реальних довірених origin.

## Приклад захищеного читання

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import Invoice


@login_required
@require_GET
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(
        Invoice.objects.filter(owner=request.user),
        pk=invoice_id,
    )
    return render(request, "invoices/detail.html", {"invoice": invoice})
```

Передумови: модель `Invoice` з `owner` FK на користувача, налаштовані auth/session middleware, URL з `invoice_id` та шаблон. Неіснуючий і чужий об'єкти дають 404. Перевір доступ власника, відмову іншому користувачу та redirect для anonymous; для змін стану окремо перевір POST/CSRF.

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
# Запускай із реальною production-конфігурацією в безпечному середовищі:
python manage.py check --deploy
```

## Джерела

- [Django security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Deployment checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
