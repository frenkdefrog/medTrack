# app/auth/routes.py
from flask import (
    render_template, redirect, url_for, flash, request, 
    current_app, session
)
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import bp
from app.auth.models import User
from app.auth.forms import LoginForm, RegistrationForm
from werkzeug.urls import url_parse
from datetime import datetime
from functools import wraps
import time

def limit_login_attempts(f):
    """Rate limiting dekorátor"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # IP alapú rate limiting
        ip = request.remote_addr
        current_time = time.time()
        
        # Rate limiting adatok lekérése a session-ből
        rate_limit_data = session.get('rate_limit', {})
        ip_data = rate_limit_data.get(ip, {'count': 0, 'timestamp': current_time})
        
        # Időablak ellenőrzése (15 perc)
        if current_time - ip_data['timestamp'] > 900:
            ip_data = {'count': 0, 'timestamp': current_time}
        
        # Túl sok próbálkozás ellenőrzése
        if ip_data['count'] >= 5:
            current_app.logger.warning(f"Rate limit exceeded for IP: {ip}")
            flash('Túl sok sikertelen próbálkozás. Kérjük, próbálja újra később.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Számláló növelése
        ip_data['count'] += 1
        rate_limit_data[ip] = ip_data
        session['rate_limit'] = rate_limit_data
        
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
@limit_login_attempts
def login():
    """Bejelentkezési végpont"""
    try:
        # Ha már be van jelentkezve
        if current_user.is_authenticated:
            return redirect(url_for('medicine.index'))
        
        # Első felhasználó ellenőrzése
        if User.objects.count() == 0:
            if request.endpoint != 'auth.register':
                flash('Az első felhasználó regisztrációja szükséges a rendszer használatához.', 'info')
                return redirect(url_for('auth.register'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.objects(email=form.email.data.lower().strip()).first()
            
            # Felhasználó ellenőrzése
            if user is None:
                current_app.logger.warning(f"Login attempt with non-existent email: {form.email.data}")
                flash('Érvénytelen email vagy jelszó', 'danger')
                return redirect(url_for('auth.login'))
            
            # Kizárás ellenőrzése
            if user.is_locked_out():
                flash('A fiók ideiglenesen zárolva van. Kérjük, próbálja később.', 'danger')
                return redirect(url_for('auth.login'))
            
            # Jelszó ellenőrzése
            if not user.check_password(form.password.data):
                user.increment_login_attempts()
                current_app.logger.warning(f"Failed login attempt for user: {user.username}")
                flash('Érvénytelen email vagy jelszó', 'danger')
                return redirect(url_for('auth.login'))
            
            # Sikeres bejelentkezés
            login_user(user)
            user.update_login_timestamp()
            current_app.logger.info(f"Successful login for user: {user.username}")
            
            # Következő oldal meghatározása
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('medicine.stock_index')
            
            return redirect(next_page)
        
        return render_template('auth/login.html', title='Bejelentkezés', form=form)
    
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}", exc_info=True)
        flash('Váratlan hiba történt. Kérjük, próbálja újra később.', 'danger')
        return redirect(url_for('auth.login'))

@bp.route('/logout')
def logout():
    """Kijelentkezési végpont"""
    try:
        if current_user.is_authenticated:
            username = current_user.username
            logout_user()
            current_app.logger.info(f"User logged out: {username}")
            flash('Sikeresen kijelentkezett.', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}", exc_info=True)
        flash('Hiba történt a kijelentkezés során.', 'danger')
        return redirect(url_for('medicine.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Regisztrációs végpont"""
    try:
        # Bejelentkezett felhasználó regisztrációja
        if current_user.is_authenticated:
            form = RegistrationForm()
            if form.validate_on_submit():
                user = User(
                    username=form.username.data.strip(),
                    email=form.email.data.lower().strip(),
                    firstname=form.firstname.data.strip(),
                    lastname=form.lastname.data.strip()
                )
                user.set_password(form.password.data)
                user.save()
                
                current_app.logger.info(
                    f"New user registered by {current_user.username}: {user.username}"
                )
                flash('Új felhasználó sikeresen hozzáadva!', 'success')
                return redirect(url_for('auth.register'))
            
            return render_template('auth/register.html', 
                                 title='Új felhasználó hozzáadása',
                                 form=form,
                                 is_first_user=False)
        
        # Ha nincs bejelentkezve, de már van felhasználó
        if User.objects.count() > 0:
            flash('Új felhasználó regisztrációjához bejelentkezés szükséges!', 'warning')
            return redirect(url_for('auth.login'))
        
        # Első felhasználó regisztrációja
        form = RegistrationForm()
        if form.validate_on_submit():
            try:
                user = User(
                    username=form.username.data.strip(),
                    email=form.email.data.lower().strip(),
                    firstname=form.firstname.data.strip(),
                    lastname=form.lastname.data.strip(),
                    created_at=datetime.utcnow()
                )
                user.set_password(form.password.data)
                user.save()
                
                current_app.logger.info(f"First user registered: {user.username}")
                flash('Sikeres regisztráció! Most már bejelentkezhet.', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                current_app.logger.error(f"Error creating first user: {str(e)}", exc_info=True)
                flash('Hiba történt a regisztráció során. Kérjük, próbálja újra.', 'danger')
                return redirect(url_for('auth.register'))
        
        return render_template('auth/register.html', 
                             title='Első felhasználó regisztrációja',
                             form=form,
                             is_first_user=True)
                             
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}", exc_info=True)
        flash('Váratlan hiba történt a regisztráció során.', 'danger')
        return redirect(url_for('auth.register'))

@bp.after_request
def after_request(response):
    """Minden kérés után lefutó függvény"""
    # Security headers hozzáadása
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response