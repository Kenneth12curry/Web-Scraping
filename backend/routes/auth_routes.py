"""
Routes d'authentification
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
import logging
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config import Config
from services.auth_service import auth_service
from services.subscription_service import subscription_service

logger = logging.getLogger(__name__)

# Créer le blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données JSON requises'}), 400
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Nom d\'utilisateur et mot de passe requis'}), 400
        
        if len(username) < 3:
            return jsonify({'success': False, 'message': 'Le nom d\'utilisateur doit contenir au moins 3 caractères'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
        
        # Créer l'utilisateur
        success, message = auth_service.create_user(username, password, email)
        
        if success:
            return jsonify({'success': True, 'message': message}), 201
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        logger.error(f"Erreur lors de l'inscription: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données JSON requises'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Nom d\'utilisateur et mot de passe requis'}), 400
        
        # Authentifier l'utilisateur
        user, message = auth_service.authenticate_user(username, password)
        
        if user:
            # Créer le token JWT
            access_token = create_access_token(identity=username)
            
            # Obtenir le statut de l'abonnement
            subscription_status = subscription_service.get_subscription_status(username)
            
            return jsonify({
                'success': True,
                'message': message,
                'access_token': access_token,
                'user': {
                    'username': user['username'],
                    'email': user.get('email'),
                    'role': user.get('role', 'user'),
                    'subscription': subscription_status
                }
            }), 200
        else:
            return jsonify({'success': False, 'message': message}), 401
            
    except Exception as e:
        logger.error(f"Erreur lors de la connexion: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Déconnexion d'un utilisateur"""
    try:
        # En JWT, la déconnexion se fait côté client en supprimant le token
        # Ici on peut ajouter une logique de blacklist si nécessaire
        return jsonify({'success': True, 'message': 'Déconnexion réussie'}), 200
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Demande de réinitialisation de mot de passe"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données JSON requises'}), 400
        
        email = data.get('email')
        if not email:
            return jsonify({'success': False, 'message': 'Email requis'}), 400
        
        # Vérifier si l'utilisateur existe
        user = auth_service.get_user_by_email(email)
        if not user:
            # Pour des raisons de sécurité, ne pas révéler si l'email existe
            return jsonify({'success': True, 'message': 'Si cet email existe, un lien de réinitialisation a été envoyé'}), 200
        
        # Créer le token de réinitialisation
        token = auth_service.create_password_reset_token(user['id'])
        if not token:
            return jsonify({'success': False, 'message': 'Erreur lors de la création du token'}), 500
        
        # TODO: Envoyer l'email avec le token
        # Pour l'instant, on retourne le token (en production, envoyer par email)
        
        return jsonify({
            'success': True, 
            'message': 'Lien de réinitialisation créé',
            'token': token  # À supprimer en production
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la demande de réinitialisation: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Réinitialisation du mot de passe"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données JSON requises'}), 400
        
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not token or not new_password:
            return jsonify({'success': False, 'message': 'Token et nouveau mot de passe requis'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
        
        # Réinitialiser le mot de passe
        success, message = auth_service.reset_password(token, new_password)
        
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@auth_bp.route('/verify-reset-token', methods=['POST'])
def verify_reset_token():
    """Vérifier un token de réinitialisation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données JSON requises'}), 400
        
        token = data.get('token')
        if not token:
            return jsonify({'success': False, 'message': 'Token requis'}), 400
        
        # Vérifier le token
        token_data = auth_service.verify_password_reset_token(token)
        
        if token_data:
            return jsonify({
                'success': True, 
                'message': 'Token valide',
                'username': token_data['username']
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 400
            
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du token: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500 