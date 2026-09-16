<!-- template-note:begin -->
> 🚨 **Шаблон, а не инструкция.** `{{…}}` — места для значений; готовую инструкцию собирает
> `render` (README репозитория).
<!-- template-note:end -->
# Инструкция: вход через Google на {{site}} отклонён

Починить две самые частые ошибки входа через Google: `redirect_uri_mismatch` и `access_blocked`
(«приложение не проверено»). Сам OAuth-клиент Google уже заведён; секретов инструкция не касается.

**ИИ-агент** — Claude, Codex или другой ИИ-агент, от которого ты получил эту инструкцию.

Составлена 2026-09-16 без сверки с экраном: если пункт меню называется иначе — ищи по смыслу.

## Шаги

1. Открой https://console.cloud.google.com/auth/clients. Сверху выбери проект, в списке клиентов
   которого есть клиент с **Client ID** `{{google_client_id}}`.
2. Какая ошибка была на экране Google:
   - **`redirect_uri_mismatch`** — шаг 3;
   - **`access_blocked`**, «This app is blocked», «app has not completed the Google verification
     process» — шаг 4.
3. Открой клиент с Client ID `{{google_client_id}}` → **Authorized redirect URIs** → **Add URI** →
   введи:

   ```text
   {{redirect_uri}}
   ```

   Ровно так, без завершающего `/`. **Save**. Изменение вступает в силу через несколько минут —
   повтори вход на {{site}} через 5 минут.
4. Слева **Audience** → **Test users** → **Add users** → введи адрес почты, которой входишь на
   {{site}} → **Save**. Статус **Publishing status: Testing** не меняй: публикация приложения
   запускает проверку Google, для своего сайта она не нужна.

## Как понять, что удалось

Вход через Google возвращает на {{site}} без экрана ошибки. Если нет — перешли ИИ-агенту текст
ошибки целиком, включая код и строку `redirect_uri=…` из **error details**, если она есть.
