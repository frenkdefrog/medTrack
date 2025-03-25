# app/medicine/__init__.py
from flask import Blueprint

bp = Blueprint('medicine', __name__)

from app.medicine import routes