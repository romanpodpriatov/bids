# api/__init__.py
from flask import Blueprint

api_bp = Blueprint('api', __name__)

from . import payments, users