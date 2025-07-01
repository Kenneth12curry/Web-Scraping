"""
Middleware de monitoring et observabilité
"""
import os
import sys
import logging
import logging.handlers
from datetime import datetime
from flask import request, g
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
from database.mysql_connector import mysql_connector
from flask_jwt_extended import get_jwt_identity

logger = logging.getLogger(__name__)

# Métriques Prometheus
REQUEST_COUNT = Counter('http_requests_total', 'Total des requêtes HTTP', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Latence des requêtes HTTP', ['method', 'endpoint'])
SCRAPING_REQUESTS = Counter('scraping_requests_total', 'Total des requêtes de scraping', ['method', 'status'])
API_USAGE = Counter('api_usage_total', 'Utilisation de l\'API', ['endpoint', 'user_id'])

class MonitoringMiddleware:
    """Middleware pour le monitoring et l'observabilité"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialiser le middleware avec l'application Flask"""
        # Configuration du logging avancé
        self._setup_logging()
        
        # Initialisation de Sentry
        self._setup_sentry()
        
        # Enregistrer les middlewares
        self._register_middlewares(app)
    
    def _setup_logging(self):
        """Configurer le logging avancé"""
        from config import Config
        
        # Créer le dossier logs s'il n'existe pas
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        
        # Configuration du logging
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.handlers.RotatingFileHandler(
                    os.path.join(Config.LOG_DIR, 'app.log'),
                    maxBytes=Config.LOG_MAX_BYTES,
                    backupCount=Config.LOG_BACKUP_COUNT,
                    encoding='utf-8'
                ),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logger.info("Logging avancé configuré")
    
    def _setup_sentry(self):
        """Configurer Sentry pour le tracking des erreurs"""
        from config import Config
        
        if Config.SENTRY_DSN and Config.SENTRY_DSN != 'your_sentry_dsn_here' and Config.SENTRY_DSN.strip():
            try:
                sentry_sdk.init(
                    dsn=Config.SENTRY_DSN,
                    integrations=[FlaskIntegration()],
                    traces_sample_rate=1.0,
                    environment=Config.SENTRY_ENVIRONMENT
                )
                logger.info("Sentry initialisé pour le tracking des erreurs")
            except Exception as e:
                logger.warning(f"Sentry ne peut pas être initialisé: {e}")
        else:
            logger.info("Sentry non configuré - tracking des erreurs désactivé")
    
    def _register_middlewares(self, app):
        """Enregistrer les middlewares Flask"""
        
        @app.before_request
        def before_request():
            """Middleware exécuté avant chaque requête"""
            g.start_time = datetime.now()
            
            # Logger la requête
            logger.info(f"Requête: {request.method} {request.path} - {request.remote_addr}")
            
            # Enregistrer les métriques de base
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status='pending'
            ).inc()
        
        @app.after_request
        def after_request(response):
            """Middleware exécuté après chaque requête"""
            if hasattr(g, 'start_time'):
                duration = (datetime.now() - g.start_time).total_seconds()
                
                # Enregistrer les métriques de latence
                REQUEST_LATENCY.labels(
                    method=request.method,
                    endpoint=request.endpoint or 'unknown'
                ).observe(duration)
                
                # Mettre à jour le compteur de requêtes avec le statut final
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.endpoint or 'unknown',
                    status=response.status_code
                ).inc()
                
                # Logger la réponse
                logger.info(f"Réponse: {response.status_code} - {duration:.3f}s")
            
            return response
        
        @app.errorhandler(404)
        def not_found(error):
            """Gestionnaire d'erreur 404"""
            logger.warning(f"Page non trouvée: {request.path}")
            return {'success': False, 'message': 'Endpoint non trouvé'}, 404
        
        @app.errorhandler(500)
        def internal_error(error):
            """Gestionnaire d'erreur 500"""
            logger.error(f"Erreur interne du serveur: {error}")
            return {'success': False, 'message': 'Erreur interne du serveur'}, 500
        
        @app.errorhandler(Exception)
        def handle_exception(e):
            """Gestionnaire d'exception global"""
            logger.error(f"Exception non gérée: {e}")
            return {'success': False, 'message': 'Erreur interne du serveur'}, 500

def get_metrics():
    """Obtenir les métriques Prometheus"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

def log_scraping_request(method: str, status: str):
    """Logger une requête de scraping"""
    SCRAPING_REQUESTS.labels(method=method, status=status).inc()

def log_api_usage(response):
    """Enregistrer l'utilisation de l'API"""
    try:
        # Ignorer les routes de monitoring, de santé, et les requêtes OPTIONS
        if request.method == 'OPTIONS' or request.endpoint in ['health', 'metrics', 'static']:
            return response
        
        # Récupérer l'utilisateur si connecté
        user_id = None
        try:
            current_user = get_jwt_identity()
            if current_user:
                # Récupérer l'ID utilisateur
                user_query = "SELECT id FROM users WHERE username = %s"
                user_data = mysql_connector.execute_query(user_query, (current_user,))
                if user_data:
                    user_id = user_data[0]['id']
        except Exception:
            pass  # Utilisateur non connecté
        # Ne rien enregistrer si pas d'utilisateur authentifié
        if not user_id:
            return response
        
        # Extraire le domaine de l'URL si c'est une requête de scraping
        domain = None
        if request.endpoint == 'scraping.scrape_url':
            try:
                data = request.get_json()
                if data and 'url' in data:
                    from urllib.parse import urlparse
                    parsed = urlparse(data['url'])
                    domain = parsed.netloc
            except Exception:
                pass
        
        # Enregistrer l'utilisation
        insert_query = """
            INSERT INTO api_usage (user_id, endpoint, method, status_code, response_time, domain)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        response_time = getattr(g, 'request_time', 0)
        
        mysql_connector.execute_query(insert_query, (
            user_id,
            request.endpoint,
            request.method,
            response.status_code,
            response_time,
            domain
        ))
        
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de l'utilisation API: {e}")
    
    return response

def start_request_timer():
    """Démarrer le timer pour mesurer le temps de réponse"""
    g.request_time = time.time()

def end_request_timer():
    """Terminer le timer et calculer le temps de réponse"""
    if hasattr(g, 'request_time'):
        g.request_time = time.time() - g.request_time 