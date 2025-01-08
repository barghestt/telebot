import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os
import re

# Список слов, которые считаются матом
BAD_WORDS = ["падла", "бля", "хуй", "сука", "мудила", "пиздец"]

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Проверка наличия мата в сообщении
def contains_bad_words(text):
    pattern = re.compile(r"|".join(re.escape(word) for word in BAD_WORDS), re.IGNORECASE)
    return bool(pattern.search(text))

# Функция для проверки сообщений
async def check_message(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text

    # Проверяем сообщение на наличие мата
    if contains_bad_words(message_text):
        # Получаем имя пользователя и его username
        user_first_name = update.message.from_user.first_name
        user_username = f"@{update.message.from_user.username}" if update.message.from_user.username else ""
        
        # Формируем предупреждающее сообщение
        warning_message = f"{user_first_name} {user_username}, пожалуйста, не используй мат!"
        
        # Отправляем предупреждение в ту же тему
        await update.message.reply_text(warning_message)

        # Удаляем сообщение
        await update.message.delete()

# Команда для проверки, что бот работает
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Бот запущен и работает! Добавьте меня администратором в группу.")

async def main():
    # Получаем токен
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    PORT = os.getenv("PORT", 8443)  # Порт, предоставленный сервером

    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))  # Используем check_message

    # Запуск бота на указанном порту
    await application.run_polling(port=int(PORT))

if __name__ == "__main__":
    import asyncio
    asyncio.create_task(main())
