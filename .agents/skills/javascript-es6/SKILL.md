---
name: javascript-es6
description: Implement and review ES6+ JavaScript modules, browser interactions and asynchronous data access, respecting the configured runtime and browser support.
---

# JavaScript ES6+

## Порядок роботи Codex

- Спочатку прочитай застосовні `AGENTS.md`, конфігурацію, залежності та сусідній код. Визнач фактичні версії й команди перевірки; не оновлюй стек без потреби задачі.
- Дотримуйся наявних домовленостей. Наведені нижче архітектурні підходи — рекомендовані рішення, а не вимога переписати проєкт.
- Зміни обмежуй запитом. Не читай і не виводь секрети; використовуй приклади зі штучними даними.
- Запусти доречні наявні перевірки; для зміни поведінки перевір успішні, помилкові й граничні сценарії. У звіті назви зміни, виконані перевірки та обмеження.


## Практики та архітектура

- Використовуй ES modules, `const` за замовчуванням і `let` для переприсвоєння; `===`, явні перетворення типів, невеликі функції та ранні повернення.
- Визнач підтримувані браузери/Node і конфігурацію збірки. ES6+ не означає підтримку всіх нових API; `fetch`, DOM і `AbortController` — API середовища, а не самого ECMAScript.
- Розділяй отримання даних, бізнес-правила й DOM. Дотримуйся ESLint/formatter проєкту; не нав'язуй framework або TypeScript.
- Використовуй `async/await` з обробкою помилок; `Promise.all` — для незалежних операцій з обмеженою паралельністю. Враховуй скасування, timeout і гонки запитів.

## Безпека

- Для тексту використовуй `textContent`; не передавай недовірений HTML у `innerHTML`. Якщо HTML потрібен, застосовуй перевірений sanitizer за контекстом.
- Валідуй структуру відповіді; `fetch` не кидає виняток автоматично на HTTP 4xx/5xx. Сервер має повторно перевіряти дані й права.
- Не вбудовуй секрети у frontend bundle. Cookie-auth запити, що змінюють стан, мають узгоджений із сервером CSRF-захист; CORS не замінює авторизацію.

## Приклад (сучасний браузер, ES module)

```javascript
export async function loadInvoiceCount(output, signal) {
  const response = await fetch('/api/invoices/count', {
    headers: { Accept: 'application/json' },
    signal,
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  const data = await response.json();
  if (!Number.isSafeInteger(data.count) || data.count < 0) {
    throw new TypeError('Invalid invoice count');
  }
  output.textContent = String(data.count);
}
```

Викликаючий код має передати DOM-елемент, обробити помилку й за потреби скасувати запит. Перевір успіх, HTTP-помилку, неправильний JSON/схему та скасування.

## Джерела

- [ECMAScript specification](https://tc39.es/ecma262/)
- [MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
