import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Список запрещённых слов (можно дополнять)
BAD_WORDS = [
    "хер",
    "жопа",
    "дурак",
    "тупой",
    "глупый",
    "блин",
    "черт",
    "задница",
    "идиот",
    "скотина",
    "урод",
    "сволочь",
    "дрянь",
    "ублюдок",
    "подонок",
    "козел",
    "сучка",
    "падла",
    "паразит",
    "тварь",
    "шалава",
    "проститутка",
    "мудак",
    "гнида",
    "засранец",
    "обормот",
    "выдра",
    "мразь",
    "говнюк",
    "дерьмо",
    "сука",
    "блядь",  # В виде цензуры
    "пиздец",  # В виде цензуры
    "ебать",
    "пидор",
    "хуй"
]

# Функция для старта бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я слежу за порядком в группе и удаляю сообщения с матом."
    )
from telegram.helpers import escape_markdown
# Функция для проверки сообщений
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.message.from_user
        # Экранируем имя пользователя для MarkdownV2
        user_name = escape_markdown(user.first_name, version=2)
        user_link = f"[{user_name}](tg://user?id={user.id})"

        message_text = update.message.text.lower()
        for bad_word in BAD_WORDS:
            if bad_word in message_text:
                await update.message.reply_text(
                    f"{user_link}, пожалуйста, не используй мат!",
                    parse_mode="MarkdownV2"
                )
                await update.message.delete()
                break
    except Exception as e:
        print(f"Ошибка: {e}")


# Основной код
if __name__ == "__main__":
    # Вставьте свой токен бота
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8154721393:AAF2IG0NwZ9YeW7eYzzH-tUY6CEYM-z9VLg")  # Лучше использовать переменные окружения

    # Получаем порт из переменной окружения
    PORT = int(os.getenv("PORT", 8443))

    # Создаём приложение
    application = Application.builder().token(TOKEN).build()

    # Команда /start
    application.add_handler(CommandHandler("start", start))

    # Обработка всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

    # Устанавливаем Webhook
    WEBHOOK_URL = f"https://telebot-e8cj.onrender.com"
    application.run_webhook(
        listen="0.0.0.0",  # Прослушиваем все подключения
        port=PORT,        # Используем порт из Render
        webhook_url=WEBHOOK_URL  # URL Webhook
    )
