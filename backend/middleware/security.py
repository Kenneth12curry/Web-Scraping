"""
Middleware de sécurité pour la protection de l'application
"""
import os
import sys
import logging
import re
from flask import request, jsonify, g
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Middleware pour la sécurité de l'application"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialiser le middleware avec l'application Flask"""
        self._register_security_headers(app)
        self._register_security_checks(app)
    
    def _register_security_headers(self, app):
        """Enregistrer les en-têtes de sécurité"""
        
        @app.after_request
        def add_security_headers(response):
            """Ajouter les en-têtes de sécurité à toutes les réponses"""
            
            # Protection XSS
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # Protection CSRF
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Politique de contenu
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
            
            # Référer Policy
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Permissions Policy
            response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
            
            return response
    
    def _register_security_checks(self, app):
        """Enregistrer les vérifications de sécurité"""
        
        @app.before_request
        def security_checks():
            """Vérifications de sécurité avant chaque requête"""
            
            # Vérifier l'User-Agent
            user_agent = request.headers.get('User-Agent', '')
            if self._is_suspicious_user_agent(user_agent):
                logger.warning(f"User-Agent suspect détecté: {user_agent}")
                return jsonify({
                    'success': False,
                    'message': 'Accès refusé'
                }), 403
            
            # Vérifier les en-têtes suspects
            if self._has_suspicious_headers(request.headers):
                logger.warning(f"En-têtes suspects détectés de {request.remote_addr}")
                return jsonify({
                    'success': False,
                    'message': 'Requête suspecte détectée'
                }), 400
            
            # Vérifier la taille du contenu
            if request.content_length and request.content_length > 10 * 1024 * 1024:  # 10MB
                logger.warning(f"Contenu trop volumineux de {request.remote_addr}: {request.content_length} bytes")
                return jsonify({
                    'success': False,
                    'message': 'Contenu trop volumineux'
                }), 413
    
    def _is_suspicious_user_agent(self, user_agent):
        """Vérifier si l'User-Agent est suspect"""
        # En mode développement, être moins restrictif
        if os.getenv('FLASK_ENV') == 'development':
            return False
            
        suspicious_patterns = [
            r'bot',
            r'crawler',
            r'spider',
            r'scanner',
            r'nmap'
        ]
        
        user_agent_lower = user_agent.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent_lower):
                return True
        
        return False
    
    def _has_suspicious_headers(self, headers):
        """Vérifier s'il y a des en-têtes suspects"""
        suspicious_headers = [
            'X-Forwarded-For',
            'X-Real-IP',
            'X-Originating-IP',
            'CF-Connecting-IP'
        ]
        
        for header in suspicious_headers:
            if header in headers:
                return True
        
        return False

def validate_input(data, max_length=1000):
    """Valider les données d'entrée"""
    if isinstance(data, str) and len(data) > max_length:
        return False, f"Données trop longues (max: {max_length} caractères)"
    
    # Vérifier les caractères dangereux
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'data:text/html',
        r'vbscript:',
        r'onload=',
        r'onerror='
    ]
    
    if isinstance(data, str):
        for pattern in dangerous_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return False, "Contenu dangereux détecté"
    
    return True, "Données valides"

def sanitize_input(data):
    """Nettoyer les données d'entrée"""
    if isinstance(data, str):
        # Supprimer les balises HTML
        data = re.sub(r'<[^>]*>', '', data)
        
        # Échapper les caractères spéciaux
        data = data.replace('&', '&amp;')
        data = data.replace('<', '&lt;')
        data = data.replace('>', '&gt;')
        data = data.replace('"', '&quot;')
        data = data.replace("'", '&#x27;')
        
        # Supprimer les caractères de contrôle
        data = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', data)
    
    return data

def require_https(f):
    """Décorateur pour exiger HTTPS"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and os.getenv('FLASK_ENV') == 'production':
            return jsonify({
                'success': False,
                'message': 'HTTPS requis en production'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def log_security_event(event_type, details, severity="INFO"):
    """Logger un événement de sécurité"""
    event = {
        'type': event_type,
        'details': details,
        'severity': severity,
        'timestamp': datetime.now().isoformat(),
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'path': request.path,
        'method': request.method
    }
    
    if severity == "WARNING":
        logger.warning(f"Événement de sécurité: {event}")
    elif severity == "ERROR":
        logger.error(f"Événement de sécurité: {event}")
    else:
        logger.info(f"Événement de sécurité: {event}") 