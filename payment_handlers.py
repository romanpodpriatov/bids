# payment_handlers.py
from telegram import LabeledPrice, Update
from telegram.ext import ContextTypes
from models import db, User, Payment
import os

PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN')

async def start_buy_stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    title = "Покупка звёзд XTR"
    description = "Покупка виртуальных звёзд для участия в аукционах"
    payload = "XTR-Stars-Payload"
    currency = "USD"
    prices = [LabeledPrice("100 XTR звёзд", 100 * 100)]  # Цена в центах
    await context.bot.send_invoice(chat_id, title, description, payload, PROVIDER_TOKEN, currency, prices)

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload != "XTR-Stars-Payload":
        await query.answer(ok=False, error_message="Что-то пошло не так...")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    telegram_id = str(update.effective_user.id)
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if user:
        user.stars_balance += 100  # Пополнение баланса на 100 звёзд
        new_payment = Payment(
            user_id=user.id,
            amount=payment.total_amount / 100,
            currency=payment.currency,
            telegram_payment_id=payment.provider_payment_charge_id,
            status='successful'
        )
        db.session.add(new_payment)
        db.session.commit()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Платеж успешно завершён. Ваш баланс пополнен.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Пользователь не найден. Обратитесь в поддержку.")
