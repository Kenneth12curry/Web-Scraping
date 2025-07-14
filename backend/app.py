"""
Application Flask modulaire - Point d'entrée principal
"""

from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sock import Sock
import logging
import os
import sys
import redis


# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
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
    sock = Sock(app)

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

    # Skip rate limit for OPTIONS (CORS preflight) - doit être AVANT le rate limiter
    @app.before_request
    def skip_rate_limit_for_options():
        if request.method == "OPTIONS":
            response = make_response("", 200)
            response.headers["Access-Control-Allow-Origin"] = request.headers.get(
                "Origin", "*"
            )
            response.headers["Access-Control-Allow-Methods"] = (
                "GET,POST,PUT,DELETE,OPTIONS"
            )
            response.headers["Access-Control-Allow-Headers"] = request.headers.get(
                "Access-Control-Request-Headers", "*"
            )
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response

    # Configuration Flask-Limiter avec gestion intelligente du storage
    limiter = _configure_flask_limiter(app)

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = request.headers.get(
            "Origin", "*"
        )
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = request.headers.get(
            "Access-Control-Request-Headers", "*"
        )
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    # Gestionnaire d'erreurs global
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Erreur non gérée: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500

    # Gestionnaire d'erreur JWT explicite
    @jwt.unauthorized_loader
    def custom_unauthorized_response(callback):
        return jsonify({"success": False, "message": "Authentification requise"}), 401

    @jwt.invalid_token_loader
    def custom_invalid_token_response(callback):
        return jsonify({"success": False, "message": "Token invalide"}), 422

    @jwt.expired_token_loader
    def custom_expired_token_response(jwt_header, jwt_payload):
        return jsonify({"success": False, "message": "Token expiré"}), 401

    @sock.route("/ws/notifications")
    def notifications(ws):
        logger.info(f"WebSocket connection established from {request.remote_addr}")
        while True:
            try:
                data = ws.receive(timeout=1)
                if data:
                    logger.info(f"Received data on websocket: {data}")
                    ws.send(f"Echo: {data}")
            except TimeoutError:
                pass
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
        logger.info(f"WebSocket connection closed for {request.remote_addr}")

    # Enregistrer les blueprints
    try:
        # Routes d'authentification
        from routes.auth_routes import auth_bp

        app.register_blueprint(auth_bp, url_prefix="/api/auth")

        # Routes d'abonnement
        from routes.subscription_routes import subscription_bp

        app.register_blueprint(subscription_bp, url_prefix="/api/subscription")

        # Routes du dashboard
        from routes.dashboard_routes import dashboard_bp

        app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

        # Routes de santé
        from routes.health_routes import health_bp

        app.register_blueprint(health_bp, url_prefix="/api")

        # Routes de scraping (fonction spéciale)
        import routes.scraping_routes

        routes.scraping_routes.scraping_routes(app)

        logger.info("Tous les blueprints ont été enregistrés avec succès")
        logger.info("Tous les middlewares ont été configurés avec succès")

    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement des blueprints: {e}")
        raise

    return app


def _configure_flask_limiter(app):
    """Configurer Flask-Limiter pour utiliser Redis"""
    from config import Config

    redis_url = f"redis://{Config.REDIS_CONFIG['host']}:{Config.REDIS_CONFIG['port']}/{Config.REDIS_CONFIG['db']}"

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=Config.RATE_LIMIT_DEFAULT,
        storage_uri=redis_url,
        strategy="fixed-window",
    )
    logger.info(f"Flask-Limiter configuré avec Redis: {redis_url}")
    return limiter


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
