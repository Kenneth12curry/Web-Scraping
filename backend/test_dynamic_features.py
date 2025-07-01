#!/usr/bin/env python3
"""
Script de test pour les nouvelles fonctionnalités dynamiques
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
}

def test_weather_api():
    """Tester l'API météo du Maroc"""
    print("🌤️  Test de l'API météo du Maroc...")
    
    try:
        # D'abord se connecter
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        })
        
        if login_response.status_code != 200:
            print("❌ Échec de connexion pour tester la météo")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tester l'API météo
        weather_response = requests.get(f"{BASE_URL}/dashboard/weather", headers=headers)
        
        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            if weather_data["success"]:
                weather = weather_data["weather"]
                print(f"✅ Météo récupérée pour {weather['city']}, Maroc")
                print(f"   🌡️  Température: {weather['temperature']}°C")
                print(f"   ☁️  Condition: {weather['condition']}")
                print(f"   💧 Humidité: {weather['humidity']}%")
                print(f"   💨 Vent: {weather['wind']} km/h")
                if weather.get('feels_like'):
                    print(f"   🌡️  Ressenti: {weather['feels_like']}°C")
                if weather.get('pressure'):
                    print(f"   📊 Pression: {weather['pressure']} hPa")
                if weather.get('visibility'):
                    print(f"   👁️  Visibilité: {weather['visibility']} km")
                return True
            else:
                print("❌ Erreur dans la réponse météo")
                return False
        else:
            print(f"❌ Erreur HTTP {weather_response.status_code} pour la météo")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test météo: {e}")
        return False

def test_notifications_api():
    """Tester l'API des notifications dynamiques"""
    print("\n🔔 Test de l'API des notifications...")
    
    try:
        # D'abord se connecter
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        })
        
        if login_response.status_code != 200:
            print("❌ Échec de connexion pour tester les notifications")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tester l'API notifications
        notifications_response = requests.get(f"{BASE_URL}/dashboard/notifications", headers=headers)
        
        if notifications_response.status_code == 200:
            notifications_data = notifications_response.json()
            if notifications_data["success"]:
                notifications = notifications_data["notifications"]
                print(f"✅ {len(notifications)} notifications récupérées")
                
                for i, notif in enumerate(notifications[:3]):  # Afficher les 3 premières
                    print(f"   {i+1}. [{notif['type']}] {notif['title']}")
                    print(f"      📝 {notif['message']}")
                    print(f"      ⏰ {notif['time']}")
                
                return True
            else:
                print("❌ Erreur dans la réponse notifications")
                return False
        else:
            print(f"❌ Erreur HTTP {notifications_response.status_code} pour les notifications")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test notifications: {e}")
        return False

def test_dashboard_stats():
    """Tester les statistiques du dashboard"""
    print("\n📊 Test des statistiques du dashboard...")
    
    try:
        # D'abord se connecter
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        })
        
        if login_response.status_code != 200:
            print("❌ Échec de connexion pour tester les stats")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tester les statistiques
        stats_response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            if stats_data["success"]:
                stats = stats_data["user_stats"]
                print(f"✅ Statistiques récupérées")
                print(f"   📈 Total requêtes: {stats.get('total_requests', 0)}")
                print(f"   ✅ Succès: {stats.get('successful_requests', 0)}")
                print(f"   ❌ Échecs: {stats.get('failed_requests', 0)}")
                print(f"   📊 Taux de succès: {stats.get('success_rate', 0):.1f}%")
                print(f"   📰 Articles extraits: {stats.get('total_articles', 0)}")
                return True
            else:
                print("❌ Erreur dans la réponse stats")
                return False
        else:
            print(f"❌ Erreur HTTP {stats_response.status_code} pour les stats")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test stats: {e}")
        return False

def test_analytics_api():
    """Tester l'API analytics"""
    print("\n📈 Test de l'API analytics...")
    
    try:
        # D'abord se connecter
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        })
        
        if login_response.status_code != 200:
            print("❌ Échec de connexion pour tester analytics")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tester l'API analytics
        analytics_response = requests.get(f"{BASE_URL}/dashboard/analytics", headers=headers)
        
        if analytics_response.status_code == 200:
            analytics_data = analytics_response.json()
            if analytics_data["success"]:
                print(f"✅ Analytics récupérées")
                print(f"   📊 Données graphiques: {len(analytics_data.get('chart_data', {}).get('labels', []))} jours")
                print(f"   🌐 Top domaines: {len(analytics_data.get('top_domains', []))}")
                print(f"   📝 Activité récente: {len(analytics_data.get('recent_activity', []))}")
                return True
            else:
                print("❌ Erreur dans la réponse analytics")
                return False
        else:
            print(f"❌ Erreur HTTP {analytics_response.status_code} pour analytics")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test analytics: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test des fonctionnalités dynamiques de FinData IA")
    print("=" * 60)
    
    # Vérifier que le serveur est en cours d'exécution
    try:
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code != 200:
            print("❌ Le serveur backend n'est pas accessible")
            return
        print("✅ Serveur backend accessible")
    except Exception as e:
        print(f"❌ Impossible de se connecter au serveur: {e}")
        return
    
    # Tests
    tests = [
        test_weather_api,
        test_notifications_api,
        test_dashboard_stats,
        test_analytics_api
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
            results.append(False)
    
    # Résumé
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests réussis: {passed}/{total}")
    print(f"❌ Tests échoués: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 Toutes les fonctionnalités dynamiques fonctionnent correctement !")
    else:
        print("⚠️  Certaines fonctionnalités nécessitent des corrections")

if __name__ == "__main__":
    main() 