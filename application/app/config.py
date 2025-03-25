"""
Alkalmazás konfigurációs modul.
"""
import os
from dotenv import load_dotenv

# load_dotenv()
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))



class Config:
    """Alap konfigurációs osztály."""
    
    # Logging beállítás
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_TYPE = os.environ.get('LOG_TYPE', 'STDOUT').upper() #'FILE' vagy 'STDOUT'
    LOG_DIR = os.environ.get('LOG_DIR', 'logs')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', '10240'))
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', '5'))
    
    # Alap konfiguráció
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-this'

    # MongoDB beállítások
    MONGODB_SETTINGS = {
        'host': os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/medapp'),
        'connect': False,
        'maxPoolSize': 100,
        'minPoolSize': 5
    }

    # Biztonsági beállítások
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    PERMANENT_SESSION_LIFETIME = 3600
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Alkalmazás specifikus beállítások
    TEMPLATES_AUTO_RELOAD = True
    STOCK_WARNING_THRESHOLD = int(os.environ.get('STOCK_WARNING_THRESHOLD', '5'))

    # Email beállítások
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Task beállítások
    ENABLE_MEDICINE_CHECKER = os.environ.get('ENABLE_MEDICINE_CHECKER', 'false').lower() in ['true', '1', 'yes']
    MEDICINE_CHECK_INTERVAL = int(os.environ.get('MEDICINE_CHECK_INTERVAL', '3'))
