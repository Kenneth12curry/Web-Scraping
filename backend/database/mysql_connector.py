"""
Connecteur MySQL avec gestion d'erreurs améliorée
"""

import mysql.connector
from mysql.connector import pooling
import logging
import time
from config import Config

logger = logging.getLogger(__name__)


class MySQLConnector:
    def __init__(self):
        self.connection_pool = None
        self.max_retries = 3
        self.retry_delay = 1  # secondes
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialiser le pool de connexions avec gestion d'erreurs"""
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                **Config.MYSQL_CONFIG
            )
            logger.info("Pool de connexions MySQL initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du pool MySQL: {e}")
            self.connection_pool = None

    def _get_connection(self):
        """Obtenir une connexion du pool avec retry"""
        for attempt in range(self.max_retries):
            try:
                if self.connection_pool is None:
                    self._initialize_pool()

                if self.connection_pool:
                    connection = self.connection_pool.get_connection()
                    # Vérifier que la connexion est valide
                    if connection.is_connected():
                        return connection
                    else:
                        connection.close()
                        raise Exception("Connexion non valide")

            except Exception as e:
                logger.warning(
                    f"Tentative {attempt + 1}/{self.max_retries} échouée: {e}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    # Réinitialiser le pool si nécessaire
                    if "pool exhausted" in str(e).lower():
                        self._initialize_pool()
                else:
                    logger.error(
                        "Impossible d'obtenir une connexion MySQL après tous les essais"
                    )
                    raise

    def execute_query(self, query, params=None):
        """Exécuter une requête avec gestion d'erreurs améliorée"""
        connection = None
        cursor = None

        try:
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Déterminer le type de requête
            if query.strip().upper().startswith(("SELECT", "SHOW", "DESCRIBE")):
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                return cursor.rowcount

        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL lors de l'exécution de la requête: {e}")
            if connection:
                connection.rollback()
            raise
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'exécution de la requête: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                try:
                    connection.close()
                except:
                    pass

    def execute_many(self, query, params_list):
        """Exécuter plusieurs requêtes avec gestion d'erreurs"""
        connection = None
        cursor = None

        try:
            connection = self._get_connection()
            cursor = connection.cursor()

            cursor.executemany(query, params_list)
            connection.commit()
            return cursor.rowcount

        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL lors de l'exécution multiple: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                try:
                    connection.close()
                except:
                    pass

    def test_connection(self):
        """Tester la connexion MySQL"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return True
        except Exception as e:
            logger.error(f"Test de connexion MySQL échoué: {e}")
            return False

    def close_pool(self):
        """Fermer le pool de connexions"""
        if self.connection_pool:
            try:
                self.connection_pool.close()
                logger.info("Pool de connexions MySQL fermé")
            except Exception as e:
                logger.error(f"Erreur lors de la fermeture du pool: {e}")


# Instance globale
mysql_connector = MySQLConnector()
