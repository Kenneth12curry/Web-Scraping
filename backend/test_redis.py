"""
Script de test pour vérifier la connexion Redis et Flask-Limiter
"""

import logging
import pytest
import redis
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Importer la configuration depuis le backend
from config import Config

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_redis_connection():
    """Tester la connexion Redis et les opérations de base."""
    try:
        logger.info("Test de la connexion Redis...")
        redis_client = redis.Redis(**Config.REDIS_CONFIG)

        # Test de ping
        response = redis_client.ping()
        assert response, "Le ping Redis a échoué"
        logger.info("✓ Connexion Redis réussie")

        # Tester les opérations SET/GET/DELETE
        redis_client.set("test_key", "test_value", ex=60)
        value = redis_client.get("test_key")
        assert value == b"test_value", "La valeur lue dans Redis est incorrecte"
        logger.info("✓ Opérations Redis de base fonctionnelles")
        redis_client.delete("test_key")

    except redis.exceptions.ConnectionError as e:
        pytest.fail(f"Impossible de se connecter à Redis: {e}")
    except Exception as e:
        pytest.fail(f"Une erreur inattendue est survenue lors du test Redis: {e}")


def test_flask_limiter_config():
    """Tester si la configuration de Flask-Limiter avec Redis se charge sans erreur."""
    try:
        logger.info("Test de la configuration Flask-Limiter...")

        app = Flask(__name__)
        redis_url = f"redis://{Config.REDIS_CONFIG['host']}:{Config.REDIS_CONFIG['port']}/{Config.REDIS_CONFIG['db']}"

        Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri=redis_url,
        )

        logger.info(f"✓ Flask-Limiter configuré avec Redis: {redis_url}")
        # Si aucune exception n'est levée, le test est considéré comme réussi.

    except Exception as e:
        pytest.fail(f"La configuration de Flask-Limiter a échoué: {e}")
