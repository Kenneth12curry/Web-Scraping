"""
Service de gestion des abonnements
"""
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import logging
from datetime import datetime, timedelta
from database.mysql_connector import mysql_connector
from database.redis_connector import redis_connector
from config import Config

logger = logging.getLogger(__name__)

class SubscriptionService:
    """Service de gestion des abonnements"""
    
    def __init__(self):
        self.db = mysql_connector
        self.config = Config
    
    def check_subscription_limits(self, username):
        """Vérifier les limites d'abonnement d'un utilisateur"""
        try:
            query = """
                SELECT subscription_plan, monthly_requests_used, monthly_requests_limit,
                       subscription_end_date
                FROM users WHERE username = %s
            """
            result = self.db.execute_query(query, (username,))
            
            if not result:
                return {
                    'allowed': False,
                    'reason': 'Utilisateur non trouvé',
                    'plan': 'unknown',
                    'used': 0,
                    'limit': 0,
                    'remaining': 0
                }
            
            user_data = result[0]
            plan = user_data['subscription_plan']
            used = user_data['monthly_requests_used']
            limit = user_data['monthly_requests_limit']
            end_date = user_data['subscription_end_date']
            
            # Vérifier si l'abonnement est expiré
            if end_date and end_date < datetime.now():
                return {
                    'allowed': False,
                    'reason': 'Abonnement expiré',
                    'plan': plan,
                    'used': used,
                    'limit': limit,
                    'remaining': 0
                }
            
            # Vérifier les limites
            remaining = limit - used
            if remaining <= 0:
                return {
                    'allowed': False,
                    'reason': 'Limite mensuelle atteinte',
                    'plan': plan,
                    'used': used,
                    'limit': limit,
                    'remaining': 0
                }
            
            return {
                'allowed': True,
                'reason': 'OK',
                'plan': plan,
                'used': used,
                'limit': limit,
                'remaining': remaining
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des limites: {e}")
            return {
                'allowed': False,
                'reason': 'Erreur interne',
                'plan': 'unknown',
                'used': 0,
                'limit': 0,
                'remaining': 0
            }
    
    def increment_request_usage(self, username):
        """Incrémenter le compteur de requêtes utilisées"""
        try:
            query = """
                UPDATE users 
                SET monthly_requests_used = monthly_requests_used + 1
                WHERE username = %s
            """
            return self.db.execute_query(query, (username,))
        except Exception as e:
            logger.error(f"Erreur lors de l'incrémentation de l'usage: {e}")
            return False
    
    def reset_monthly_usage(self):
        """Réinitialiser l'usage mensuel (appelé par un cron job)"""
        try:
            query = "UPDATE users SET monthly_requests_used = 0"
            return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation de l'usage: {e}")
            return False
    
    def upgrade_user_subscription(self, username, plan, requests_limit):
        """Mettre à jour l'abonnement d'un utilisateur"""
        try:
            # Définir la date de fin selon le plan
            if plan == 'monthly':
                end_date = datetime.now() + timedelta(days=30)
            elif plan == 'yearly':
                end_date = datetime.now() + timedelta(days=365)
            else:  # free
                end_date = None
            
            query = """
                UPDATE users 
                SET subscription_plan = %s, 
                    monthly_requests_limit = %s,
                    subscription_start_date = NOW(),
                    subscription_end_date = %s,
                    monthly_requests_used = 0
                WHERE username = %s
            """
            
            if self.db.execute_query(query, (plan, requests_limit, end_date, username)):
                logger.info(f"Abonnement mis à jour pour {username}: {plan} ({requests_limit} requêtes)")
                return True, "Abonnement mis à jour avec succès"
            else:
                return False, "Erreur lors de la mise à jour de l'abonnement"
                
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'abonnement: {e}")
            return False, "Erreur interne du serveur"
    
    def get_subscription_status(self, username):
        """Obtenir le statut de l'abonnement d'un utilisateur"""
        try:
            query = """
                SELECT subscription_plan, monthly_requests_used, monthly_requests_limit,
                       subscription_start_date, subscription_end_date, last_login
                FROM users WHERE username = %s
            """
            result = self.db.execute_query(query, (username,))
            
            if not result:
                return None
            
            user_data = result[0]
            
            # Calculer les statistiques
            remaining = user_data['monthly_requests_limit'] - user_data['monthly_requests_used']
            usage_percentage = (user_data['monthly_requests_used'] / user_data['monthly_requests_limit']) * 100
            
            # Vérifier si l'abonnement est actif
            is_active = True
            if user_data['subscription_end_date'] and user_data['subscription_end_date'] < datetime.now():
                is_active = False
            
            return {
                'plan': user_data['subscription_plan'],
                'used': user_data['monthly_requests_used'],
                'limit': user_data['monthly_requests_limit'],
                'remaining': remaining,
                'usage_percentage': round(usage_percentage, 2),
                'is_active': is_active,
                'start_date': user_data['subscription_start_date'],
                'end_date': user_data['subscription_end_date'],
                'last_login': user_data['last_login']
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut: {e}")
            return None

# Instance globale
subscription_service = SubscriptionService() 