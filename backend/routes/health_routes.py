"""
Routes de santé et monitoring
"""

from flask import Blueprint, jsonify
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import logging
import sys
import os

# Ajouter le répertoire parent au path


from database.mysql_connector import mysql_connector
from database.redis_connector import redis_connector
from config import Config

logger = logging.getLogger(__name__)

# Créer le blueprint
health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Vérification de la santé de l'application"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0",
            "services": {},
        }

        # Vérifier MySQL
        try:
            if mysql_connector.test_connection():
                health_status["services"]["mysql"] = "healthy"
            else:
                health_status["services"]["mysql"] = "unhealthy: Connection test failed"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["services"]["mysql"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        finally:
            # Ensure connection is closed if it was opened
            pass

        # Vérifier Redis
        try:
            if redis_connector.test_connection():
                health_status["services"]["redis"] = "healthy"
            else:
                health_status["services"]["redis"] = "unhealthy: Connection test failed"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["services"]["redis"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        finally:
            # Ensure connection is closed if it was opened
            pass

        # Vérifier les API keys
        health_status["services"]["groq"] = (
            "available" if Config.HAS_GROQ else "unavailable"
        )
        health_status["services"]["scrapedo"] = (
            "available" if Config.HAS_SCRAPEDO else "unavailable"
        )

        status_code = 200 if health_status["status"] == "healthy" else 503

        return jsonify(health_status), status_code

    except Exception as e:
        logger.error(f"Erreur lors du health check: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


@health_bp.route("/metrics")
def metrics():
    """Métriques Prometheus"""
    try:
        return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}
    except Exception as e:
        logger.error(f"Erreur lors de la génération des métriques: {e}")
        return jsonify({"error": "Erreur lors de la génération des métriques"}), 500
