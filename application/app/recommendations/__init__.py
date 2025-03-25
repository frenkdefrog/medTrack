# app/recommendations/__init__.py
from flask import Blueprint

bp = Blueprint('recommendations', __name__)

from app.recommendations import routes