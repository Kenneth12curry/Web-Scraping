#!/usr/bin/env python3
"""
Script pour corriger la structure de la base de données
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mysql_connector import mysql_connector


def fix_database_schema():
    """Corriger la structure de la base de données"""
    try:
        print("Correction de la structure de la base de données...")

        # Vérifier la connexion
        if not mysql_connector.test_connection():
            print("❌ Impossible de se connecter à la base de données")
            return False

        # Désactiver les contraintes de clé étrangère AVANT toute suppression
        mysql_connector.execute_query("SET FOREIGN_KEY_CHECKS=0;")
        # Vider les tables avant suppression pour éviter les contraintes FK
        delete_queries = [
            "DELETE FROM scraping_history",
            "DELETE FROM api_usage",
            "DELETE FROM users",
        ]
        for query in delete_queries:
            try:
                mysql_connector.execute_query(query)
                print(f"✅ Données supprimées: {query}")
            except Exception as e:
                print(f"⚠️  Impossible de supprimer les données ({query}): {e}")
        # Supprimer les anciennes tables si elles existent (dans l'ordre pour respecter les FK)
        drop_queries = [
            "DROP TABLE IF EXISTS scraping_history",
            "DROP TABLE IF EXISTS api_usage",
            "DROP TABLE IF EXISTS users",
        ]
        for query in drop_queries:
            mysql_connector.execute_query(query)
            print(f"✅ Table supprimée: {query}")
        # Réactiver les contraintes de clé étrangère
        mysql_connector.execute_query("SET FOREIGN_KEY_CHECKS=1;")

        # Recréer les tables avec la bonne structure
        create_users_table = """
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(100) NULL,
            last_name VARCHAR(100) NULL,
            company VARCHAR(255) NULL,
            subscription_plan VARCHAR(20) DEFAULT 'free',
            requests_limit INT DEFAULT 100,
            requests_used INT DEFAULT 0,
            reset_token VARCHAR(255),
            reset_token_expires DATETIME,
            subscription_end_date DATETIME NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            scrapedo_api_key VARCHAR(255) NULL,
            groq_api_key VARCHAR(255) NULL
        )
        """

        create_api_usage_table = """
        CREATE TABLE api_usage (
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

        create_scraping_history_table = """
        CREATE TABLE scraping_history (
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
        mysql_connector.execute_query(create_users_table)
        print("✅ Table users créée")

        mysql_connector.execute_query(create_api_usage_table)
        print("✅ Table api_usage créée")

        mysql_connector.execute_query(create_scraping_history_table)
        print("✅ Table scraping_history créée")

        # Créer un utilisateur de test
        from werkzeug.security import generate_password_hash

        password_hash = generate_password_hash("test123")
        insert_user = """
            INSERT INTO users (username, email, password_hash, subscription_plan, created_at)
            VALUES ('testuser', 'test@example.com', %s, 'free', NOW())
        """
        mysql_connector.execute_query(insert_user, (password_hash,))
        print("✅ Utilisateur de test créé")

        # Ajouter quelques données de test
        user_query = "SELECT id FROM users WHERE username = 'testuser'"
        user_data = mysql_connector.execute_query(user_query)
        if user_data:
            user_id = user_data[0]["id"]

            # Ajouter des données d'utilisation API
            api_usage_data = [
                (user_id, "/api/dashboard/stats", "GET", 200, 0.5, None),
                (user_id, "/api/dashboard/analytics", "GET", 200, 0.8, None),
                (user_id, "/api/scraping/extract", "POST", 200, 2.1, "techcrunch.com"),
                (user_id, "/api/scraping/extract", "POST", 200, 1.8, "forbes.com"),
                (user_id, "/api/auth/profile", "GET", 200, 0.3, None),
            ]

            for data in api_usage_data:
                insert_query = """
                    INSERT INTO api_usage (user_id, endpoint, method, status_code, response_time, domain, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, DATE_SUB(NOW(), INTERVAL %s DAY))
                """
                days_ago = len(api_usage_data) - api_usage_data.index(data)
                mysql_connector.execute_query(insert_query, (*data, days_ago))

            # Ajouter des données de scraping
            scraping_data = [
                (user_id, "https://techcrunch.com", "scrapedo", 25, "success", 3.2),
                (user_id, "https://forbes.com", "selenium", 18, "success", 4.1),
                (user_id, "https://wired.com", "playwright", 32, "success", 2.8),
            ]

            for data in scraping_data:
                insert_query = """
                    INSERT INTO scraping_history (user_id, url, method, articles_count, status, processing_time, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, DATE_SUB(NOW(), INTERVAL %s DAY))
                """
                days_ago = len(scraping_data) - scraping_data.index(data)
                mysql_connector.execute_query(insert_query, (*data, days_ago))

            print("✅ Données de test ajoutées")

        # Ajouter les colonnes API si elles n'existent pas
        try:
            mysql_connector.execute_query(
                "ALTER TABLE users ADD COLUMN scrapedo_api_key VARCHAR(255) NULL"
            )
            print("✅ Colonne scrapedo_api_key ajoutée")
        except Exception as e:
            print(
                f"(Info) Colonne scrapedo_api_key déjà existante ou erreur bénigne: {e}"
            )
        try:
            mysql_connector.execute_query(
                "ALTER TABLE users ADD COLUMN groq_api_key VARCHAR(255) NULL"
            )
            print("✅ Colonne groq_api_key ajoutée")
        except Exception as e:
            print(f"(Info) Colonne groq_api_key déjà existante ou erreur bénigne: {e}")

        print("✅ Structure de la base de données corrigée avec succès !")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        import traceback

        traceback.print_exc()
        return False


def add_api_columns():
    try:
        print("Ajout des colonnes scrapedo_api_key et groq_api_key à la table users...")
        try:
            mysql_connector.execute_query(
                "ALTER TABLE users ADD COLUMN scrapedo_api_key VARCHAR(255) NULL"
            )
            print("✅ Colonne scrapedo_api_key ajoutée")
        except Exception as e:
            print(
                f"(Info) Colonne scrapedo_api_key déjà existante ou erreur bénigne: {e}"
            )
        try:
            mysql_connector.execute_query(
                "ALTER TABLE users ADD COLUMN groq_api_key VARCHAR(255) NULL"
            )
            print("✅ Colonne groq_api_key ajoutée")
        except Exception as e:
            print(f"(Info) Colonne groq_api_key déjà existante ou erreur bénigne: {e}")
        print("✅ Structure de la table users vérifiée/corrigée.")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout des colonnes: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    fix_database_schema()
    add_api_columns()
