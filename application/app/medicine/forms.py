# app/medicine/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, BooleanField, URLField, TextAreaField, SelectField, IntegerField, DateField
from wtforms.validators import DataRequired, Optional, URL, Length, ValidationError, NumberRange
from datetime import datetime
import os

def validate_suggestion(form, field):
    if form.has_suggestion.data and not field.data:
        raise ValidationError('Kérlek, válassz a rögzített javaslatok közül!')

def validate_decimal_places(form, field):
    if field.data is not None:
        str_val = str(field.data)
        if '.' in str_val:
            decimal_places = len(str_val.split('.')[1])
            if decimal_places > 2:
                raise ValidationError('Maximum 2 tizedesjegy engedélyezett.')
class MedicineForm(FlaskForm):
    name = StringField('Név', 
                      validators=[DataRequired(), 
                                Length(max=100, message='Maximum 100 karakter lehet')])
    
    default_dosage = FloatField('Alapértelmezett adagolás', 
                               validators=[DataRequired()])
    
    default_packaging = FloatField('Alapértelmezett kiszerelés', 
                                 validators=[DataRequired()])
    
    warning_threshold = IntegerField('Figyelmeztetési küszöb (nap)',
                                     validators=[
                                         DataRequired(),
                                         NumberRange(min=1, max=60,
                                                     message="A küszöbérték 1 és 60 nap közötti lehet")
                                     ],
                                     default=int(os.environ.get('STOCK_WARNING_THRESHOLD',5)))
    
    has_suggestion = BooleanField('Van javaslat')
    
    suggestion_id = SelectField('Javaslat', 
                              choices=[('', 'Válassz javaslatot...')],
                              validators=[Optional(), validate_suggestion],
                              coerce=str)
    
    link = URLField('Link', 
                   validators=[Optional(), 
                             URL(message='Érvénytelen URL formátum')])
    
    description = TextAreaField('Leírás', 
                              validators=[Optional(), 
                                        Length(max=2000, message='Maximum 2000 karakter lehet')])

class StockTransactionForm(FlaskForm):
    medicine = SelectField('Gyógyszer', validators=[DataRequired(message="Kérem, válasszon egy gyógyszert...")], coerce=str)  # medicine_id helyett medicine
    transaction_type = SelectField('Művelet típusa', 
                                 choices=[
                                     ('', 'Válasszon egy műveletet'),
                                     ('initial', 'Kezdő készlet'),
                                     ('refill', 'Kiváltás'),
                                     ('correction', 'Korrekció')
                                 ],
                                 validators=[DataRequired()])
    quantity = FloatField('Mennyiség', 
                          validators=[DataRequired(), 
                                    NumberRange(min=-60, max=60),
                                    validate_decimal_places])
    transaction_date = DateField('Dátum',
                               format='%Y-%m-%d',
                               validators=[DataRequired()])
    notes = TextAreaField('Megjegyzés', validators=[Optional()])