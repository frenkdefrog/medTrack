# app/medicine/helpers.py
from datetime import datetime, timedelta

def calculate_stock_status(current_quantity, daily_dosage, warning_threshold):
    """Calculate stock status and return relevant information"""
    if not current_quantity or not daily_dosage:
        return {
            'days_remaining': 0,
            'warning_date': None,
            'status': 'error',
            'message': 'Hiányzó adatok'
        }

    days_remaining = int(current_quantity / daily_dosage)
    warning_date = datetime.now().date() + timedelta(days=days_remaining)
    
    status = 'ok' if days_remaining > warning_threshold else 'warning'
    
    return {
        'days_remaining': days_remaining,
        'warning_date': warning_date,
        'status': status,
        'message': f'Még {days_remaining} napra elegendő'
    }

def validate_transaction(transaction_type, quantity, current_stock=None):
    """Validate transaction based on type and quantity"""
    errors = []
    
    if transaction_type == 'initial' and current_stock:
        errors.append('Már van kezdő készlet rögzítve')
    
    if transaction_type == 'correction' and quantity > 0:
        errors.append('Korrekció esetén csak negatív érték adható meg')
    
    if transaction_type in ['initial', 'refill'] and quantity <= 0:
        errors.append('Kezdő készlet és kiváltás esetén pozitív értéket kell megadni')
    
    return errors