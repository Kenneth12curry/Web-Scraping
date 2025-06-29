"""
Connecteur MySQL pour l'application Findata IA
"""
import mysql.connector
from mysql.connector import Error
import logging
import os
from config import Config

logger = logging.getLogger(__name__)

class MySQLConnector:
    """Classe pour gérer la connexion MySQL"""
    
    def __init__(self):
        self.connection = None
        self.config = Config.MYSQL_CONFIG.copy()
        # Ajouter le port s'il n'est pas dans la config
        if 'port' not in self.config:
            self.config['port'] = 3306
    
    def get_connection(self):
        """Obtenir une connexion MySQL"""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
                logger.info("Connexion MySQL établie")
            return self.connection
        except Error as e:
            logger.error(f"Erreur de connexion MySQL: {e}")
            return None
    
    def execute_query(self, query, params=None):
        """Exécuter une requête SQL"""
        try:
            connection = self.get_connection()
            if not connection:
                return None
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                connection.commit()
                result = cursor.rowcount
            
            cursor.close()
            return result
            
        except Error as e:
            logger.error(f"Erreur d'exécution MySQL: {e}")
            return None
    
    def close_connection(self):
        """Fermer la connexion MySQL"""
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                logger.info("Connexion MySQL fermée")
        except Error as e:
            logger.error(f"Erreur lors de la fermeture MySQL: {e}")
    
    def init_database(self):
        """Initialiser la base de données avec les tables nécessaires"""
        try:
            # Table des utilisateurs
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                subscription_plan VARCHAR(20) DEFAULT 'free',
                requests_limit INT DEFAULT 100,
                requests_used INT DEFAULT 0,
                reset_token VARCHAR(255),
                reset_token_expires DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            
            # Table d'utilisation de l'API
            create_api_usage_table = """
            CREATE TABLE IF NOT EXISTS api_usage (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                endpoint VARCHAR(100),
                method VARCHAR(10),
                status_code INT,
                response_time FLOAT,
                domain VARCHAR(100),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
            
            # Table d'historique de scraping
            create_scraping_history_table = """
            CREATE TABLE IF NOT EXISTS scraping_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                url VARCHAR(500),
                method VARCHAR(50),
                articles_count INT,
                status VARCHAR(20),
                processing_time FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
            
            # Exécuter les requêtes de création
            self.execute_query(create_users_table)
            self.execute_query(create_api_usage_table)
            self.execute_query(create_scraping_history_table)
            
            logger.info("Base de données initialisée avec succès")
            return True
            
        except Error as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
            return False

    def test_connection(self):
        """Tester la connexion à la base de données"""
        try:
            connection = self.get_connection()
            if not connection:
                raise Exception("Impossible d'obtenir une connexion du pool")
            
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            # Vérifier que le résultat existe et contient la valeur attendue
            if result and len(result) > 0 and result[0] == 1:
                logger.info("✅ Test de connexion MySQL réussi")
                return True
            else:
                raise Exception("Test de connexion MySQL échoué")
                
        except Exception as e:
            logger.error(f"❌ Test de connexion MySQL échoué: {e}")
            return False

# Instance globale
mysql_connector = MySQLConnector() 