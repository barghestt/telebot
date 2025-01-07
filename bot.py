import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from bdw import BadWordFilter  # Импортируем класс BadWordFilter
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем экземпляр фильтра
bad_word_filter = BadWordFilter()

# Функция для проверки сообщений
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text

    # Проверяем сообщение на наличие мата
    if bad_word_filter.contains_bad_words(message_text):
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
