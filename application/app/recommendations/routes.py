# app/recommendations/routes.py
from flask import render_template, jsonify, request, current_app
from flask_login import current_user, login_required
from app.recommendations import bp
from app.recommendations.models import Recommendation
from app.recommendations.forms import RecommendationForm
from datetime import datetime

@bp.route('/')
@login_required
def index():
    # Csak a nem törölt elemeket jelenítjük meg
    recommendations = Recommendation.objects(
        created_by=current_user.id,
        is_deleted=False
    ).order_by('-created_at')
    
    return render_template('recommendations/index.html', 
                         title='Javaslatok',
                         recommendations=recommendations)

@bp.route('/modal/<modal_type>')
@login_required
def get_modal(modal_type):
    try:
        if modal_type == 'add':
            form = RecommendationForm()
            return render_template('recommendations/modals/recommendation.html', form=form)
        
        elif modal_type == 'edit':
            recom_id = request.args.get('id')
            recommendation = Recommendation.objects(
                id=recom_id, 
                created_by=current_user.id,
                is_deleted=False
            ).first_or_404()
            
            form = RecommendationForm(obj=recommendation)
            return render_template('recommendations/modals/recommendation.html', 
                                form=form,
                                recommendation=recommendation)
        
        return jsonify({'error': 'Invalid modal type'}), 400
    except Exception as e:
        current_app.logger.error(f"Error in get_modal: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/recommendations', methods=['POST'])
@login_required
def add_recommendation():
    try:
        form = RecommendationForm()
        if form.validate_on_submit():
            recommendation = Recommendation(
                recommendation_name=form.recommendation_name.data,
                doctor=form.doctor.data,
                doctor_phone=form.doctor_phone.data,
                doctor_email=form.doctor_email.data,
                recommendation_date=form.recommendation_date.data,
                recommendation_enddate=form.recommendation_enddate.data,
                notes=form.notes.data,
                created_by=current_user.id
            )
            recommendation.save()
            return jsonify({'message': 'Recommendation added successfully'})
        return jsonify({'error': form.errors}), 400
    except Exception as e:
        current_app.logger.error(f"Error in add_recommendation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/recommendations/<recommendation_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def recommendation_api(recommendation_id):
    try:
        recommendation = Recommendation.objects(
            id=recommendation_id, 
            created_by=current_user.id,
            is_deleted=False  # Csak aktív elemeket kezelünk
        ).first_or_404()
        
        if request.method == 'GET':
            return jsonify(recommendation.to_dict())
        
        elif request.method == 'PUT':
            form = RecommendationForm()
            if form.validate_on_submit():
                recommendation.update(
                    recommendation_name=form.recommendation_name.data,
                    doctor=form.doctor.data,
                    doctor_phone=form.doctor_phone.data,
                    doctor_email=form.doctor_email.data,
                    recommendation_date=form.recommendation_date.data,
                    recommendation_enddate=form.recommendation_enddate.data,
                    notes=form.notes.data,
                    updated_at=datetime.utcnow()
                )
                return jsonify({'message': 'Recommendation updated successfully'})
            return jsonify({'error': form.errors}), 400
        
        elif request.method == 'DELETE':
            # Soft delete - csak az is_deleted flag átállítása
            recommendation.update(
                is_deleted=True,
                updated_at=datetime.utcnow()
            )
            return jsonify({'message': 'Recommendation deleted successfully'})
            
    except Exception as e:
        current_app.logger.error(f"Error in recommendation_api: {str(e)}")
        return jsonify({'error': str(e)}), 500