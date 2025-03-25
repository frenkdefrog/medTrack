# app/medicine/routes.py
from flask import render_template, jsonify, request, current_app
from flask_login import current_user, login_required
from app.medicine import bp
from app.medicine.models import Medicine
from app.medicine.forms import MedicineForm, StockTransactionForm
from app.medicine.models import StockTransaction, MedicineStock, TransactionType
from app.recommendations.models import Recommendation
from datetime import datetime
from bson import ObjectId
import json

@bp.route('/')
@login_required
def index():
    # Csak a nem törölt elemeket jelenítjük meg
    medicines = Medicine.objects(
        created_by=current_user.id,
        is_deleted=False
    ).order_by('-created_at')
    
    for medicine in medicines:
        if medicine.suggestion:
            medicine.suggestion.reload()

    return render_template('medicine/index.html', 
                         title='Gyógyszerek',
                         medicines=medicines)

@bp.route('/modal/<modal_type>')
@login_required
def get_modal(modal_type):
    try:
        # Get available recommendations
        recommendations = Recommendation.objects(
            created_by=current_user.id,
            is_deleted=False
        ).order_by('-created_at')
        
        if modal_type == 'add':
            form = MedicineForm()
            # Populate suggestions dropdown
            form.suggestion_id.choices = [('', 'Válassz javaslatot...')] + [
                (str(r.id), r.recommendation_name) for r in recommendations
            ]
            return render_template('medicine/modals/medicine.html', 
                                 form=form,
                                 has_recommendations=bool(recommendations))
        
        elif modal_type == 'edit':
            medicine_id = request.args.get('id')
            medicine = Medicine.objects(
                id=medicine_id, 
                created_by=current_user.id,
                is_deleted=False
            ).first_or_404()
            
            form = MedicineForm(obj=medicine)
            # Populate suggestions dropdown
            form.suggestion_id.choices = [('', 'Válassz javaslatot...')] + [
                (str(r.id), r.recommendation_name) for r in recommendations
            ]
            
            # Ha van kapcsolódó javaslat, állítsuk be a form mezőjét
            if medicine.suggestion:
                form.suggestion_id.data = str(medicine.suggestion.id)
            
            return render_template('medicine/modals/medicine.html', 
                                form=form,
                                medicine=medicine,
                                has_recommendations=bool(recommendations))
        
        return jsonify({'error': 'Invalid modal type'}), 400
    except Exception as e:
        current_app.logger.error(f"Error in get_modal: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/medicines', methods=['POST'])
@login_required
def add_medicine():
    try:
        form = MedicineForm()
        # Populate choices again before validation
        recommendations = Recommendation.objects(
            created_by=current_user.id,
            is_deleted=False
        ).order_by('-created_at')
        form.suggestion_id.choices = [('', 'Válassz javaslatot...')] + [
            (str(r.id), r.recommendation_name) for r in recommendations
        ]
        
        if form.validate_on_submit():
            data = {
                "name": form.name.data,
                "default_dosage": form.default_dosage.data,
                "default_packaging": form.default_packaging.data,
                "warning_threshold": form.warning_threshold.data,
                "has_suggestion": form.has_suggestion.data,
                "description": form.description.data,
                "created_by": current_user.id
            }
            
            if form.link.data:
                data['link'] = form.link.data

            # Konvertáljuk az ID-t és keressük meg a javaslatot
            if form.has_suggestion.data and form.suggestion_id.data:
                suggestion = Recommendation.objects.get(id=ObjectId(form.suggestion_id.data))
                data['suggestion'] = suggestion
            else:
                data['has_suggestion'] = False
                data['suggestion'] = None

            medicine = Medicine(**data)
            medicine.save()
            return jsonify({'message': 'Medicine added successfully'})
        return jsonify({'error': form.errors}), 400
    except Exception as e:
        current_app.logger.error(f"Error in add_medicine: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/medicines/<medicine_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def medicine_api(medicine_id):
    try:
        medicine = Medicine.objects(
            id=medicine_id, 
            created_by=current_user.id,
            is_deleted=False
        ).first_or_404()
        
        if request.method == 'GET':
            return jsonify(medicine.to_dict())
        
        elif request.method == 'PUT':
            form = MedicineForm()
            # Populate choices before validation
            recommendations = Recommendation.objects(
                created_by=current_user.id,
                is_deleted=False
            ).order_by('-created_at')
            form.suggestion_id.choices = [('', 'Válassz javaslatot...')] + [
                (str(r.id), r.recommendation_name) for r in recommendations
            ]
            
            if form.validate_on_submit():
                update_data = {
                    "name": form.name.data,
                    "default_dosage": form.default_dosage.data,
                    "default_packaging": form.default_packaging.data,
                    "warning_threshold": form.warning_threshold.data,
                    "has_suggestion": form.has_suggestion.data,
                    "description": form.description.data,
                    "updated_at": datetime.utcnow()
                }
                
                if form.link.data:
                    update_data['link'] = form.link.data
                else:
                    update_data['link'] = None

                # Konvertáljuk az ID-t és keressük meg a javaslatot
                if form.has_suggestion.data and form.suggestion_id.data:
                    suggestion = Recommendation.objects.get(id=ObjectId(form.suggestion_id.data))
                    update_data['suggestion'] = suggestion
                else:
                    update_data['has_suggestion'] = False
                    update_data['suggestion'] = None

                medicine.update(**update_data)
                return jsonify({'message': 'Medicine updated successfully'})
            return jsonify({'error': form.errors}), 400
        
        elif request.method == 'DELETE':
            # Soft delete - csak az is_deleted flag átállítása
            medicine.update(
                is_deleted=True,
                updated_at=datetime.utcnow()
            )
            return jsonify({'message': 'Medicine deleted successfully'})
            
    except Exception as e:
        current_app.logger.error(f"Error in medicine_api: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/stock')
@login_required
def stock_index():
    stocks = MedicineStock.objects(created_by=current_user.id)
    stocks_data = [stock.to_dict() for stock in stocks]

    firstname = getattr(current_user, 'firstname', '')
    lastname = getattr(current_user, 'lastname','')
    user_fullname = f"{lastname} {firstname}".strip() or "Felhasználó"
    return render_template('medicine/stock/index.html', 
                         title='Gyógyszerkészlet',
                         stocks=stocks_data,
                         user_fullname = user_fullname,
                         user_email_template=current_user.email_template) #A user nevének átadása

@bp.route('/stock/modal/<modal_type>')
@login_required
def stock_modal(modal_type):
    try:
        if modal_type == 'transaction':
            form = StockTransactionForm()
            medicines = Medicine.objects(
                created_by=current_user.id,
                is_deleted=False
            )

            form.medicine.choices =[('', 'Válasszon egy gyógyszert...')]+[(str(m.id), m.name) for m in medicines]
            
            # Készítsünk egy egyszerű dictionary-t a gyógyszerekről
            medicines_data = {}
            for m in medicines:
                medicines_data[str(m.id)] = {
                    'name': m.name,
                    'default_packaging': float(m.default_packaging)
                }
            
            print("Server-side medicines_data:", medicines_data)  # Debug print
            
            return render_template(
                'medicine/stock/modals/transaction.html',
                form=form,
                medicines_data=medicines_data  # Directly pass the dictionary
            )
    except Exception as e:
        current_app.logger.error(f"Error in stock_modal: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/stock/transaction', methods=['POST'])
@login_required
def add_stock_transaction():
    try:
        form = StockTransactionForm()
        medicines = Medicine.objects(
            created_by=current_user.id,
            is_deleted=False
        )
        form.medicine.choices = [(str(m.id), m.name) for m in medicines]
        
        if form.validate_on_submit():
            medicine = Medicine.objects.get(id=form.medicine.data)
            
            # Konvertáljuk a dátumot
            transaction_date = datetime.combine(form.transaction_date.data, datetime.min.time())
            
            # Ellenőrizzük a meglévő készletet
            stock = MedicineStock.objects(
                medicine=medicine,
                created_by=current_user.id
            ).first()
            
            # Ha már van készlet és nem kezdő készlet rögzítése történik
            if stock and form.transaction_type.data != 'initial':
                # Számítsuk ki a készletet a tranzakció dátumára
                quantity_at_transaction = stock.get_quantity_at_date(transaction_date)
                
                # Ellenőrizzük, hogy a tranzakció végrehajtható-e
                if form.quantity.data < 0 and abs(form.quantity.data) > quantity_at_transaction:
                    return jsonify({
                        'error': {
                            'quantity': [f'A művelet nem hajtható végre. A készlet {quantity_at_transaction} volt a megadott dátumon.']
                        }
                    }), 400
                
                # Létrehozzuk a tranzakciót
                transaction = StockTransaction(
                    medicine=medicine,
                    transaction_type=form.transaction_type.data,
                    quantity=form.quantity.data,
                    transaction_date=transaction_date,
                    notes=form.notes.data,
                    created_by=current_user.id
                )
                transaction.save()
                
                # Frissítjük a készletet
                stock.base_quantity = quantity_at_transaction + form.quantity.data
                stock.last_transaction_date = transaction_date
                stock.updated_at = datetime.utcnow()
                stock.save()
            
            # Ha még nincs készlet vagy kezdő készlet rögzítése történik
            else:
                # Kezdő készlet esetén nem lehet negatív
                if form.transaction_type.data == 'initial' and form.quantity.data <= 0:
                    return jsonify({
                        'error': {
                            'quantity': ['A kezdő készlet nem lehet nulla vagy negatív!']
                        }
                    }), 400
                
                # Ha már van készlet, nem lehet újra kezdő készletet rögzíteni
                if stock and form.transaction_type.data == 'initial':
                    return jsonify({
                        'error': {
                            'transaction_type': ['Már van rögzített készlet, nem adható meg kezdő készlet!']
                        }
                    }), 400
                
                # Létrehozzuk a tranzakciót
                transaction = StockTransaction(
                    medicine=medicine,
                    transaction_type=form.transaction_type.data,
                    quantity=form.quantity.data,
                    transaction_date=transaction_date,
                    notes=form.notes.data,
                    created_by=current_user.id
                )
                transaction.save()
                
                # Ha még nincs készlet, létrehozzuk
                if not stock:
                    stock = MedicineStock(
                        medicine=medicine,
                        base_quantity=form.quantity.data,
                        last_transaction_date=transaction_date,
                        created_by=current_user.id
                    )
                    stock.save()
                else:
                    # Ha van készlet, de kezdő készlet rögzítése történik
                    stock.base_quantity = form.quantity.data
                    stock.last_transaction_date = transaction_date
                    stock.updated_at = datetime.utcnow()
                    stock.save()
            
            # Frissített készlet adatok visszaadása
            return jsonify({
                'message': 'Stock transaction added successfully',
                'stock': stock.to_dict()
            })
            
        return jsonify({'error': form.errors}), 400
        
    except Exception as e:
        current_app.logger.error(f"Error in add_stock_transaction: {str(e)}")
        print(f"Detailed error: {str(e)}")  # Debug információ
        return jsonify({'error': str(e)}), 500

@bp.route('/api/stock/history/<medicine_id>')
@login_required
def get_stock_history(medicine_id):
    try:
        transactions = StockTransaction.objects(
            medicine=medicine_id,
            created_by=current_user.id
        ).order_by('-transaction_date')
        
        return jsonify([{
            'id': str(t.id),
            'type': t.transaction_type,
            'quantity': t.quantity,
            'date': t.transaction_date.strftime('%Y-%m-%d %H:%M'),
            'notes': t.notes
        } for t in transactions])
    except Exception as e:
        current_app.logger.error(f"Error in get_stock_history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/email-template', methods=['GET','PUT'])
@login_required
def email_template():
    if request.method == "GET":
        return jsonify({
            'template': current_user.email_template
        })
    elif request.method == 'PUT':
        try:
            new_template = request.json.get('template')
            if not new_template:
                return jsonify({'error': 'Template is required'}), 400
            
            current_user.update(set__email_template=new_template)
            return jsonify({'message':'Template updated successfully'})
        except Exception as e:
            current_app.logger.error(f"Error updating email template: {str(e)}")
            return jsonify({'error': str(e)}),500
