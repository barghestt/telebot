import os
import re
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from uvicorn import run
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI-приложение
fastapi_app = FastAPI()

# Список запрещённых слов
BAD_WORDS = [
    "хер", "урод", "сволочь", "дрянь", "ублюдок", "сучка", "падла",
    "тварь", "шалава", "проститутка", "мудак", "гнида", "мразь",
    "говнюк", "сука", "блядь", "бля", "блядский", "блядина", "блядовать",
    "пизда", "пиздец", "пиздануть", "пиздатый", "пиздеть", "пиздёж", "пиздюк",
    "ебать", "ебёт", "ебал", "ебанутая", "ебанутый", "ебануться", "ёб",
    "пидор", "пидорас", "пидорок", "пидорюга", "пидорнуть", "пидорский",
    "хуй", "хуета", "хуйня", "хули", "хуевый", "хуярить", "хуяк"
]

# Предкомпиляция регулярного выражения
BAD_WORD_PATTERN = re.compile(r'\b(' + '|'.join(map(re.escape, BAD_WORDS)) + r')\b', re.IGNORECASE)

# Проверка наличия необходимых переменных окружения
if not (TOKEN := os.getenv("TELEGRAM_TOKEN")):
    logger.error("Не найден TELEGRAM_TOKEN")
    exit(1)

if not (WEBHOOK_URL := os.getenv("WEB_URL")):
    logger.error("Не найден WEB_URL")
    exit(1)

# Создаем Telegram приложение
application = Application.builder().token(TOKEN).build()

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_first_name = update.message.from_user.first_name
    await update.message.chat.send_message(f"Привет, {user_first_name}! Я ваш бот для проверки сообщений.")

# Функция для проверки сообщений на наличие мата
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.lower()
    if BAD_WORD_PATTERN.search(message_text):
        user = update.message.from_user
        user_first_name = user.first_name
        user_username = f"@{user.username}" if user.username else ""
        
        # Создаем ссылку на профиль пользователя через его user_id
        user_profile_link = f"[{user_first_name}](tg://user?id={user.id})"

        warning_message = f"{user_profile_link} {user_username}, пожалуйста, не используй мат!"
        
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            text=warning_message,
            parse_mode="Markdown",
            message_thread_id=update.message.message_thread_id
        )
        try:
            await update.message.delete()
        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения: {e}")

# Добавляем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

# Создаем эндпоинт вебхука
@fastapi_app.post("/webhook")
async def telegram_webhook(request: Request):
    """Обрабатываем запросы от Telegram"""
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука: {e}")

# Эндпоинт для проверки состояния
@fastapi_app.get("/health")
def health_check():
    return {"status": "ok"}

# Основная функция для запуска FastAPI
if __name__ == "__main__":
    # Устанавливаем вебхук
    asyncio.run(application.bot.set_webhook(WEBHOOK_URL + "/webhook"))
    # Запускаем FastAPI
    run("bot:fastapi_app", host="0.0.0.0", port=int(os.getenv("PORT", 8443)), reload=True)
