"""
Service d'authentification
"""
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import logging
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import secrets
import hashlib
from config import Config
from database.mysql_connector import mysql_connector
from database.redis_connector import redis_connector

logger = logging.getLogger(__name__)

class AuthService:
    """Service de gestion de l'authentification"""
    
    def __init__(self):
        self.db = mysql_connector
        self.cache = redis_connector
    
    def get_user_by_username(self, username):
        """Récupérer un utilisateur par son nom d'utilisateur"""
        try:
            query = "SELECT * FROM users WHERE username = %s"
            result = self.db.execute_query(query, (username,))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
            return None
    
    def get_user_by_email(self, email):
        """Récupérer un utilisateur par son email"""
        try:
            query = "SELECT * FROM users WHERE email = %s"
            result = self.db.execute_query(query, (email,))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur par email: {e}")
            return None
    
    def create_user(self, username, password, email=None):
        """Créer un nouvel utilisateur"""
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = self.get_user_by_username(username)
            if existing_user:
                return False, "Nom d'utilisateur déjà utilisé"
            
            if email:
                existing_email = self.get_user_by_email(email)
                if existing_email:
                    return False, "Email déjà utilisé"
            
            # Hasher le mot de passe
            password_hash = generate_password_hash(password)
            
            # Insérer l'utilisateur
            query = """
                INSERT INTO users (username, password_hash, email, role, subscription_plan, monthly_requests_limit)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (username, password_hash, email, 'user', 'free', 30)
            
            if self.db.execute_update(query, params):
                logger.info(f"Utilisateur créé avec succès: {username}")
                return True, "Utilisateur créé avec succès"
            else:
                return False, "Erreur lors de la création de l'utilisateur"
                
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'utilisateur: {e}")
            return False, "Erreur interne du serveur"
    
    def authenticate_user(self, username, password):
        """Authentifier un utilisateur"""
        try:
            user = self.get_user_by_username(username)
            if not user:
                return None, "Nom d'utilisateur ou mot de passe incorrect"
            
            if check_password_hash(user['password_hash'], password):
                # Mettre à jour la dernière connexion
                self.update_last_login(username)
                return user, "Authentification réussie"
            else:
                return None, "Nom d'utilisateur ou mot de passe incorrect"
                
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification: {e}")
            return None, "Erreur interne du serveur"
    
    def update_last_login(self, username):
        """Mettre à jour la dernière connexion"""
        try:
            query = "UPDATE users SET last_login = NOW() WHERE username = %s"
            self.db.execute_update(query, (username,))
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la dernière connexion: {e}")
    
    def create_password_reset_token(self, user_id):
        """Créer un token de réinitialisation de mot de passe"""
        try:
            # Générer un token sécurisé
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(minutes=30)
            
            # Supprimer les anciens tokens non utilisés
            cleanup_query = "DELETE FROM password_reset_tokens WHERE user_id = %s AND (used = TRUE OR expires_at < NOW())"
            self.db.execute_update(cleanup_query, (user_id,))
            
            # Insérer le nouveau token
            insert_query = "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)"
            if self.db.execute_update(insert_query, (user_id, token, expires_at)):
                return token
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du token de réinitialisation: {e}")
            return None
    
    def verify_password_reset_token(self, token):
        """Vérifier un token de réinitialisation de mot de passe"""
        try:
            query = """
                SELECT pt.*, u.username, u.email 
                FROM password_reset_tokens pt
                JOIN users u ON pt.user_id = u.id
                WHERE pt.token = %s AND pt.used = FALSE AND pt.expires_at > NOW()
            """
            result = self.db.execute_query(query, (token,))
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du token: {e}")
            return None
    
    def mark_token_as_used(self, token):
        """Marquer un token comme utilisé"""
        try:
            query = "UPDATE password_reset_tokens SET used = TRUE WHERE token = %s"
            return self.db.execute_update(query, (token,))
        except Exception as e:
            logger.error(f"Erreur lors du marquage du token: {e}")
            return False
    
    def update_user_password(self, user_id, new_password):
        """Mettre à jour le mot de passe d'un utilisateur"""
        try:
            password_hash = generate_password_hash(new_password)
            query = "UPDATE users SET password_hash = %s WHERE id = %s"
            return self.db.execute_update(query, (password_hash, user_id))
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du mot de passe: {e}")
            return False
    
    def reset_password(self, token, new_password):
        """Réinitialiser le mot de passe avec un token"""
        try:
            # Vérifier le token
            token_data = self.verify_password_reset_token(token)
            if not token_data:
                return False, "Token invalide ou expiré"
            
            # Mettre à jour le mot de passe
            if self.update_user_password(token_data['user_id'], new_password):
                # Marquer le token comme utilisé
                self.mark_token_as_used(token)
                logger.info(f"Mot de passe réinitialisé pour l'utilisateur {token_data['username']}")
                return True, "Mot de passe réinitialisé avec succès"
            else:
                return False, "Erreur lors de la réinitialisation du mot de passe"
                
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation du mot de passe: {e}")
            return False, "Erreur interne du serveur"

# Instance globale
auth_service = AuthService() 