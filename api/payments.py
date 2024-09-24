# api/payments.py
from . import api_bp
from flask import request, jsonify
from models import db, User, Payment

@api_bp.route('/update_balance', methods=['POST'])
def update_balance():
    data = request.get_json()
    telegram_id = data.get('telegram_id')
    amount = data.get('amount')
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if user:
        user.stars_balance += amount
        db.session.commit()
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'user not found'}), 404
