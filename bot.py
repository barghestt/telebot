import logging
from telegram.helpers import escape_markdown
from telegram import Update
from telegram.constants import ParseMode
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

# Функция для удаления сообщений с матом и отправки предупреждения
async def filter_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        if contains_bad_words(update.message.text):
            # Сохраняем необходимые данные
            user = update.message.from_user
            chat = update.message.chat
            user_id = user.id
            user_name = escape_markdown(user.first_name, version=2)
            user_mention = f"[{user_name}](tg://user?id={user_id})"
            
            try:
                # Удаляем сообщение
                await update.message.delete()
                logger.info(f"Удалено сообщение от {user.username or user.full_name}: {update.message.text}")
                
                # Экранируем все специальные символы Markdown
                warning_message = f"Пожалуйста, {user_mention}, не используйте нецензурную лексику!"
                warning_message = escape_markdown(warning_message, version=2)  # Экранирование

                # Отправляем предупреждение
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=warning_message,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            except Exception as e:
                logger.error(f"Ошибка при удалении сообщения или отправке предупреждения: {e}")

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_bad_words))

    # Установка Webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8443)),
        webhook_url=WEBHOOK_URL
    )
