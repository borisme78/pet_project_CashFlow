---
name: html-css-quality
description: Build and improve semantic HTML and responsive CSS with accessible forms, keyboard interaction and maintainable styling; preserve the existing design system.
---

# HTML та CSS

## Порядок роботи Codex

- Спочатку прочитай застосовні `AGENTS.md`, конфігурацію, залежності та сусідній код. Визнач фактичні версії й команди перевірки; не оновлюй стек без потреби задачі.
- Дотримуйся наявних домовленостей. Наведені нижче архітектурні підходи — рекомендовані рішення, а не вимога переписати проєкт.
- Зміни обмежуй запитом. Не читай і не виводь секрети; використовуй приклади зі штучними даними.
- Запусти доречні наявні перевірки; для зміни поведінки перевір успішні, помилкові й граничні сценарії. У звіті назви зміни, виконані перевірки та обмеження.


## Практики та архітектура

- HTML — Living Standard; CSS складається з модулів, тому «CSS3» не є єдиною поточною версією. Перевір підтримку нових можливостей у цільових браузерах.
- Використовуй семантичні `main`, `nav`, `section`, заголовки за структурою документа; посилання для навігації, `button` для дій. Нативні елементи кращі за саморобні ARIA-віджети.
- Зберігай наявну систему стилів; використовуй custom properties для токенів, Grid/Flexbox для layout, низьку специфічність. Не додавай `!important` чи framework без конкретної причини.
- Адаптивність перевіряй за вмістом, а не лише фіксованими моделями пристроїв; уникай переповнення та фіксованих висот для текстових блоків.

## Доступність та безпека

- Орієнтир — WCAG 2.2 AA: клавіатура, видимий фокус, достатній контраст, текстові labels та повідомлення про помилки; не покладайся лише на колір. Повну відповідність не оголошуй за одним автоматичним тестом.
- Додавай коректний `lang`, viewport, alt відповідно до ролі зображення; декоративним — `alt=""`. Враховуй `prefers-reduced-motion` для анімації.
- Екрануй динамічні дані за контекстом; не вставляй введення користувача в HTML/CSS/URL без перевірки. CSP є додатковим захистом, не заміною escaping.
- Не вважай HTML validation авторизацією або перевіркою сервера. Для state-changing форм із cookie-auth потрібний серверний CSRF token.

## Приклад

```html
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Рахунки</title>
  <link rel="stylesheet" href="/static/invoices.css">
</head>
<body>
  <main class="page">
    <h1>Рахунки</h1>
    <form action="/invoices" method="get" class="filters">
      <label for="customer">Клієнт</label>
      <input id="customer" name="customer" autocomplete="organization">
      <button type="submit">Знайти</button>
    </form>
  </main>
</body>
</html>
```

```css
:root { --space: 1rem; --focus: #174ea6; }
* { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, sans-serif; line-height: 1.5; }
.page { max-inline-size: 64rem; margin-inline: auto; padding: var(--space); }
.filters { display: grid; gap: 0.5rem; max-inline-size: 28rem; }
input, button { font: inherit; padding: 0.75rem; min-inline-size: 0; }
:focus-visible { outline: 3px solid var(--focus); outline-offset: 3px; }
```

Це GET-фільтр без зміни стану. Перевір клавіатуру, масштаб 200%, вузький viewport, довгі написи та контраст.

## Джерела

- [HTML Standard](https://html.spec.whatwg.org/multipage/)
- [W3C CSS](https://www.w3.org/Style/CSS/)
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
