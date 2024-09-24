# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, FileField, SubmitField, SelectField, EmailField
from wtforms.validators import DataRequired, NumberRange, Length, Email
from datetime import datetime, timedelta

class PurchaseStarsForm(FlaskForm):
    amount = IntegerField('Количество звёзд', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Купить')

class AuctionForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Описание', validators=[DataRequired()])
    starting_price = IntegerField('Стартовая цена', validators=[DataRequired(), NumberRange(min=1)])
    duration = IntegerField('Длительность (в часах)', validators=[DataRequired(), NumberRange(min=1)])
    auction_type = SelectField('Тип аукциона', choices=[
        ('english', 'Английский'),
        ('dutch', 'Голландский'),
        ('sealed', 'Закрытые ставки'),
        ('perpetual', 'Вечный')
    ])
    image = FileField('Изображение')
    submit = SubmitField('Создать аукцион')

class BidForm(FlaskForm):
    amount = IntegerField('Сумма ставки', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Сделать ставку')

class LoginForm(FlaskForm):
    telegram_id = StringField('Ваш Telegram ID', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    telegram_id = StringField('Ваш Telegram ID', validators=[DataRequired()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class ProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = EmailField('Email', validators=[Email()])
    submit = SubmitField('Сохранить изменения')

class SubscriptionForm(FlaskForm):
    submit = SubmitField('Оформить подписку за 100 XTR')

class SupportForm(FlaskForm):
    subject = StringField('Тема', validators=[DataRequired()])
    message = TextAreaField('Сообщение', validators=[DataRequired()])
    submit = SubmitField('Отправить')

