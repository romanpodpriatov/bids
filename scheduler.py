# scheduler.py

from flask_apscheduler import APScheduler
from models import db, Auction, Bid
from notifications import notify_user
from datetime import datetime
import asyncio

scheduler = APScheduler()

def finish_auction(auction_id):
    with scheduler.app.app_context():
        auction = Auction.query.get(auction_id)
        if auction and auction.is_active:
            auction.is_active = False
            db.session.commit()
            # Определение победителя
            highest_bid = Bid.query.filter_by(auction_id=auction.id).order_by(Bid.amount.desc()).first()
            if highest_bid:
                winner = highest_bid.bidder
                # Уведомление через Telegram бота
                asyncio.run(notify_user(winner.telegram_id, f'Вы выиграли аукцион "{auction.title}".'))
                asyncio.run(notify_user(auction.creator.telegram_id, f'Ваш аукцион "{auction.title}" завершён. Победитель: {winner.username}.'))
            else:
                asyncio.run(notify_user(auction.creator.telegram_id, f'Ваш аукцион "{auction.title}" завершён без ставок.'))
