import os
import requests
from flask import Flask, request, jsonify
from anthropic import Anthropic
from system_prompt import SYSTEM_PROMPT

app = Flask(__name__)

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# История диалогов по chat_id (хранится в памяти)
conversation_history = {}
MAX_HISTORY = 20  # последних сообщений


def send_message(chat_id, text):
    """Отправить сообщение в Telegram."""
    # Telegram ограничивает длину сообщения 4096 символами
    if len(text) > 4000:
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for chunk in chunks:
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": chunk,
                "parse_mode": "Markdown"
            })
    else:
        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })


def send_typing(chat_id):
    """Показать индикатор печати."""
    requests.post(f"{TELEGRAM_API}/sendChatAction", json={
        "chat_id": chat_id,
        "action": "typing"
    })


def reset_history(chat_id):
    """Сбросить историю диалога."""
    if chat_id in conversation_history:
        del conversation_history[chat_id]


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return jsonify({"ok": True})

    message = data["message"]
    chat_id = message["chat"]["id"]
    user_name = message["chat"].get("first_name", "")

    # Команды
    if "text" in message:
        text = message["text"].strip()

        if text == "/start":
            reset_history(chat_id)
            send_message(chat_id,
                f"Привет, {user_name}! 👋\n\n"
                "Я помогу рассчитать смету на видео- или фотопроект.\n\n"
                "Просто скинь бриф — опиши что нужно снять, где, сколько смен, "
                "что нужно в постпродакшне. Я задам уточняющие вопросы если нужно и посчитаю КП.\n\n"
                "Команды:\n"
                "/start — начать заново\n"
                "/reset — очистить историю диалога"
            )
            return jsonify({"ok": True})

        if text == "/reset":
            reset_history(chat_id)
            send_message(chat_id, "История очищена. Отправь новый бриф.")
            return jsonify({"ok": True})

        user_input = text

    elif "document" in message:
        # Если прислали файл — попросить описать текстом
        caption = message.get("caption", "")
        if caption:
            user_input = f"[Пользователь прислал файл с подписью]: {caption}"
        else:
            send_message(chat_id,
                "Файл получен, но я пока не могу читать документы напрямую. "
                "Скопируй текст брифа и отправь его сообщением — я посчитаю смету."
            )
            return jsonify({"ok": True})
    else:
        return jsonify({"ok": True})

    # Показать индикатор печати
    send_typing(chat_id)

    # Инициализировать историю для нового чата
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []

    # Добавить сообщение пользователя
    conversation_history[chat_id].append({
        "role": "user",
        "content": user_input
    })

    # Обрезать историю до MAX_HISTORY сообщений
    if len(conversation_history[chat_id]) > MAX_HISTORY:
        conversation_history[chat_id] = conversation_history[chat_id][-MAX_HISTORY:]

    # Вызов Claude
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=conversation_history[chat_id]
        )

        assistant_text = response.content[0].text

        # Сохранить ответ в историю
        conversation_history[chat_id].append({
            "role": "assistant",
            "content": assistant_text
        })

        send_message(chat_id, assistant_text)

    except Exception as e:
        send_message(chat_id, f"Ошибка при обращении к ИИ: {str(e)}\nПопробуй ещё раз.")

    return jsonify({"ok": True})


@app.route("/", methods=["GET"])
def index():
    return "Smeta Bot is running ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
