# Инструкция: приватный GPT с Action на OAuth и его callback URL

Завести в ChatGPT приватный GPT, подключить к нему Action — вызовы HTTP API по схеме OpenAPI — с
входом через OAuth, получить **callback URL** и проверить вызов кнопкой **Test**. Нужен платный
план ChatGPT (Plus и выше): на бесплатном создавать GPT нельзя.

**ИИ-агент** — Claude, Codex или другой ИИ-агент, в чате с которым ты получил эту инструкцию.

Callback URL секретом не является. Client secret — является: в чат и в заметки он не идёт.

Составлена 2026-09-16 без сверки с экраном: если кнопка называется иначе — ищи по смыслу и поправь
инструкцию.

## Значения для подстановки

Имена в обратных кавычках в шагах ниже (`client-id`, `schema-url`, …) — не текст для ввода, а
места для подстановки. Значения тебе дают вместе с этой инструкцией: ИИ-агент в сообщении или
инструкция задачи таблицей «поле → значение». Значения нет нигде — спроси ИИ-агента, а не угадывай.

| Поле | Что это | Пример |
|---|---|---|
| `gpt-name` | имя GPT | `Learning API` |
| `client-id` | id OAuth-клиента, не секрет | `example-gpt-actions` |
| `secret-source` | откуда взять client secret | «уже в буфере обмена» |
| `authorization-url` | адрес авторизации сервера | `https://api.example.org/oauth2/authorize` |
| `token-url` | адрес выдачи токена | `https://api.example.org/oauth2/token` |
| `scope` | права через пробел | `read write` |
| `token-exchange` | способ передачи id и secret | `Default (POST request)` или «любой» |
| `schema-url` | адрес схемы OpenAPI | `https://api.example.org/openapi.yaml` |
| `test-operation` | операция для проверки | `listItems` |

## 🚨 Порядок: callback URL появляется последним

Окно OAuth **не показывает** callback URL и не сохраняется без client id и secret, поэтому
callback URL появляется только после сохранения (шаг 8). Кнопка **Test** до шага 9 падает, и это
нормально.

## Шаги

1. Открой https://chatgpt.com → слева **GPTs** (или **Explore GPTs**) → **Create**.
2. Вкладка **Configure** (Настроить). В **Name** введи `gpt-name`. Остальные поля — описание,
   инструкции, картинка — **можно оставить пустыми**.
3. Внизу вкладки нажми **Create new action**.
4. **Authentication** → шестерёнка → выбери **OAuth** и заполни:

   | Поле окна | Значение |
   |---|---|
   | Client ID | `client-id` |
   | Client Secret | из `secret-source` |
   | Authorization URL | `authorization-url` |
   | Token URL | `token-url` |
   | Scope | `scope` |
   | Token Exchange Method | `token-exchange` |

   Нажми **Save**.
5. В **Schema** нажми **Import from URL**, введи `schema-url`, **Import**. Ниже появится список
   операций — проверь, что он не пустой. Ошибка разбора схемы — перепиши её текст целиком.
6. **Privacy policy** — **можно оставить пустым**: он нужен только для публикации.
7. Сохрани GPT: кнопка **Create** / **Update** справа сверху → в доступе выбери **Only me**
   (Только я). Не публикуй в GPT Store.
8. Вернись в **Configure** → в блоке **Actions** под списком действий появилась строка
   **Callback URL** вида `https://chat.openai.com/aip/g-…/oauth/callback`. Строки нет — обнови
   страницу и открой действие заново.
9. Напиши ИИ-агенту в чат одну строку, подставив callback URL из шага 8 целиком:

   ```text
   callback URL: <callback URL из шага 8>
   ```

   Дождись его ответа и переходи к шагу 10.
10. Открой действие → у `test-operation` нажми **Test**. Справа в превью появится кнопка
    **Sign in with …** → вход в браузере → возврат в ChatGPT → ответ операции.

## Как понять, что удалось

Готово, когда **Test** вернул ответ операции, а не ошибку. Если нет:

| Что видно | Что делать |
|---|---|
| под схемой красным `In components section, schemas subsection is not an object` | не твоя ошибка, а схемы: перешли текст ИИ-агенту, после его ответа — **Import from URL** заново |
| сервер при входе ругается на `redirect_uri` | повтори шаг 9: скопируй callback URL заново, **целиком** |
| после входа ChatGPT пишет про ошибку токена, `invalid_client` | secret введён не тот или с пробелом — вставь заново из `secret-source`, **Save**, **Update** |
| callback URL поменялся (действие пересоздано) | повтори шаг 9 с новым URL |
| любая другая ошибка | перешли ИИ-агенту её текст целиком, включая код |
