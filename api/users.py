# api/users.py
from . import api_bp
from flask import request, jsonify
from models import User

@api_bp.route('/get_user/<telegram_id>', methods=['GET'])
def get_user(telegram_id):
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if user:
        return jsonify({
            'id': user.id,
            'telegram_id': user.telegram_id,
            'username': user.username,
            'stars_balance': user.stars_balance
        }), 200
    else:
        return jsonify({'status': 'user not found'}), 404
