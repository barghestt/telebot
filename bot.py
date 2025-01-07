import logging
from telegram.helpers import escape_markdown
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import re

# Список слов, которые считаются матом
BAD_WORDS = ["падла", "бля", "хуй"]

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        # Отправляем предупреждение в ту же тему
        warning_message = f"{update.message.from_user.first_name}, пожалуйста, не используй мат!"
        
        # Используем chat_id и message_thread_id для отправки в нужную тему
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            text=warning_message,
            message_thread_id=update.message.message_thread_id  # Указываем ID темы
        )
        
        # Удаляем сообщение
        await update.message.delete()

# Команда для проверки, что бот работает
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен и работает! Добавьте меня администратором в группу.")

if __name__ == "__main__":
    # Получение токена и URL из переменных окружения
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    WEBHOOK_URL = os.getenv("WEB_URL")  # Например, https://your-app.onrender.com

    # Создание приложения
    app = ApplicationBuilder().token(TOKEN).build()

    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))  # Используем check_message

    # Установка Webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8443)),
        webhook_url=WEBHOOK_URL
    )
