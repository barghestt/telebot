from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Список запрещённых слов (можно дополнять)
BAD_WORDS = ["плохое слово1", "плохое слово2", "мат1", "мат2"]

# Функция для старта бота
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Привет! Я слежу за порядком в группе и удаляю сообщения с матом.")

# Функция для проверки сообщений
def check_message(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text.lower()
    for bad_word in BAD_WORDS:
        if bad_word in message_text:
            # Удаляем сообщение
            update.message.delete()
            # Отправляем предупреждение
            update.message.reply_text(
                f"{update.message.from_user.first_name}, пожалуйста, не используй мат!"
            )
            break

# Основной код
if __name__ == "__main__":
    # Вставьте свой токен бота
    import os
    TOKEN = os.getenv("7644372092:AAH_w8xAu-euH9VzmdJp7hw4pzpL9PM7S70")

    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    # Команда /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Обработка всех текстовых сообщений
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, check_message))

    # Запуск бота
    updater.start_polling()
    updater.idle()
