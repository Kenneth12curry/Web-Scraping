"""
Routes de gestion des abonnements
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.subscription_service import subscription_service

logger = logging.getLogger(__name__)

# Créer le blueprint
subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/upgrade', methods=['POST'])
@jwt_required()
def upgrade_subscription():
    """Mettre à jour l'abonnement d'un utilisateur"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'Données JSON requises'}), 400
        
        plan = data.get('plan')
        requests_limit = data.get('requests_limit')
        
        if not plan or not requests_limit:
            return jsonify({'success': False, 'message': 'Plan et limite de requêtes requis'}), 400
        
        # Mettre à jour l'abonnement
        success, message = subscription_service.upgrade_user_subscription(
            current_user, plan, requests_limit
        )
        
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'abonnement: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@subscription_bp.route('/status', methods=['GET'])
@jwt_required()
def get_subscription_status():
    """Obtenir le statut de l'abonnement"""
    try:
        current_user = get_jwt_identity()
        
        # Obtenir le statut
        status = subscription_service.get_subscription_status(current_user)
        
        if status:
            return jsonify({
                'success': True,
                'subscription': status
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500 