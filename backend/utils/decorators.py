"""
Décorateurs utilitaires pour l'application
"""

import functools
import logging
from flask import request, jsonify, g

logger = logging.getLogger(__name__)


def validate_json(*required_fields):
    """Décorateur pour valider les champs JSON requis"""

    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if not data:
                return (
                    jsonify({"success": False, "message": "Données JSON requises"}),
                    400,
                )

            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": f'Champs manquants: {", ".join(missing_fields)}',
                        }
                    ),
                    400,
                )

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
