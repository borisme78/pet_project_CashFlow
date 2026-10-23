---
name: git-workflow
description: Apply safe Git branching, Conventional Commits, merges and conflict resolution when a task requires Git operations or workflow guidance.
---

# Git: безпечний робочий процес

## Порядок роботи Codex

- Спочатку прочитай застосовні `AGENTS.md`, конфігурацію, залежності та сусідній код. Визнач фактичні версії й команди перевірки; не оновлюй стек без потреби задачі.
- Дотримуйся наявних домовленостей. Наведені нижче архітектурні підходи — рекомендовані рішення, а не вимога переписати проєкт.
- Зміни обмежуй запитом. Не читай і не виводь секрети; використовуй приклади зі штучними даними.
- Запусти доречні наявні перевірки; для зміни поведінки перевір успішні, помилкові й граничні сценарії. У звіті назви зміни, виконані перевірки та обмеження.


## Практики та стандарти

- Перед операціями перевір `git status --short --branch`, поточну гілку, remotes та diff. Не включай чужі чи незавершені зміни до власного коміту.
- Використовуй flow команди. Якщо його немає, рекомендуй короткоживучу `feat/...` або `fix/...` від основної гілки та PR; Git Flow з `develop/release/hotfix` доречний за потреби паралельних релізів, а не обов'язковий.
- Коміти мають бути цілісними. Формат Conventional Commits: `type(scope): description`; `feat` — функція, `fix` — виправлення, `!` або footer `BREAKING CHANGE:` — несумісна зміна. Інші типи є домовленістю команди.

## Історія, конфлікти та безпека

- Не виконуй `reset --hard`, `clean -fd`, видалення гілок, переписування опублікованої історії чи force push без відповідної авторизації. Звичайний запит написати код не означає дозволу push/merge.
- Для опублікованого коміту зазвичай використовуй `revert`; rebase застосовуй до власної неопублікованої гілки. Навіть `--force-with-lease` переписує історію; за потреби погодженого переписування перевір точний очікуваний remote SHA, не використовуй простий `--force`.
- Під час конфлікту прочитай обидві зміни та їхню мету, узгодь поведінку, прибери маркери, перевір результат тестами. Не приймай усю сторону `ours/theirs` механічно; під час rebase їх значення відрізняється від інтуїтивного.
- Не коміть `.env`, ключі, токени чи приватні дані. Якщо секрет потрапив в історію, спочатку відклич/заміни його; видалення файла не усуває витік.

## Приклад workflow

Команди — зразок для чистої робочої копії; `main`, remote і шлях адаптуй. `fetch` та `push` потребують мережі; push виконуй лише в межах запиту користувача.

```sh
git status --short --branch
git fetch origin
git switch -c feat/invoice-validation origin/main
# Внеси зміни та виконай перевірки проєкту.
git diff --check
git diff -- path/to/changed-file
git add -- path/to/changed-file
git diff --cached
git commit -m "feat(invoices): validate invoice totals"
git push -u origin feat/invoice-validation
```

Для синхронізації зі спільною основною гілкою без переписування історії: `git merge origin/main`. Після конфлікту — виправ файли, `git add -- <files>`, `git merge --continue`; скасування незавершеного merge — `git merge --abort`. Для rebase використовуй відповідно `git rebase --continue` / `git rebase --abort`, лише якщо rebase був обраний свідомо.

## Джерела

- [Git reference](https://git-scm.com/docs)
- [git-push: force-with-lease](https://git-scm.com/docs/git-push)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
