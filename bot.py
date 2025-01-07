from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import re

# Список слов, которые считаются матом (можно расширить)
BAD_WORDS = ["плохое слово1", "плохое слово2", "плохое слово3"]

# Проверка наличия мата в сообщении
def contains_bad_words(text):
    pattern = re.compile(r"|".join(re.escape(word) for word in BAD_WORDS), re.IGNORECASE)
    return bool(pattern.search(text))

# Функция для удаления сообщений с матом
async def filter_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        if contains_bad_words(update.message.text):
            try:
                await update.message.delete()
                print(f"Удалено сообщение от {update.message.from_user.username}: {update.message.text}")
            except Exception as e:
                print(f"Не удалось удалить сообщение: {e}")

# Команда для проверки, что бот работает
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен и работает! Добавьте меня администратором в группу.")

if __name__ == "__main__":
    # Создайте приложение
    app = ApplicationBuilder().token("ВАШ_TELEGRAM_TOKEN").build()

    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_bad_words))

    # Запуск бота
    print("Бот запущен!")
    app.run_polling()
