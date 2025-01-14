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
    
def escape_markdown_v2(text: str) -> str:
    """Экранирует специальные символы для MarkdownV2."""
    escape_chars = r"*_[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

# Функция для проверки сообщений на наличие мата
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.lower()

    if BAD_WORD_PATTERN.search(message_text):
        # Экранируем имя пользователя
        user_first_name = escape_markdown_v2(update.message.from_user.first_name or "Пользователь")
        # Экранируем username, если он есть
        user_username = f"@{escape_markdown_v2(update.message.from_user.username)}" if update.message.from_user.username else ""
        # Формируем ссылку на профиль
        user_id = update.message.from_user.id
        user_link = f"[{user_first_name}](tg://user?id={user_id})"
        
        # Если username есть, добавляем его в сообщение
        warning_message = (
            f"{user_first_name} ({user_username})"
            if user_username
            else user_link
        )
        warning_message += ", пожалуйста, не используй мат!"
        
        # Отправляем сообщение с экранированными данными
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            text=warning_message,
            parse_mode="MarkdownV2",  # Обязательно указываем MarkdownV2
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
