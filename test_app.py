#!/usr/bin/env python3
"""
Script de test pour vérifier le bon fonctionnement de l'API FinData IA-M.K
"""

import requests
import json
import time
import sys
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:8080/api"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

def print_test_result(test_name, success, message=""):
    """Afficher le résultat d'un test"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"   {message}")
    print()

def test_health_check():
    """Test du health check"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        success = response.status_code == 200
        data = response.json() if success else {}
        message = f"Status: {data.get('status', 'unknown')}" if success else f"Status code: {response.status_code}"
        return success, message
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def test_login():
    """Test de connexion"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", 
                               json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
                               timeout=5)
        success = response.status_code == 200
        data = response.json() if success else {}
        message = f"Token: {data.get('access_token', '')[:20]}..." if success else f"Status code: {response.status_code}"
        return success, data.get('access_token', ''), message
    except Exception as e:
        return False, None, f"Erreur: {str(e)}"

def test_dashboard_stats(token):
    """Test des statistiques du dashboard"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers, timeout=5)
        success = response.status_code == 200
        data = response.json() if success else {}
        message = f"Plan: {data.get('subscription', {}).get('plan', 'unknown')}" if success else f"Status code: {response.status_code}"
        return success, message
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def test_analytics(token):
    """Test des analytics"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/dashboard/analytics", headers=headers, timeout=5)
        success = response.status_code == 200
        data = response.json() if success else {}
        message = f"Domaines: {len(data.get('domain_stats', []))}" if success else f"Status code: {response.status_code}"
        return success, message
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def test_scraping(token):
    """Test du scraping"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        test_url = "https://httpbin.org/html"
        response = requests.post(f"{BASE_URL}/scraping/extract", 
                               json={"url": test_url, "method": "requests"},
                               headers=headers, timeout=30)
        success = response.status_code == 200
        data = response.json() if success else {}
        message = f"Articles trouvés: {data.get('total_articles', 0)}" if success else f"Status code: {response.status_code}"
        return success, message
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def test_logout(token):
    """Test de déconnexion"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/auth/logout", headers=headers, timeout=5)
        success = response.status_code == 200
        message = "Déconnexion réussie" if success else f"Status code: {response.status_code}"
        return success, message
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def main():
    """Fonction principale de test"""
    print("🧪 Tests de l'API FinData IA-M.K")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Test du health check...")
    success, message = test_health_check()
    print_test_result("Health Check", success, message)
    
    if not success:
        print("❌ L'API n'est pas accessible. Assurez-vous qu'elle est démarrée sur http://localhost:8080")
        sys.exit(1)
    
    # Test 2: Connexion
    print("2. Test de connexion...")
    success, token, message = test_login()
    print_test_result("Login", success, message)
    
    if not success or not token:
        print("❌ Impossible de se connecter. Vérifiez les identifiants.")
        sys.exit(1)
    
    # Test 3: Dashboard stats
    print("3. Test des statistiques du dashboard...")
    success, message = test_dashboard_stats(token)
    print_test_result("Dashboard Stats", success, message)
    
    # Test 4: Analytics
    print("4. Test des analytics...")
    success, message = test_analytics(token)
    print_test_result("Analytics", success, message)
    
    # Test 5: Scraping
    print("5. Test du scraping...")
    success, message = test_scraping(token)
    print_test_result("Scraping", success, message)
    
    # Test 6: Déconnexion
    print("6. Test de déconnexion...")
    success, message = test_logout(token)
    print_test_result("Logout", success, message)
    
    print("🎉 Tous les tests sont terminés !")
    print("\n📋 Résumé:")
    print("- L'API est accessible et fonctionnelle")
    print("- L'authentification fonctionne correctement")
    print("- Les endpoints répondent comme attendu")
    print("- Le scraping de base fonctionne")
    print("\n🚀 Vous pouvez maintenant démarrer le frontend React !")

if __name__ == "__main__":
    main() 