# Инструкция: приватный GPT с Action на OAuth и его callback URL

Завести в ChatGPT приватный GPT, подключить к нему Action — вызовы HTTP API по схеме OpenAPI — с
входом через OAuth, получить **callback URL** и проверить вызов кнопкой **Test**. Нужен платный
план ChatGPT (Plus и выше): на бесплатном создавать GPT нельзя.

Callback URL секретом не является. Client secret — является: в чат агенту и в заметки он не идёт,
его берут оттуда, куда положил агент (`secret-source`).

Составлена 2026-09-16 без сверки с экраном: если кнопка называется иначе — ищи по смыслу и поправь
инструкцию.

## Значения, которые подставляет инструкция задачи

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
| `callback-return` | куда отдать callback URL | «сообщением агенту» |

## 🚨 Порядок: callback URL появляется последним

Окно OAuth **не показывает** callback URL и не сохраняется без client id и secret. А сервер часто
не примет вход, пока не знает callback URL. Поэтому порядок всегда такой: сначала клиент на
сервере (id и secret выпускает агент), потом поля в редакторе, сохранение — и только тогда
callback URL уходит на сервер. До этого **Test** падает, и это нормально.

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
   **Callback URL** вида `https://chatgpt.com/aip/g-…/oauth/callback`. Строки нет — обнови
   страницу и открой действие заново.
9. Скопируй callback URL целиком и отдай его по `callback-return`. Дождись, пока агент скажет, что
   сервер его принял.
10. Открой действие → у `test-operation` нажми **Test**. Справа в превью появится кнопка
    **Sign in with …** → вход в браузере → возврат в ChatGPT → ответ операции.

## Как понять, что удалось

Готово, когда **Test** вернул ответ операции, а не ошибку. Если нет:

| Что видно | Что делать |
|---|---|
| сервер при входе ругается на `redirect_uri` | callback URL на сервере не тот: отдай его заново, **целиком**, без `/` в конце |
| после входа ChatGPT пишет про ошибку токена, `invalid_client` | secret введён не тот или с пробелом — вставь заново из `secret-source`, **Save**, **Update** |
| callback URL поменялся | так бывает после пересоздания действия — отдай новый по `callback-return` |
| любая другая ошибка | перепиши её текст целиком, включая код, и отдай вместе с callback URL |
