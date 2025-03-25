# app/medicine/models.py
from app import db
from datetime import datetime
from enum import Enum
from datetime import datetime, date, timedelta
import os

class Medicine(db.Document):
    name = db.StringField(required=True, max_length=100)
    default_dosage = db.FloatField(required=True)
    default_packaging = db.FloatField(required=True)
    warning_threshold = db.IntField(required=True, default=int(os.environ.get('STOCK_WARNING_THRESHOLD',5)))
    has_suggestion = db.BooleanField(default=False)
    suggestion = db.ReferenceField('Recommendation', required=False)
    link = db.URLField(required=False)
    description = db.StringField(max_length=2000)
    created_by = db.ReferenceField('User', required=True)
    created_at = db.DateTimeField(default=datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.utcnow)
    is_deleted = db.BooleanField(default=False)

    meta = {
        'collection': 'medicines',
        'indexes': [
            'name',
            'created_by',
            'created_at',
            'is_deleted'
        ],
        'ordering': ['-created_at']
    }

    def to_dict(self):
        suggestion_data = None
        if self.suggestion:
            self.suggestion.reload()
            suggestion_data = {
                'id': str(self.suggestion.id),
                'name': self.suggestion.recommendation_name,
                'enddate': self.suggestion.recommendation_enddate.strftime('%Y-%m-%d') if self.suggestion.recommendation_enddate else None
            }
        
        return {
            'id': str(self.id),
            'name': self.name,
            'default_dosage': self.default_dosage,
            'default_packaging': self.default_packaging,
            'warning_threshold': self.warning_threshold,
            'has_suggestion': self.has_suggestion,
            'suggestion': suggestion_data,
            'link': self.link,
            'description': self.description
        }

class TransactionType(Enum):
    INITIAL = 'initial'
    REFILL = 'refill'
    CORRECTION = 'correction'

class StockTransaction(db.Document):
    medicine = db.ReferenceField('Medicine', required=True)
    transaction_type = db.StringField(required=True, choices=[t.value for t in TransactionType])
    quantity = db.FloatField(required=True)
    transaction_date = db.DateTimeField(required=True)  # Ezt hagyjuk DateTimeField-nek
    notes = db.StringField(max_length=500)
    created_by = db.ReferenceField('User', required=True)
    created_at = db.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'stock_transactions',
        'indexes': [
            'medicine',
            'transaction_date',
            'created_by'
        ],
        'ordering': ['-transaction_date']
    }

class MedicineStock(db.Document):
    medicine = db.ReferenceField('Medicine', required=True, unique=True)
    base_quantity = db.FloatField(required=True, default=0)  # Átnevezett mező
    last_transaction_date = db.DateTimeField()
    created_by = db.ReferenceField('User', required=True)
    created_at = db.DateTimeField(default=datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.utcnow)
       
    meta = {
        'collection': 'medicine_stocks',
        'indexes': [
            'medicine',
            'created_by'
        ]
    }

    def get_quantity_at_date(self, target_date=None):
        
        if not self.last_transaction_date or not self.medicine.default_dosage:
            return self.base_quantity

        if target_date is None:
            target_date = datetime.now().date()
        elif isinstance(target_date, datetime):
            target_date = target_date.date()

        # #  Debug információk
        # print(f"Base quantity: {self.base_quantity}")
        # print(f"Last transaction date: {self.last_transaction_date}")
        # print(f"Target date: {target_date}")
        # print(f"Daily dosage: {self.medicine.default_dosage}")
        
        days_passed = (datetime.now().date() - self.last_transaction_date.date()).days
        
        # print(f"Days passed: {days_passed}") 
        
        daily_consumption = float(self.medicine.default_dosage)
        
        consumed_quantity = days_passed * daily_consumption
        # print(f"Consumed quantity: {consumed_quantity}")  # Debug információ
    
        actual_quantity = max(0, self.base_quantity - consumed_quantity)
    
        # print(f"Actual quantity: {actual_quantity}")  # Debug információ
    
        return actual_quantity

    def calculate_days_remaining(self):
        actual_quantity = self.get_quantity_at_date()
        if not self.medicine or not actual_quantity or not self.medicine.default_dosage:
            return 0
        return int(actual_quantity / self.medicine.default_dosage)

    def calculate_warning_date(self):
        days_remaining = self.calculate_days_remaining()
        if not days_remaining:
            return None
        return datetime.now().date() + timedelta(days=days_remaining)

    def can_refill(self):
        days_remaining = self.calculate_days_remaining()
        return days_remaining <= self.medicine.warning_threshold

    def to_dict(self):
        actual_quantity = self.get_quantity_at_date()
        days_remaining = self.calculate_days_remaining()
        warning_date = self.calculate_warning_date()

        return {
            'id': str(self.id),
            'medicine_id': str(self.medicine.id),
            'medicine_name': self.medicine.name,
            'current_quantity': actual_quantity,
            'base_quantity': self.base_quantity,
            'last_transaction_date': self.last_transaction_date.strftime('%Y-%m-%d %H:%M') if self.last_transaction_date else None,
            'warning_threshold': self.medicine.warning_threshold,
            'days_remaining': days_remaining,
            'warning_date': warning_date.strftime('%Y-%m-%d') if warning_date else None,
            'can_refill': self.can_refill(),
            'daily_dosage': self.medicine.default_dosage
        }