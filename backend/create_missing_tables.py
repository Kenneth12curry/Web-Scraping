#!/usr/bin/env python3
"""
Script pour créer les tables manquantes api_usage et scraping_history
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mysql_connector import mysql_connector

CREATE_API_USAGE_TABLE = '''
CREATE TABLE IF NOT EXISTS api_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INT NOT NULL,
    response_time FLOAT,
    domain VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
'''

def create_api_usage_table():
    try:
        mysql_connector.execute_query(CREATE_API_USAGE_TABLE)
        print("✅ Table 'api_usage' créée ou déjà existante.")
    except Exception as e:
        print(f"❌ Erreur lors de la création de la table 'api_usage': {e}")
        sys.exit(1)

def create_missing_tables():
    """Créer les tables manquantes"""
    try:
        print("Création des tables manquantes...")
        
        # Vérifier la connexion
        if not mysql_connector.test_connection():
            print("❌ Impossible de se connecter à la base de données")
            return False
        
        # Créer la table api_usage si elle n'existe pas
        create_api_usage_table()
        
        # Créer la table scraping_history si elle n'existe pas
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
        mysql_connector.execute_query(create_scraping_history_table)
        print("✅ Table scraping_history créée ou déjà existante")
        
        # Créer la table login_history si elle n'existe pas
        create_login_history_table = """
        CREATE TABLE IF NOT EXISTS login_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),
            location VARCHAR(255),
            device VARCHAR(255),
            status VARCHAR(20),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        mysql_connector.execute_query(create_login_history_table)
        print("✅ Table login_history créée ou déjà existante")
        
        # Ajouter les colonnes first_name, last_name, company si elles n'existent pas
        try:
            mysql_connector.execute_query("ALTER TABLE users ADD COLUMN first_name VARCHAR(100) NULL")
            print("✅ Colonne first_name ajoutée")
        except Exception as e:
            print(f"(Info) Colonne first_name déjà existante ou erreur bénigne: {e}")
        try:
            mysql_connector.execute_query("ALTER TABLE users ADD COLUMN last_name VARCHAR(100) NULL")
            print("✅ Colonne last_name ajoutée")
        except Exception as e:
            print(f"(Info) Colonne last_name déjà existante ou erreur bénigne: {e}")
        try:
            mysql_connector.execute_query("ALTER TABLE users ADD COLUMN company VARCHAR(255) NULL")
            print("✅ Colonne company ajoutée")
        except Exception as e:
            print(f"(Info) Colonne company déjà existante ou erreur bénigne: {e}")
        
        # Ajouter la colonne error_message à api_usage si elle n'existe pas
        try:
            mysql_connector.execute_query("ALTER TABLE api_usage ADD COLUMN error_message TEXT NULL")
            print("✅ Colonne error_message ajoutée à api_usage")
        except Exception as e:
            print(f"(Info) Colonne error_message déjà existante ou erreur bénigne: {e}")
        # Ajouter la colonne error_message à scraping_history si elle n'existe pas
        try:
            mysql_connector.execute_query("ALTER TABLE scraping_history ADD COLUMN error_message TEXT NULL")
            print("✅ Colonne error_message ajoutée à scraping_history")
        except Exception as e:
            print(f"(Info) Colonne error_message déjà existante ou erreur bénigne: {e}")
        
        # Vérifier que les tables existent
        tables = mysql_connector.execute_query("SHOW TABLES")
        print("Tables existantes:")
        for table in tables:
            print(f"  - {list(table.values())[0]}")
        
        print("✅ Tables manquantes créées avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    create_api_usage_table()
    create_missing_tables() 