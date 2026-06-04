# Инструкция по деплою на Render.com

## Что нужно заранее

1. **Telegram Bot Token** — получить у @BotFather в Telegram
2. **Anthropic API Key** — на сайте console.anthropic.com
3. **Аккаунт на GitHub** — бесплатный
4. **Аккаунт на Render.com** — бесплатный

---

## Шаг 1 — Создать репозиторий на GitHub

1. Зайди на github.com → New repository
2. Назови: `smeta-bot`
3. Сделай **Public**
4. Нажми "Create repository"
5. Загрузи файлы: `main.py`, `system_prompt.py`, `requirements.txt`

---

## Шаг 2 — Деплой на Render.com

1. Зайди на render.com → **New +** → **Web Service**
2. Подключи GitHub и выбери репозиторий `smeta-bot`
3. Настройки:
   - **Name:** smeta-bot (любое)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn main:app`
   - **Instance Type:** Free
4. Нажми **Create Web Service**
5. Подожди 2–3 минуты, пока задеплоится
6. Скопируй URL вида: `https://smeta-bot.onrender.com`

---

## Шаг 3 — Добавить переменные окружения

В Render → твой сервис → **Environment** → Add:

| Key | Value |
|-----|-------|
| `TELEGRAM_TOKEN` | токен от @BotFather |
| `ANTHROPIC_API_KEY` | ключ с console.anthropic.com |

Сохрани — сервис перезапустится автоматически.

---

## Шаг 4 — Подключить вебхук Telegram

Открой браузер и перейди по ссылке (подставь свои данные):

```
https://api.telegram.org/bot[TELEGRAM_TOKEN]/setWebhook?url=https://[твой-адрес].onrender.com/webhook
```

Пример:
```
https://api.telegram.org/bot123456:ABC-DEF/setWebhook?url=https://smeta-bot.onrender.com/webhook
```

Должен появиться ответ:
```json
{"ok": true, "result": true, "description": "Webhook was set"}
```

---

## Шаг 5 — Проверить

Открой своего бота в Telegram и отправь `/start`

---

## Важно про бесплатный план Render

На бесплатном плане сервис "засыпает" через 15 минут бездействия.
При первом сообщении после паузы — задержка 30–60 секунд (пока "просыпается").

Если это критично — перейди на план Starter ($7/мес) — сервис работает постоянно.

---

## Команды бота

- `/start` — приветствие и сброс истории
- `/reset` — очистить историю диалога (начать новую смету)
