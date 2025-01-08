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

# Проверка наличия мата в сообщении
def contains_bad_words(text):
    pattern = re.compile(r"|".join(re.escape(word) for word in BAD_WORDS), re.IGNORECASE)
    return bool(pattern.search(text))

# Функция для проверки сообщений
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.lower()

    # Создаем регулярное выражение для поиска всех плохих слов
    pattern = re.compile(r'\b(' + '|'.join(map(re.escape, BAD_WORDS)) + r')\b', re.IGNORECASE)
    
    # Проверяем, есть ли плохие слова в сообщении
    if pattern.search(message_text):
        # Получаем имя пользователя и его username
        user_first_name = update.message.from_user.first_name
        user_username = f"@{update.message.from_user.username}" if update.message.from_user.username else ""
        
        # Формируем предупреждающее сообщение
        warning_message = f"{user_first_name} {user_username}, пожалуйста, не используй мат!"
        
        # Отправляем предупреждение в ту же тему
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            text=warning_message,
            message_thread_id=update.message.message_thread_id  # Указываем ID темы
        )
        
        # Удаляем сообщение
        await update.message.delete()

# Основной код
if __name__ == "__main__":
    # Вставьте свой токен бота
    TOKEN = os.getenv("TELEGRAM_TOKEN")  # Лучше использовать переменные окружения

    # Получаем порт из переменной окружения
    PORT = int(os.getenv("PORT", 8443))

    # Создаём приложение
    application = Application.builder().token(TOKEN).build()

    # Команда /start
    application.add_handler(CommandHandler("start", start))

    # Обработка всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

    # Устанавливаем Webhook
    WEBHOOK_URL = os.getenv("WEB_URL")  # Например, https://your-app.onrender.com
    application.run_webhook(
        listen="0.0.0.0",  # Прослушиваем все подключения
        port=PORT,        # Используем порт из Render
        webhook_url=WEBHOOK_URL  # URL Webhook
    )
