import threading
import asyncio
import logging
import os
import time
import uuid
import base64
import json
import hashlib
import hmac
from dotenv import load_dotenv
load_dotenv()

from forms import (
    AuctionForm,
    BidForm,
    LoginForm,
    ProfileForm,
    SupportForm
)
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    session,
    jsonify
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel, gettext as _, get_locale

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    filters
)
from telegram import Update, LabeledPrice

from models import (
    db,
    User,
    Auction,
    Bid,
    Watchlist,
    Achievement,
    UserAchievement,
    Rating
)
from utils import (
    generate_uuid,
    save_image,
    allowed_file,
    calculate_end_time
)
from scheduler import scheduler, finish_auction
from api import api_bp

# Инициализация приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 'sqlite:///auction.db'
)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['BABEL_DEFAULT_LOCALE'] = 'ru'
app.config['BABEL_SUPPORTED_LOCALES'] = ['ru', 'en']

# Инициализация расширений
db.init_app(app)
migrate = Migrate(app, db)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Инициализация Babel
def get_user_locale():
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])

babel = Babel(app, locale_selector=get_user_locale)

@app.context_processor
def inject_get_locale():
    return dict(get_locale=get_locale)

# Менеджер загрузки пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Планировщик задач
scheduler.init_app(app)
scheduler.start()

# Регистрация Blueprint для API
app.register_blueprint(api_bp, url_prefix='/api')

# Инициализация Telegram бота
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN')  # Удалено, т.к. покупка звёзд отключена

# Проверка наличия необходимых токенов
if not TELEGRAM_BOT_TOKEN:
    logging.error("TELEGRAM_BOT_TOKEN не установлен. Проверьте переменные окружения.")
    exit(1)

# Создание приложения Telegram бота
application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

# Обработчики Telegram бота

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Все функции вашего бота бесплатны.")

async def buy_stars_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Функция отключена, так как покупка звёзд недоступна
    await update.message.reply_text("Покупка звёзд временно недоступна.")

# Обработчик ошибок Telegram бота
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Произошла ошибка: {context.error}")

# Загрузка обработчиков в приложение бота
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('buy_stars', buy_stars_command))
application.add_error_handler(error_handler)

def check_telegram_auth(data):
    auth_date = int(data.get('auth_date', 0))
    # Проверяем, что время авторизации не слишком старое (например, не более 1 дня)
    if time.time() - auth_date > 86400:
        return False

    check_hash = data.pop('hash')
    data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(data.items())])
    secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
    hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    return hmac.compare_digest(hmac_hash, check_hash)

# Маршруты веб-приложения

@app.route('/')
def index():
    auctions = Auction.query.filter_by(is_active=True).all()
    return render_template('index.html', auctions=auctions)

@app.route('/telegram_auth')
def telegram_auth():
    data = request.args.to_dict()
    if check_telegram_auth(data):
        telegram_id = data.get('id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        photo_url = data.get('photo_url')  # URL аватара пользователя

        # Ищем пользователя в базе данных
        user = User.query.filter_by(telegram_id=telegram_id).first()

        if user:
            # Обновляем данные пользователя, если они изменились
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.photo_url = photo_url
            # Назначаем администратором, если это нужный пользователь
            if telegram_id == '223800299' and not user.is_admin:
                user.is_admin = True
                logging.info(f"Пользователь {user.username} назначен администратором.")
            db.session.commit()
        else:
            # Если пользователя нет, создаём нового
            user = User(
                telegram_id=telegram_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                photo_url=photo_url,
                is_admin=(telegram_id == '223800299')  # Назначаем админом, если telegram_id совпадает
            )
            db.session.add(user)
            db.session.commit()
            logging.info(f"Создан новый пользователь: {user.username} с admin статусом: {user.is_admin}")

        # Логиним пользователя
        login_user(user)
        flash('Вы успешно вошли в систему через Telegram.', 'success')
        return redirect(url_for('profile'))
    else:
        flash('Ошибка аутентификации через Telegram.', 'danger')
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        telegram_id = form.telegram_id.data
        user = User.query.filter_by(telegram_id=telegram_id).first()
        if user:
            # Назначаем администратором, если это нужный пользователь
            if telegram_id == '223800299' and not user.is_admin:
                user.is_admin = True
                logging.info(f"Пользователь {user.username} назначен администратором.")
            login_user(user)
            flash(_('Вы успешно вошли в систему.'), 'success')
            return redirect(url_for('index'))
        else:
            flash(_('Пользователь не найден.'), 'danger')
    return render_template('login.html', form=form)

# Удален маршрут /register
# Удалены связанные формы и модели

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('Вы вышли из системы.'), 'info')
    return redirect(url_for('index'))

@app.route('/new_auction', methods=['GET', 'POST'])
@login_required
def new_auction():
    form = AuctionForm()
    if form.validate_on_submit():
        image_filename = None
        if 'image' in request.files and allowed_file(request.files['image'].filename):
            image_filename = save_image(request.files['image'], app.config['UPLOAD_FOLDER'])
        auction = Auction(
            uuid=generate_uuid(),
            title=form.title.data,
            description=form.description.data,
            image_filename=image_filename,
            starting_price=form.starting_price.data,
            current_price=form.starting_price.data,
            end_time=calculate_end_time(form.duration.data),
            is_active=True,
            user_id=current_user.id,
            auction_type=form.auction_type.data
        )
        db.session.add(auction)
        db.session.commit()
        # Планирование задачи завершения аукциона
        scheduler.add_job(
            func=finish_auction,
            trigger='date',
            run_date=auction.end_time,
            args=[auction.id],
            id=f'auction_{auction.id}'
        )
        flash(_('Аукцион успешно создан.'), 'success')
        return redirect(url_for('my_auctions'))
    return render_template('new_auction.html', form=form)

@app.route('/my_auctions')
@login_required
def my_auctions():
    auctions = Auction.query.filter_by(user_id=current_user.id).all()
    return render_template('my_auctions.html', auctions=auctions)

@app.route('/auction/<uuid>', methods=['GET', 'POST'])
def auction_detail(uuid):
    auction = Auction.query.filter_by(uuid=uuid).first_or_404()
    form = BidForm()
    if form.validate_on_submit():
        return place_bid(uuid)
    return render_template('auction.html', auction=auction, form=form)

@login_required
def place_bid(uuid):
    auction = Auction.query.filter_by(uuid=uuid).first_or_404()
    form = BidForm()
    if form.validate_on_submit():
        bid_amount = form.amount.data
        if bid_amount <= auction.current_price:
            flash(_('Ставка должна быть больше текущей цены.'), 'danger')
        else:
            # Удалено уменьшение баланса звёзд:
            # current_user.stars_balance -= bid_amount
            bid = Bid(
                auction_id=auction.id,
                user_id=current_user.id,
                amount=bid_amount
            )
            auction.current_price = bid_amount
            db.session.add(bid)
            db.session.commit()
            flash(_('Ставка успешно сделана.'), 'success')
            # Уведомление через Telegram бота
            asyncio.run(notify_user_async(auction.creator.telegram_id, _('Новая ставка на ваш аукцион "%(title)s".', title=auction.title)))
            return redirect(url_for('auction_detail', uuid=uuid))
    return render_template('auction.html', auction=auction, form=form)

@app.route('/add_to_watchlist/<uuid>')
@login_required
def add_to_watchlist(uuid):
    auction = Auction.query.filter_by(uuid=uuid).first_or_404()
    existing = Watchlist.query.filter_by(user_id=current_user.id, auction_id=auction.id).first()
    if not existing:
        watchlist_item = Watchlist(user_id=current_user.id, auction_id=auction.id)
        db.session.add(watchlist_item)
        db.session.commit()
        flash(_('Аукцион добавлен в список наблюдения.'), 'success')
    else:
        flash(_('Аукцион уже в вашем списке наблюдения.'), 'info')
    return redirect(url_for('auction_detail', uuid=uuid))

@app.route('/watchlist')
@login_required
def watchlist():
    items = Watchlist.query.filter_by(user_id=current_user.id).all()
    return render_template('watchlist.html', items=items)

@app.route('/achievements')
@login_required
def achievements():
    achievements = Achievement.query.all()
    user_achievements_records = UserAchievement.query.filter_by(user_id=current_user.id).all()
    user_achievements = {ua.achievement_id: ua for ua in user_achievements_records}
    return render_template('achievements.html', achievements=achievements, user_achievements=user_achievements)

@app.route('/support', methods=['GET', 'POST'])
def support():
    form = SupportForm()
    if form.validate_on_submit():
        # Логика отправки сообщения в службу поддержки
        flash(_('Ваш запрос отправлен в службу поддержки.'), 'success')
        return redirect(url_for('index'))
    return render_template('support.html', form=form)

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash(_('Доступ запрещён.'), 'danger')
        return redirect(url_for('index'))
    total_users = User.query.count()
    active_auctions = Auction.query.filter_by(is_active=True).count()
    completed_auctions = Auction.query.filter_by(is_active=False).count()
    total_payments = db.session.query(db.func.sum(Payment.amount)).scalar() or 0  # Удалите, если модель Payment больше не используется
    users = User.query.all()
    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        active_auctions=active_auctions,
        completed_auctions=completed_auctions,
        total_payments=total_payments,
        users=users
    )

# Функция уведомления через Telegram бота
async def notify_user_async(telegram_id, message):
    try:
        await application.bot.send_message(chat_id=telegram_id, text=message)
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение пользователю {telegram_id}: {e}")

def notify_user(telegram_id, message):
    asyncio.run(notify_user_async(telegram_id, message))

# Функция для запуска Flask-приложения
def run_flask_app():
    # Отключаем перезагрузчик и отладчик
    app.run(debug=False, use_reloader=False)

if __name__ == '__main__':
    # Запуск Flask-приложения в отдельном потоке
    flask_thread = threading.Thread(target=run_flask_app, name='FlaskThread')
    flask_thread.start()

    # Запуск Telegram-бота в главном потоке
    asyncio.run(application.run_polling())
