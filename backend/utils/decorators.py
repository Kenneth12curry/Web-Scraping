"""
Décorateurs utilitaires pour l'application
"""
import functools
import logging
import time
from flask import request, jsonify, g

logger = logging.getLogger(__name__)

def monitor_request(f):
    """Décorateur pour monitorer les requêtes"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Stocker le temps de début
        g.start_time = time.time()
        
        try:
            response = f(*args, **kwargs)
            
            # Calculer la durée
            duration = time.time() - g.start_time
            
            # Logger la requête
            logger.info(f"Requête {request.method} {request.path} - {response.status_code} - {duration:.3f}s")
            
            return response
            
        except Exception as e:
            # En cas d'erreur, logger quand même
            duration = time.time() - g.start_time
            logger.error(f"Erreur dans {f.__name__}: {e} - {duration:.3f}s")
            raise
    
    return decorated_function

def log_api_usage(f):
    """Décorateur pour logger l'utilisation de l'API"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            response = f(*args, **kwargs)
            
            # Logger l'utilisation
            from flask_jwt_extended import get_jwt_identity
            current_user = get_jwt_identity()
            user_id = current_user if current_user else 'anonymous'
            
            logger.info(f"API utilisée: {request.endpoint} par {user_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur dans log_api_usage: {e}")
            raise
    
    return decorated_function

def validate_json(*required_fields):
    """Décorateur pour valider les champs JSON requis"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'Données JSON requises'}), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'success': False, 
                    'message': f'Champs manquants: {", ".join(missing_fields)}'
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cache_result(expire_time=3600):
    """Décorateur pour mettre en cache le résultat d'une fonction"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Générer une clé de cache basée sur la fonction et ses arguments
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Essayer de récupérer du cache
            try:
                from database.redis_connector import redis_connector
                cached_result = redis_connector.get_cached_data(cache_key)
                
                if cached_result:
                    return cached_result
                
                # Exécuter la fonction et mettre en cache
                result = f(*args, **kwargs)
                redis_connector.set_cached_data(cache_key, result, expire_time)
                
                return result
            except Exception as e:
                logger.warning(f"Cache non disponible: {e}")
                # Fallback: exécuter sans cache
                return f(*args, **kwargs)
        return decorated_function
    return decorator 