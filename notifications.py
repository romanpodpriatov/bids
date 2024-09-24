# notifications.py

import logging
from telegram.ext import ApplicationBuilder
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

async def notify_user(telegram_id, message):
    try:
        await application.bot.send_message(chat_id=telegram_id, text=message)
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение пользователю {telegram_id}: {e}")
