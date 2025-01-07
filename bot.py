from telegram import Update
from telegram.constants import ParseMode  # Импорт ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import re

# Список слов, которые считаются матом
BAD_WORDS = ["падла", "бля", "хуй"]

# Проверка наличия мата в сообщении
def contains_bad_words(text):
    pattern = re.compile(r"|".join(re.escape(word) for word in BAD_WORDS), re.IGNORECASE)
    return bool(pattern.search(text))

# Функция для удаления сообщений с матом и отправки предупреждения
async def filter_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        if contains_bad_words(update.message.text):
            user = update.message.from_user  # Сохраняем информацию о пользователе
            chat = update.message.chat  # Сохраняем информацию о чате
            user_mention = f"[{user.first_name}](tg://user?id={user.id})"  # Формируем ссылку на профиль
            
            try:
                # Удаляем сообщение
                await update.message.delete()
                print(f"Удалено сообщение от {user.username or user.full_name}: {update.message.text}")
                
                # Отправляем предупреждение
                warning_message = f"Пожалуйста, {user_mention}, не используйте нецензурную лексику!"
                await chat.send_message(
                    text=warning_message,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            except Exception as e:
                print(f"Ошибка при удалении сообщения или отправке предупреждения: {e}")

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
