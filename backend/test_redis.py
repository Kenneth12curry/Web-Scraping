"""
Script de test pour vérifier la connexion Redis et Flask-Limiter
"""

import os
import sys
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_redis_connection():
    """Tester la connexion Redis"""
    try:
        logger.info("Test de la connexion Redis...")

        # Importer la configuration
        from config import Config

        # Tester la connexion Redis
        import redis

        redis_client = redis.Redis(**Config.REDIS_CONFIG)

        # Test de ping
        response = redis_client.ping()
        if response:
            logger.info("✓ Connexion Redis réussie")

            # Tester quelques opérations de base
            redis_client.set("test_key", "test_value", ex=60)
            value = redis_client.get("test_key")
            if value == b"test_value":
                logger.info("✓ Opérations Redis de base fonctionnelles")
                redis_client.delete("test_key")
                return True
            else:
                logger.error("✗ Erreur lors des opérations Redis de base")
                return False
        else:
            logger.error("✗ Échec du ping Redis")
            return False

    except Exception as e:
        logger.error(f"✗ Erreur de connexion Redis: {e}")
        return False


def test_flask_limiter_config():
    """Tester la configuration Flask-Limiter"""
    try:
        logger.info("Test de la configuration Flask-Limiter...")

        from config import Config
        from flask import Flask
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address

        # Créer une app de test
        app = Flask(__name__)

        # Configuration Redis pour Flask-Limiter
        redis_config = Config.REDIS_CONFIG
        redis_url = f"redis://{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"

        # Rate limiting avec Redis
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri=redis_url,
        )

        logger.info(f"✓ Flask-Limiter configuré avec Redis: {redis_url}")
        return True

    except Exception as e:
        logger.error(f"✗ Erreur de configuration Flask-Limiter: {e}")
        return False


def main():
    """Fonction principale de test"""
    logger.info("=== Test de la configuration Redis et Flask-Limiter ===")

    # Test de la connexion Redis
    if not test_redis_connection():
        logger.error("❌ Échec du test de connexion Redis")
        return False

    # Test de la configuration Flask-Limiter
    if not test_flask_limiter_config():
        logger.error("❌ Échec du test de configuration Flask-Limiter")
        return False

    logger.info("✅ Tous les tests Redis et Flask-Limiter ont réussi!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
