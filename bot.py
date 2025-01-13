from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import logging
import threading
import asyncio
import os

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Список запрещенных слов (матерные слова)
bad_words = [
    'хуй',
    'говно',
    # Добавьте сюда все нужные слова
]

# Функция для проверки наличия плохих слов в сообщении
def contains_bad_words(text):
    for word in bad_words:
        if word in text.lower():
            return True
    return False

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    await update.message.reply_text("Бот готов удалять матерные сообщения в вашем канале.")

# Обработчик входящих сообщений
async def filter_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    text = message.text or message.caption
    
    if text and contains_bad_words(text):
        await message.reply_text("Пожалуйста, не используйте нецензурную лексику в этом канале.")
        await message.delete()

# Создаем Flask приложение
app = Flask(__name__)

# Замените 'YOUR_TOKEN' на ваш токен от BotFather
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Замените 'YOUR_RENDER_URL' на ваш URL на Render
WEBHOOK_URL = os.getenv("WEB_URL")

bot = Bot(TOKEN)

# Асинхронное приложение для обработки обновлений
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT | filters.CAPTION & (~filters.COMMAND), filter_messages))

# Инициализация приложения
async def initialize_application():
    await application.initialize()

# Функция для обработки обновлений в отдельном потоке
async def process_update(update):
    await application.process_update(update)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    
    # Убедимся, что приложение инициализировано
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize_application())
    
    # Обрабатываем обновление в отдельном потоке
    loop.run_until_complete(process_update(update))
    loop.close()
    
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    # Устанавливаем вебхук
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
