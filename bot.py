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

# Функция для проверки сообщений
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.lower()
    for bad_word in BAD_WORDS:
        if bad_word in message_text:
            # Отправляем предупреждение до удаления
            await update.message.reply_text(
                f"{update.message.from_user.first_name}, пожалуйста, не используй мат!"
            )
            # Удаляем сообщение
            await update.message.delete()
            break


# Основной код
if __name__ == "__main__":
    # Вставьте свой токен бота
    
    TOKEN = "7644372092:AAH_w8xAu-euH9VzmdJp7hw4pzpL9PM7S70"

    # Создаём приложение
    application = Application.builder().token(TOKEN).build()

    # Команда /start
    application.add_handler(CommandHandler("start", start))

    # Обработка всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

    # Запуск бота
    application.run_polling()
