# app/utils/decorators.py
from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Kérjük jelentkezzen be a folytatáshoz!', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function