#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration MySQL et Redis dans l'application FinData
"""

import os
import sys
import requests
import json
import time
from dotenv import load_dotenv

# Ajouter le répertoire backend au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Charger les variables d'environnement
load_dotenv()

def test_mysql_connection():
    """Test de connexion MySQL"""
    print("🔍 Test de connexion MySQL...")
    
    try:
        import mysql.connector
        from mysql.connector import Error
        
        # Configuration MySQL depuis les variables d'environnement
        mysql_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', ''),
            'database': os.getenv('MYSQL_DATABASE', 'findata'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': True
        }
        
        # Test de connexion
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        # Test de requête simple
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("✅ Connexion MySQL réussie")
            
            # Vérifier si les tables existent
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            print(f"📋 Tables trouvées: {tables}")
            
            # Vérifier la table users
            if 'users' in tables:
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                print(f"👥 Nombre d'utilisateurs: {user_count}")
            
            conn.close()
            return True
        else:
            print("❌ Test de requête MySQL échoué")
            return False
            
    except Error as e:
        print(f"❌ Erreur de connexion MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue MySQL: {e}")
        return False

def test_redis_connection():
    """Test de connexion Redis"""
    print("\n🔍 Test de connexion Redis...")
    
    try:
        import redis
        
        # Configuration Redis depuis les variables d'environnement
        redis_config = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', 6379)),
            'db': int(os.getenv('REDIS_DB', 0)),
            'decode_responses': True
        }
        
        # Test de connexion
        redis_client = redis.Redis(**redis_config)
        redis_client.ping()
        
        # Test de lecture/écriture
        test_key = "test_findata"
        test_value = {"test": "data", "timestamp": time.time()}
        
        redis_client.setex(test_key, 60, json.dumps(test_value))
        retrieved_value = redis_client.get(test_key)
        
        if retrieved_value:
            parsed_value = json.loads(retrieved_value)
            if parsed_value["test"] == "data":
                print("✅ Connexion Redis réussie")
                redis_client.delete(test_key)
                return True
        
        print("❌ Test de lecture/écriture Redis échoué")
        return False
        
    except Exception as e:
        print(f"❌ Erreur de connexion Redis: {e}")
        return False

def test_app_health():
    """Test de santé de l'application Flask"""
    print("\n🔍 Test de santé de l'application...")
    
    try:
        # URL de l'application (ajustez selon votre configuration)
        base_url = "http://localhost:8080"
        health_url = f"{base_url}/api/health"
        
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Application Flask accessible")
            print(f"📊 Statut: {health_data.get('status')}")
            print(f"🔧 Services: {health_data.get('services')}")
            return True
        else:
            print(f"❌ Application Flask non accessible (status: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'application Flask")
        print("💡 Assurez-vous que l'application est démarrée sur http://localhost:8080")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test de santé: {e}")
        return False

def test_app_endpoints():
    """Test des endpoints de l'application"""
    print("\n🔍 Test des endpoints de l'application...")
    
    try:
        base_url = "http://localhost:8080"
        
        # Test de l'endpoint de métriques
        metrics_url = f"{base_url}/api/metrics"
        response = requests.get(metrics_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Endpoint métriques accessible")
        else:
            print(f"❌ Endpoint métriques non accessible (status: {response.status_code})")
        
        # Test de l'endpoint de scraping (sans authentification)
        scraping_url = f"{base_url}/api/scraping/extract"
        response = requests.post(scraping_url, json={}, timeout=10)
        
        if response.status_code == 401:  # Attendu car pas d'authentification
            print("✅ Endpoint scraping protégé (authentification requise)")
        else:
            print(f"⚠️ Endpoint scraping inattendu (status: {response.status_code})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des endpoints: {e}")
        return False

def check_environment():
    """Vérification de l'environnement"""
    print("🔍 Vérification de l'environnement...")
    
    # Variables d'environnement importantes
    important_vars = [
        'MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DATABASE',
        'REDIS_HOST', 'REDIS_PORT', 'REDIS_DB',
        'JWT_SECRET_KEY', 'ADMIN_USERNAME', 'ADMIN_PASSWORD'
    ]
    
    missing_vars = []
    for var in important_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Masquer les valeurs sensibles
            if 'PASSWORD' in var or 'SECRET' in var:
                print(f"✅ {var}: {'*' * len(value)}")
            else:
                print(f"✅ {var}: {value}")
    
    if missing_vars:
        print(f"⚠️ Variables manquantes: {missing_vars}")
        print("💡 Créez un fichier .env basé sur env.example")
        return False
    
    return True

def main():
    """Fonction principale de test"""
    print("🚀 Test d'intégration MySQL/Redis pour FinData")
    print("=" * 50)
    
    # Vérifier l'environnement
    env_ok = check_environment()
    
    # Tests de connexion
    mysql_ok = test_mysql_connection()
    redis_ok = test_redis_connection()
    
    # Tests de l'application
    app_ok = test_app_health()
    endpoints_ok = test_app_endpoints()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    tests = [
        ("Environnement", env_ok),
        ("MySQL", mysql_ok),
        ("Redis", redis_ok),
        ("Application Flask", app_ok),
        ("Endpoints", endpoints_ok)
    ]
    
    all_passed = True
    for test_name, passed in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Tous les tests sont passés ! L'application est prête.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
        print("\n💡 Conseils de dépannage:")
        print("1. Vérifiez que MySQL est démarré et accessible")
        print("2. Vérifiez que Redis est démarré et accessible")
        print("3. Vérifiez que l'application Flask est démarrée")
        print("4. Vérifiez le fichier .env et les variables d'environnement")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 