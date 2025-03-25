# app/auth/models.py
from datetime import datetime
from typing import Optional, Dict, Any
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

class User(UserMixin, db.Document):
    """Felhasználói modell"""
    email: str = db.StringField(required=True, unique=True)
    username: str = db.StringField(required=True, unique=True)
    firstname: str = db.StringField(required=True)
    lastname: str = db.StringField(required=True)
    password_hash: str = db.StringField(required=True)
    is_active: bool = db.BooleanField(default=True)
    created_at: datetime = db.DateTimeField(default=datetime.utcnow)
    last_login: datetime = db.DateTimeField()
    login_attempts: int = db.IntField(default=0)
    
    email_template: str = db.StringField(default="""Tisztelt Doktornő/Doktor Úr!
    
Az alábbi gyógyszereket kérem szépen felírni nekem, hogy ha van rá lehetőség:
{medicines}

Köszönettel:
{fullname}""")

    meta = {
        'collection': 'users',
        'indexes': [
            {'fields': ['email'], 'unique': True, 'sparse': True},
            {'fields': ['username'], 'unique': True, 'sparse': True},
            {'fields': ['created_at']},
            {'fields': ['last_login']}
        ],
        'ordering': ['-created_at']
    }

    def set_password(self, password: str) -> None:
        """Jelszó beállítása hash-elt formában"""
        if len(password) < 6:
            raise ValueError("A jelszónak legalább 6 karakter hosszúnak kell lennie")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Jelszó ellenőrzése"""
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self) -> str:
        """Teljes név visszaadása"""
        return f"{self.firstname} {self.lastname}"

    def update_login_timestamp(self) -> None:
        """Utolsó bejelentkezés időpontjának frissítése"""
        self.last_login = datetime.utcnow()
        self.login_attempts = 0
        self.save()

    def increment_login_attempts(self) -> None:
        """Sikertelen bejelentkezési kísérletek számának növelése"""
        self.login_attempts += 1
        self.save()

    def is_locked_out(self) -> bool:
        """Ellenőrzi, hogy a felhasználó ki van-e zárva"""
        max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
        return self.login_attempts >= max_attempts

    def to_dict(self) -> Dict[str, Any]:
        """Felhasználói adatok dictionary formátumban"""
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self) -> str:
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    """Felhasználó betöltése ID alapján"""
    try:
        return User.objects(id=user_id).first()
    except Exception as e:
        current_app.logger.error(f"Error loading user {user_id}: {str(e)}")
        return None