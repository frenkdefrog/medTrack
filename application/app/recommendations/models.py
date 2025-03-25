# app/recommendations/models.py
from app import db
from datetime import datetime

class Recommendation(db.Document):
    recommendation_name = db.StringField(required=True, max_length=200)
    doctor = db.StringField(required=True, max_length=100)
    doctor_phone = db.StringField(max_length=20)
    doctor_email = db.StringField(required=False)
    recommendation_date = db.DateTimeField(required=True)
    recommendation_enddate = db.DateTimeField()
    notes = db.StringField(max_length=2000)
    created_by = db.ReferenceField('User', required=True)
    created_at = db.DateTimeField(default=datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.utcnow)
    is_deleted = db.BooleanField(default=False)

    meta = {
        'collection': 'recommendations',
        'indexes': [
            'recommendation_name',
            'doctor',
            'recommendation_date',
            'created_by',
            'created_at',
            'is_deleted'
        ],
        'ordering': ['-created_at']
    }

    def to_dict(self):
        return {
            'id': str(self.id),
            'recommendation_name': self.recommendation_name,
            'doctor': self.doctor,
            'doctor_phone': self.doctor_phone,
            'doctor_email': self.doctor_email,
            'recommendation_date': self.recommendation_date.strftime('%Y-%m-%d') if self.recommendation_date else None,
            'recommendation_enddate': self.recommendation_enddate.strftime('%Y-%m-%d') if self.recommendation_enddate else None,
            'notes': self.notes
        }