# app/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, ValidationError, 
    Regexp, Optional
)
from app.auth.models import User
from flask import current_app

class LoginForm(FlaskForm):
    """Bejelentkezési űrlap"""
    email = StringField('Email', validators=[
        DataRequired(message="Az email cím megadása kötelező"),
        Email(message="Érvénytelen email cím formátum")
    ])
    password = PasswordField('Jelszó', validators=[
        DataRequired(message="A jelszó megadása kötelező")
    ])
    submit = SubmitField('Bejelentkezés')

class RegistrationForm(FlaskForm):
    """Regisztrációs űrlap"""
    username = StringField('Felhasználónév', validators=[
        DataRequired(message="A felhasználónév megadása kötelező"),
        Length(min=3, max=20, message="A felhasználónévnek 3-20 karakter hosszúnak kell lennie"),
        Regexp(
            r'^[\w.@+-]+$',
            message="A felhasználónév csak betűket, számokat és @/./+/-/_ karaktereket tartalmazhat"
        )
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Az email cím megadása kötelező"),
        Email(message="Érvénytelen email cím formátum")
    ])
    password = PasswordField('Jelszó', validators=[
        DataRequired(message="A jelszó megadása kötelező"),
        Length(min=6, message="A jelszónak legalább 6 karakter hosszúnak kell lennie"),
        Regexp(
            r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!-_@#$%^&*(),.?":{}|<>]{6,}$',
            message="A jelszónak tartalmaznia kell legalább egy betűt és egy számot"
        )
    ])
    password2 = PasswordField('Jelszó megerősítése', validators=[
        DataRequired(message="A jelszó megerősítése kötelező"),
        EqualTo('password', message="A két jelszónak meg kell egyeznie")
    ])
    firstname = StringField('Keresztnév', validators=[
        DataRequired(message="A keresztnév megadása kötelező"),
        Length(min=1, max=150, message="A keresztnév 1-150 karakter hosszú lehet")
    ])
    lastname = StringField('Vezetéknév', validators=[
        DataRequired(message="A vezetéknév megadása kötelező"),
        Length(min=1, max=150, message="A vezetéknév 1-150 karakter hosszú lehet")
    ])
    submit = SubmitField('Regisztráció')

    def validate_email(self, email):
        """Email cím egyediségének ellenőrzése"""
        try:
            user = User.objects(email=email.data.lower().strip()).first()
            if user is not None:
                raise ValidationError('Ez az email cím már regisztrálva van.')
        except Exception as e:
            current_app.logger.error(f"Error validating email: {str(e)}")
            raise ValidationError('Hiba történt az email ellenőrzése során.')

    def validate_username(self, username):
        """Felhasználónév egyediségének ellenőrzése"""
        try:
            user = User.objects(username=username.data.strip()).first()
            if user is not None:
                raise ValidationError('Ez a felhasználónév már foglalt.')
        except Exception as e:
            current_app.logger.error(f"Error validating username: {str(e)}")
            raise ValidationError('Hiba történt a felhasználónév ellenőrzése során.')