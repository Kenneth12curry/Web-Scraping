"""
Connecteur Redis avec fallback
"""
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import logging
import redis
import json
import pickle
from config import Config

logger = logging.getLogger(__name__)

class RedisConnector:
    """Connecteur Redis avec fallback vers la mémoire locale"""
    
    def __init__(self):
        self.config = Config.REDIS_CONFIG
        self.redis_client = None
        self.fallback_cache = {}
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialiser la connexion Redis"""
        try:
            self.redis_client = redis.Redis(**self.config)
            # Test de connexion
            self.redis_client.ping()
            logger.info("✅ Connexion Redis établie")
        except Exception as e:
            logger.warning(f"⚠️ Redis non disponible: {e}")
            logger.info("Utilisation du cache en mémoire local")
            self.redis_client = None
    
    def test_connection(self):
        """Tester la connexion Redis"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                logger.info("✅ Test de connexion Redis réussi")
                return True
            else:
                logger.warning("⚠️ Redis non disponible - utilisation du cache local")
                return False
        except Exception as e:
            logger.error(f"❌ Test de connexion Redis échoué: {e}")
            return False
    
    def get_cached_data(self, key):
        """Récupérer des données du cache"""
        try:
            if self.redis_client:
                # Essayer Redis d'abord
                data = self.redis_client.get(key)
                if data:
                    return json.loads(data)
            else:
                # Fallback vers la mémoire locale
                if key in self.fallback_cache:
                    cached_item = self.fallback_cache[key]
                    if cached_item['expires_at'] > self._get_current_time():
                        return cached_item['data']
                    else:
                        # Supprimer l'élément expiré
                        del self.fallback_cache[key]
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du cache: {e}")
            return None
    
    def set_cached_data(self, key, data, expire_time=3600):
        """Stocker des données en cache"""
        try:
            if self.redis_client:
                # Utiliser Redis
                json_data = json.dumps(data)
                self.redis_client.setex(key, expire_time, json_data)
            else:
                # Fallback vers la mémoire locale
                self.fallback_cache[key] = {
                    'data': data,
                    'expires_at': self._get_current_time() + expire_time
                }
                # Nettoyer les éléments expirés
                self._cleanup_expired_items()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du stockage en cache: {e}")
            return False
    
    def delete_cached_data(self, key):
        """Supprimer des données du cache"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                if key in self.fallback_cache:
                    del self.fallback_cache[key]
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du cache: {e}")
            return False
    
    def clear_all_cache(self):
        """Vider tout le cache"""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                self.fallback_cache.clear()
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du vidage du cache: {e}")
            return False
    
    def get_cache_stats(self):
        """Obtenir les statistiques du cache"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    'type': 'redis',
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory_human': info.get('used_memory_human', '0B'),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0)
                }
            else:
                return {
                    'type': 'memory',
                    'items_count': len(self.fallback_cache),
                    'memory_usage': 'local'
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {e}")
            return {'type': 'error', 'error': str(e)}
    
    def _get_current_time(self):
        """Obtenir le temps actuel en secondes"""
        import time
        return int(time.time())
    
    def _cleanup_expired_items(self):
        """Nettoyer les éléments expirés du cache local"""
        current_time = self._get_current_time()
        expired_keys = [
            key for key, item in self.fallback_cache.items()
            if item['expires_at'] <= current_time
        ]
        for key in expired_keys:
            del self.fallback_cache[key]
        
        if expired_keys:
            logger.debug(f"Nettoyage de {len(expired_keys)} éléments expirés du cache local")

# Instance globale
redis_connector = RedisConnector() 