# app/recommendations/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField
from wtforms.validators import InputRequired, DataRequired, Email, Length, Optional, ValidationError
from datetime import datetime

class RecommendationForm(FlaskForm):
    recommendation_name = StringField('Javaslat megnevezése', 
                                    validators=[DataRequired(), 
                                              Length(max=200, message='Maximum 200 karakter lehet')])
    
    doctor = StringField('Orvos neve', 
                        validators=[DataRequired(), 
                                  Length(max=100, message='Maximum 100 karakter lehet')])
    
    doctor_phone = StringField('Orvos telefonszáma', 
                             validators=[Optional(), 
                                       Length(max=20, message='Maximum 20 karakter lehet')])
    doctor_email = StringField('Orvos email címe',
                               validators=[Optional(),
                               Length(max=120)])
    
    recommendation_date = DateField('Javaslat dátuma', 
                                  validators=[DataRequired()],
                                  default=datetime.today)
    
    recommendation_enddate = DateField('Javaslat érvényességi ideje', 
                                     validators=[Optional()])
    
    notes = TextAreaField('Megjegyzések', 
                         validators=[Optional(), 
                                   Length(max=2000, message='Maximum 2000 karakter lehet')])

    
