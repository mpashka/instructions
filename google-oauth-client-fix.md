# Инструкция: вход через Google отклонён — адрес возврата и тестовые пользователи

Починить две самые частые ошибки входа через Google на своём сайте: `redirect_uri_mismatch` и
`access_blocked` («приложение не проверено»). Сам OAuth-клиент Google уже заведён; секретов
инструкция не касается и в чат их не просит.

Составлена 2026-09-16 без сверки с экраном: если пункт меню называется иначе — ищи по смыслу и
поправь инструкцию.

## Значения, которые подставляет инструкция задачи

| Поле | Что это | Пример |
|---|---|---|
| `project` | проект в Google Cloud | `example-app` |
| `client-name` | имя OAuth-клиента в списке | `Web client 1` |
| `redirect-uri` | адрес возврата, ровно как его шлёт сайт | `https://app.example.org/login/oauth2/code/google` |
| `test-user` | почта, которой разрешён вход | «твой gmail» |

## Шаги

1. Открой https://console.cloud.google.com/auth/clients, сверху выбери проект `project`.
2. Какая ошибка на экране Google:
   - **`redirect_uri_mismatch`** — шаг 3;
   - **`access_blocked`**, «This app is blocked», «app has not completed the Google verification
     process» — шаг 4.
3. Открой клиент `client-name` → **Authorized redirect URIs** → **Add URI** → введи `redirect-uri`.
   Ровно так: схема `https`, без завершающего `/`, без `*`. **Save**. Изменение вступает в силу
   через несколько минут — повтори вход через 5 минут.
4. Слева **Audience** → **Test users** → **Add users** → введи `test-user` → **Save**. Статус
   **Publishing status: Testing** не меняй: публикация приложения запускает проверку Google, для
   своего сайта она не нужна.

## Как понять, что удалось

Вход через Google возвращает на сайт без экрана ошибки. Ошибка та же через 5 минут — в тексте
ошибки (**error details**) есть `redirect_uri=…`: сравни его с `redirect-uri` посимвольно и отдай
агенту оба. Ошибка другая — перепиши её текст целиком, включая код.
