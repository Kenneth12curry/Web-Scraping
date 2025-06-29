"""
Application Flask modulaire - Point d'entrée principal
"""
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os
import sys
import redis

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Configuration
    from config import Config
    app.config.from_object(Config)
    
    # Extensions
    jwt = JWTManager(app)
    CORS(app)
    
    # Middleware de monitoring et observabilité
    from middleware.monitoring import MonitoringMiddleware
    monitoring = MonitoringMiddleware(app)
    
    # Middleware de gestion d'erreurs
    from middleware.error_handlers import ErrorHandlerMiddleware
    error_handlers = ErrorHandlerMiddleware(app)
    
    # Middleware de sécurité
    from middleware.security import SecurityMiddleware
    security = SecurityMiddleware(app)
    
    # Middleware de rate limiting avancé
    from middleware.rate_limiter import RateLimiterMiddleware
    rate_limiter = RateLimiterMiddleware(app)
    
    # Configuration Flask-Limiter avec gestion intelligente du storage
    limiter = _configure_flask_limiter(app)
    
    # Middleware de logging
    @app.before_request
    def log_request():
        logger.info(f"{request.method} {request.path} - {request.remote_addr}")
    
    @app.after_request
    def log_response(response):
        logger.info(f"Response: {response.status_code}")
        return response
    
    # Gestionnaire d'erreurs global
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Erreur non gérée: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur interne du serveur'
        }), 500
    
    # Enregistrer les blueprints
    try:
        # Routes d'authentification
        from routes.auth_routes import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        
        # Routes d'abonnement
        from routes.subscription_routes import subscription_bp
        app.register_blueprint(subscription_bp, url_prefix='/api/subscription')
        
        # Routes du dashboard
        from routes.dashboard_routes import dashboard_bp
        app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
        
        # Routes de santé
        from routes.health_routes import health_bp
        app.register_blueprint(health_bp, url_prefix='/api')
        
        # Routes de scraping (fonction spéciale)
        from routes.scraping_routes import scraping_routes
        scraping_routes(app)
        
        logger.info("Tous les blueprints ont été enregistrés avec succès")
        logger.info("Tous les middlewares ont été configurés avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement des blueprints: {e}")
        raise
    
    return app

def _configure_flask_limiter(app):
    """Configurer Flask-Limiter avec gestion intelligente du storage"""
    try:
        # Construire l'URL Redis à partir de la configuration
        from config import Config
        redis_config = Config.REDIS_CONFIG
        redis_url = f"redis://{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"
        
        # Tester la connexion Redis
        redis_client = redis.Redis(**redis_config)
        redis_client.ping()  # Test de connexion
        
        # Rate limiting avec Redis
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri=redis_url,
            strategy="fixed-window-elastic-expiry"
        )
        logger.info(f"✅ Flask-Limiter configuré avec Redis: {redis_url}")
        return limiter
        
    except Exception as e:
        logger.warning(f"⚠️ Redis non disponible pour Flask-Limiter: {e}")
        logger.info("🔄 Utilisation du stockage en mémoire pour Flask-Limiter (mode développement)")
        
        # Fallback vers la mémoire locale avec configuration explicite
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri="memory://",
            strategy="fixed-window"
        )
        
        # Supprimer l'avertissement en configurant explicitement le storage
        app.config['RATELIMIT_STORAGE_URL'] = "memory://"
        app.config['RATELIMIT_STRATEGY'] = "fixed-window"
        
        logger.info("✅ Flask-Limiter configuré avec stockage mémoire")
        return limiter

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 