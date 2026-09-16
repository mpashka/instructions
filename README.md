# Общие инструкции для человека

Повторяющиеся действия на сайтах и в программах, которые ИИ-агент поручает человеку. Инструкция
задачи ссылается сюда: «возьми `~/Projects/github/m_pashka/instructions/<имя>.md`, подставь
значения» — и таблица «универсальное поле → значение».

Правило, по которому пишутся инструкции, — `~/Projects/github/m_pashka/ai/rules/user-instructions.md`.
Главное из него: что можно заскриптовать — скриптуется, здесь только то, что остаётся рукам.

Репозиторий — `git@github.com:mpashka/instructions.git`, **публичный**: ничего рабочего, личного и
секретного.

## Раскладка

| Путь | Что |
|---|---|
| `<имя>.md` | инструкция: цель, шаги, необязательные поля, как понять, что удалось; дата проверки |
| `dialogs/<сайт>.html` | диалоги многоязычного сайта: рисунок, универсальные имена полей (`data-field`), переключатель RU/EN |
| `dialogs/_template.html` | шаблон описания диалогов — копировать, а не править |

Дерево пока плоское. Иерархия вводится, когда нужное перестанет находиться по списку ниже.

## Инструкции

- [llm-chat-answer.md](llm-chat-answer.md) — вставить готовый промпт в чат нейросети и сохранить ответ файлом
- [xiaomi-adb-install.md](xiaomi-adb-install.md) — разрешить `adb install` на телефоне Xiaomi и подтвердить установку
- [cloudflare-web-analytics.md](cloudflare-web-analytics.md) — завести сайт в Cloudflare Web Analytics и получить токен счётчика
- [chatgpt-gpt-oauth-action.md](chatgpt-gpt-oauth-action.md) — приватный GPT с Action на OAuth: поля, callback URL, проверка Test
- [google-oauth-client-fix.md](google-oauth-client-fix.md) — вход через Google отклонён: `redirect_uri_mismatch`, тестовые пользователи
