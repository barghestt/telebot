import os
import re
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Список запрещённых слов
BAD_WORDS = [
    "хер", "жопа", "дурак", "тупой", "глупый", "блин", "черт", "задница", "идиот", "скотина", 
    "урод", "сволочь", "дрянь", "ублюдок", "подонок", "козел", "сучка", "падла", "паразит", 
    "тварь", "шалава", "проститутка", "мудак", "гнида", "засранец", "обормот", "выдра", "мразь", 
    "говнюк", "дерьмо", "сука", "блядь", "пиздец", "ебать", "пидор", "хуй"
]

# Предкомпиляция регулярного выражения для повышения эффективности
BAD_WORD_PATTERN = re.compile(r'\b(' + '|'.join(map(re.escape, BAD_WORDS)) + r')\b', re.IGNORECASE)

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_first_name = update.message.from_user.first_name
    await update.message.reply(f"Привет, {user_first_name}! Я ваш бот для проверки сообщений.")

# Функция для проверки сообщений на наличие мата
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.lower()

    # Проверяем наличие плохих слов с использованием предкомпилированного паттерна
    if BAD_WORD_PATTERN.search(message_text):
        user_first_name = update.message.from_user.first_name
        user_username = f"@{update.message.from_user.username}" if update.message.from_user.username else ""
        
        # Отправляем предупреждающее сообщение
        warning_message = f"{user_first_name} {user_username}, пожалуйста, не используй мат!"
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            text=warning_message,
            message_thread_id=update.message.message_thread_id
        )
        
        # Удаляем сообщение
        await update.message.delete()

# Основная функция для запуска бота
if __name__ == "__main__":
    # Токен бота и URL для вебхука
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    PORT = int(os.getenv("PORT", 8443))
    WEBHOOK_URL = os.getenv("WEB_URL")

    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчик для команды /start
    application.add_handler(CommandHandler("start", start))

    # Добавляем обработчик для текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

    # Запускаем вебхук
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )
