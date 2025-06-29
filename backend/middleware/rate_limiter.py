"""
Middleware de rate limiting avancé
"""
import os
import sys
import logging
from flask import request, jsonify, g
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiterMiddleware:
    """Middleware pour la gestion avancée du rate limiting"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialiser le middleware avec l'application Flask"""
        self._register_rate_limiters(app)
    
    def _register_rate_limiters(self, app):
        """Enregistrer les décorateurs de rate limiting"""
        
        def rate_limit(limit_type="default"):
            """Décorateur pour appliquer des limites de taux personnalisées"""
            def decorator(f):
                @wraps(f)
                def decorated_function(*args, **kwargs):
                    # Obtenir l'identifiant de l'utilisateur
                    user_id = self._get_user_identifier()
                    
                    # Vérifier les limites selon le type
                    if not self._check_rate_limit(user_id, limit_type):
                        return jsonify({
                            'success': False,
                            'message': f'Limite de taux dépassée pour {limit_type}',
                            'retry_after': self._get_retry_after(user_id, limit_type)
                        }), 429
                    
                    # Incrémenter le compteur
                    self._increment_counter(user_id, limit_type)
                    
                    return f(*args, **kwargs)
                return decorated_function
            return decorator
        
        # Enregistrer le décorateur dans l'application
        app.rate_limit = rate_limit
    
    def _get_user_identifier(self):
        """Obtenir l'identifiant unique de l'utilisateur"""
        try:
            from flask_jwt_extended import get_jwt_identity
            current_user = get_jwt_identity()
            if current_user:
                return f"user:{current_user}"
        except Exception:
            pass
        
        # Fallback sur l'IP
        return f"ip:{request.remote_addr}"
    
    def _check_rate_limit(self, user_id, limit_type):
        """Vérifier si l'utilisateur respecte les limites"""
        try:
            from database.redis_connector import redis_connector
            
            # Définir les limites selon le type
            limits = {
                "auth": {"requests": 5, "window": 300},  # 5 req/5min pour l'auth
                "scraping": {"requests": 10, "window": 60},  # 10 req/min pour le scraping
                "api": {"requests": 100, "window": 3600},  # 100 req/h pour l'API
                "default": {"requests": 50, "window": 3600}  # 50 req/h par défaut
            }
            
            limit_config = limits.get(limit_type, limits["default"])
            key = f"rate_limit:{user_id}:{limit_type}"
            
            # Vérifier le compteur actuel
            current_count = redis_connector.get_connection().get(key)
            if current_count and int(current_count) >= limit_config["requests"]:
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Erreur lors de la vérification du rate limit: {e}")
            # En cas d'erreur, autoriser la requête
            return True
    
    def _increment_counter(self, user_id, limit_type):
        """Incrémenter le compteur de requêtes"""
        try:
            from database.redis_connector import redis_connector
            
            limits = {
                "auth": {"requests": 5, "window": 300},
                "scraping": {"requests": 10, "window": 60},
                "api": {"requests": 100, "window": 3600},
                "default": {"requests": 50, "window": 3600}
            }
            
            limit_config = limits.get(limit_type, limits["default"])
            key = f"rate_limit:{user_id}:{limit_type}"
            
            # Incrémenter avec expiration
            redis_conn = redis_connector.get_connection()
            pipe = redis_conn.pipeline()
            pipe.incr(key)
            pipe.expire(key, limit_config["window"])
            pipe.execute()
            
        except Exception as e:
            logger.warning(f"Erreur lors de l'incrémentation du rate limit: {e}")
    
    def _get_retry_after(self, user_id, limit_type):
        """Obtenir le temps d'attente avant la prochaine requête"""
        try:
            from database.redis_connector import redis_connector
            
            key = f"rate_limit:{user_id}:{limit_type}"
            ttl = redis_connector.get_connection().ttl(key)
            
            return max(0, ttl)
            
        except Exception:
            return 60  # Fallback: 1 minute

def apply_rate_limits(app):
    """Appliquer les limites de taux aux routes spécifiques"""
    
    @app.route('/api/auth/login', methods=['POST'])
    @app.rate_limit("auth")
    def login_with_rate_limit():
        # Cette route sera gérée par le blueprint auth_routes
        pass
    
    @app.route('/api/auth/register', methods=['POST'])
    @app.rate_limit("auth")
    def register_with_rate_limit():
        # Cette route sera gérée par le blueprint auth_routes
        pass
    
    @app.route('/api/scraping/extract', methods=['POST'])
    @app.rate_limit("scraping")
    def scraping_with_rate_limit():
        # Cette route sera gérée par scraping_routes
        pass 