# app/auth/__init__.py
from flask import Blueprint

bp = Blueprint('auth', __name__)

# Blueprint regisztrálása után importáljuk a route-okat
from app.auth import routes

# Verzió információ
__version__ = '1.0.0'