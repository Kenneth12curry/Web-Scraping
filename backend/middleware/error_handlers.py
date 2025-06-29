"""
Middleware de gestion d'erreurs avancé
"""
import os
import sys
import logging
import traceback
from flask import request, jsonify, g
from werkzeug.exceptions import HTTPException
from datetime import datetime

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware:
    """Middleware pour la gestion avancée des erreurs"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialiser le middleware avec l'application Flask"""
        self._register_error_handlers(app)
    
    def _register_error_handlers(self, app):
        """Enregistrer les gestionnaires d'erreurs"""
        
        @app.errorhandler(400)
        def bad_request(error):
            """Gestionnaire d'erreur 400 - Bad Request"""
            return self._format_error_response(
                error_code=400,
                error_type="Bad Request",
                message="Requête malformée ou paramètres invalides",
                details=str(error) if hasattr(error, 'description') else None
            )
        
        @app.errorhandler(401)
        def unauthorized(error):
            """Gestionnaire d'erreur 401 - Unauthorized"""
            return self._format_error_response(
                error_code=401,
                error_type="Unauthorized",
                message="Authentification requise",
                details="Token JWT manquant ou invalide"
            )
        
        @app.errorhandler(403)
        def forbidden(error):
            """Gestionnaire d'erreur 403 - Forbidden"""
            return self._format_error_response(
                error_code=403,
                error_type="Forbidden",
                message="Accès refusé",
                details="Permissions insuffisantes pour cette ressource"
            )
        
        @app.errorhandler(404)
        def not_found(error):
            """Gestionnaire d'erreur 404 - Not Found"""
            return self._format_error_response(
                error_code=404,
                error_type="Not Found",
                message="Ressource non trouvée",
                details=f"L'endpoint {request.path} n'existe pas"
            )
        
        @app.errorhandler(405)
        def method_not_allowed(error):
            """Gestionnaire d'erreur 405 - Method Not Allowed"""
            return self._format_error_response(
                error_code=405,
                error_type="Method Not Allowed",
                message="Méthode HTTP non autorisée",
                details=f"La méthode {request.method} n'est pas autorisée pour cet endpoint"
            )
        
        @app.errorhandler(429)
        def too_many_requests(error):
            """Gestionnaire d'erreur 429 - Too Many Requests"""
            return self._format_error_response(
                error_code=429,
                error_type="Too Many Requests",
                message="Trop de requêtes",
                details="Limite de taux dépassée. Veuillez réessayer plus tard."
            )
        
        @app.errorhandler(500)
        def internal_server_error(error):
            """Gestionnaire d'erreur 500 - Internal Server Error"""
            # Logger l'erreur pour le debugging
            logger.error(f"Erreur interne du serveur: {error}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return self._format_error_response(
                error_code=500,
                error_type="Internal Server Error",
                message="Erreur interne du serveur",
                details="Une erreur inattendue s'est produite. Veuillez réessayer plus tard."
            )
        
        @app.errorhandler(Exception)
        def handle_unexpected_error(error):
            """Gestionnaire d'exception non gérée"""
            # Logger l'erreur pour le debugging
            logger.error(f"Exception non gérée: {error}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return self._format_error_response(
                error_code=500,
                error_type="Unexpected Error",
                message="Erreur inattendue",
                details="Une erreur inattendue s'est produite. Veuillez réessayer plus tard."
            )
        
        @app.errorhandler(HTTPException)
        def handle_http_exception(error):
            """Gestionnaire d'exception HTTP générique"""
            return self._format_error_response(
                error_code=error.code,
                error_type=error.name,
                message=error.description,
                details=str(error)
            )
    
    def _format_error_response(self, error_code, error_type, message, details=None):
        """Formater une réponse d'erreur standardisée"""
        response = {
            'success': False,
            'error': {
                'code': error_code,
                'type': error_type,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'path': request.path,
                'method': request.method
            }
        }
        
        if details:
            response['error']['details'] = details
        
        # Ajouter des informations de debugging en mode développement
        if os.getenv('FLASK_ENV') == 'development':
            response['error']['debug'] = {
                'user_agent': request.headers.get('User-Agent'),
                'ip_address': request.remote_addr,
                'request_id': getattr(g, 'request_id', None)
            }
        
        return jsonify(response), error_code

def log_error(error, context=None):
    """Logger une erreur avec contexte"""
    error_info = {
        'error': str(error),
        'type': type(error).__name__,
        'timestamp': datetime.now().isoformat(),
        'path': request.path,
        'method': request.method,
        'user_agent': request.headers.get('User-Agent'),
        'ip_address': request.remote_addr
    }
    
    if context:
        error_info['context'] = context
    
    logger.error(f"Erreur enregistrée: {error_info}")
    
    # Envoyer à Sentry si configuré
    try:
        import sentry_sdk
        sentry_sdk.capture_exception(error)
    except Exception:
        pass

def create_error_response(message, error_code=400, details=None):
    """Créer une réponse d'erreur personnalisée"""
    response = {
        'success': False,
        'message': message,
        'error_code': error_code
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), error_code 