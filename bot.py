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

# Создаем Telegram приложение
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEB_URL")

application = Application.builder().token(TOKEN).build()

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_first_name = update.message.from_user.first_name
    await update.message.chat.send_message(f"Привет, {user_first_name}! Я ваш бот для проверки сообщений.")
    
# Функция для проверки сообщений на наличие мата
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.lower()

    if BAD_WORD_PATTERN.search(message_text):
        # Получаем имя и фамилию пользователя
        user_first_name = update.message.from_user.first_name or "Пользователь"
        user_last_name = update.message.from_user.last_name or ""
        full_name = f"{user_first_name} {user_last_name}".strip()  # Объединяем имя и фамилию
        
        # Проверяем наличие username
        user_username = update.message.from_user.username
        if user_username:
            user_info = f"{full_name} (@{user_username})"
        else:
            user_id = update.message.from_user.id
            # Формируем HTML-ссылку
            user_info = f"<a href='tg://user?id={user_id}'>{full_name}</a>"
        
        # Формируем предупреждающее сообщение
        warning_message = f"{user_info}, пожалуйста, не используй мат!"
        
        # Отправляем сообщение
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            text=warning_message,  # Текст с HTML-ссылкой
            parse_mode="HTML",  # Указываем использование HTML
            message_thread_id=update.message.message_thread_id
        )
        await update.message.delete()


# Добавляем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

# Создаем эндпоинт вебхука
@fastapi_app.post("/webhook")
async def telegram_webhook(request: Request):
    """Обрабатываем запросы от Telegram"""
    try:
        # Инициализируем приложение (гарантированно один раз)
        await application.initialize()

        # Обрабатываем обновления
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        print(f"Ошибка при обработке вебхука: {e}")

# Эндпоинт для проверки состояния
@fastapi_app.get("/health")
def health_check():
    return {"status": "ok"}

# Основная функция для запуска FastAPI
if __name__ == "__main__":
    # Устанавливаем вебхук
    import asyncio
    asyncio.run(application.bot.set_webhook(WEBHOOK_URL + "/webhook"))

    # Запускаем FastAPI
    run("bot:fastapi_app", host="0.0.0.0", port=int(os.getenv("PORT", 8443)), reload=True)
