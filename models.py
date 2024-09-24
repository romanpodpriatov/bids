# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Column, Integer, String

db = SQLAlchemy()

# Модель пользователя
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String(120))
    stars_balance = db.Column(db.Integer, default=0)
    subscription_status = db.Column(db.String(10), default='inactive')
    subscription_end = db.Column(db.DateTime)
    photo_url = Column(String)
    is_admin = db.Column(db.Boolean, default=False)
    # Связи
    auctions = db.relationship('Auction', backref='creator', lazy=True)
    bids = db.relationship('Bid', backref='bidder', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)
    watchlist_items = db.relationship('Watchlist', backref='user', lazy=True)
    user_achievements = db.relationship('UserAchievement', backref='user', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)

# Модель аукциона
class Auction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(128))
    starting_price = db.Column(db.Integer, nullable=False)
    current_price = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    auction_type = db.Column(db.String(20), default='english')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Связи
    bids = db.relationship('Bid', backref='auction', lazy=True)
    watchlist_items = db.relationship('Watchlist', backref='auction', lazy=True)
    ratings = db.relationship('Rating', backref='auction', lazy=True)

# Модель ставки
class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auction.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    max_bid = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Модель платежа
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    telegram_payment_id = db.Column(db.String(128), unique=True)
    status = db.Column(db.String(10), default='pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Модель списка наблюдения
class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    auction_id = db.Column(db.Integer, db.ForeignKey('auction.id'), nullable=False)

# Модель достижения
class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(128))
    # Связи
    user_achievements = db.relationship('UserAchievement', backref='achievement', lazy=True)


# Модель пользовательского достижения
class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Модель рейтинга
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auction.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
