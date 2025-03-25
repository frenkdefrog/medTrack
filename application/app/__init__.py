"""
Flask alkalmazás inicializáló modul.
"""
import os
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, redirect, url_for, request, jsonify, session, render_template
from flask.json import JSONEncoder
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect, CSRFError
from bson import ObjectId
from app.config import Config

class CustomJSONEncoder(JSONEncoder):
    """Egyedi JSON encoder osztály MongoDB ObjectId szerializálásához."""
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

# Globális objektumok inicializálása
db = MongoEngine()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Kérjük, jelentkezzen be a folytatáshoz!'

def configure_logging(app):
    """
    Logging konfiguráció beállítása.

    Args:
        app: Flask alkalmazás példány
    """
    app.logger.handlers.clear()

    log_level = getattr(logging, app.config['LOG_LEVEL'], logging.INFO)
    app.logger.setLevel(log_level)

    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )

    if app.config['LOG_TYPE'] == 'STDOUT':
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        app.logger.addHandler(console_handler)
        app.logger.info("Logging to STDOUT")
    
    elif app.config['LOG_TYPE'] == 'FILE':
        # Log könyvtár létrehozása ha szükséges
        log_dir = app.config['LOG_DIR']
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # File handler
        log_file_path = os.path.join(log_dir, app.config['LOG_FILE'])
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=app.config['LOG_MAX_BYTES'],
            backupCount=app.config['LOG_BACKUP_COUNT']
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
        app.logger.info(f"Logging to file: {log_file_path}")
    
    else:
        raise ValueError(f"Invalid LOG_TYPE: {app.config['LOG_TYPE']}")

def init_mongodb(app):
    """MongoDB inicializálása"""
    try:
        db.init_app(app)
        with app.app_context():
            db.connection.server_info()
        app.logger.info("MongoDB connection successful")
    except Exception as e:
        app.logger.error(f"MongoDB connection failed: {str(e)}", exc_info=True)
        raise

def configure_security_headers(app):
    """Biztonsági headerek konfigurálása"""
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

def configure_error_handlers(app):
    """Hibakezelők konfigurálása"""
    @app.errorhandler(404)
    def not_found_error(_):
        app.logger.error(f"Page not found: {request.url}")
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {str(error)}", exc_info=True)
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        app.logger.error(f"CSRF Error: {e.description}")
        return jsonify({'error': e.description}), 400

def configure_request_logging(app):
    """Kérés logging konfigurálása"""
    @app.before_request
    def log_request_info():
        app.logger.info(f"Request: {request.method} {request.url}")
        if app.config['LOG_LEVEL'] == 'DEBUG':
            app.logger.debug(f"Headers: {dict(request.headers)}")
            app.logger.debug(f"Body: {request.get_data()}")

    @app.after_request
    def log_response(response):
        app.logger.info(f"Response: {response.status}")
        return response

def register_blueprints(app):
    """Blueprint-ek regisztrálása"""
    from app.auth import bp as auth_bp
    from app.medicine import bp as medicine_bp
    from app.recommendations import bp as recommendations_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(medicine_bp, url_prefix='/medicine')
    app.register_blueprint(recommendations_bp, url_prefix='/recoms')

def create_app(config_class=Config):
    """Flask alkalmazás létrehozása"""
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    app.json_encoder = CustomJSONEncoder

    configure_logging(app)
    init_mongodb(app)

    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    configure_security_headers(app)
    configure_error_handlers(app)
    configure_request_logging(app)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    register_blueprints(app)

    if app.config.get('ENABLE_MEDICINE_CHECKER', False):
        try:
            from app.tasks.medicine_checker import init_scheduler
            init_scheduler(app)
            app.logger.info("Medicine checker sheduler initialized")
        except Exception as e:
            app.logger.error(f"Failed to initialize medicine checker: {str(e)}")

    app.logger.info("Application initialized successfully")
    return app