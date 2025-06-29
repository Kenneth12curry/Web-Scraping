#!/usr/bin/env python3
"""
Script de test pour générer des données de test et vérifier le dashboard
"""

import requests
import json
import time
import sqlite3
from datetime import datetime, timedelta
import random

# Configuration
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
STATS_URL = f"{BASE_URL}/api/dashboard/stats"
ANALYTICS_URL = f"{BASE_URL}/api/dashboard/analytics"
SCRAPING_URL = f"{BASE_URL}/api/scraping/extract"

# Credentials de test
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login():
    """Connexion pour obtenir un token JWT"""
    try:
        response = requests.post(LOGIN_URL, json={
            'username': ADMIN_USERNAME,
            'password': ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('access_token')
        
        print(f"❌ Erreur de connexion: {response.status_code}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de la connexion: {e}")
        return None

def generate_test_data(token):
    """Générer des données de test en effectuant des requêtes"""
    headers = {'Authorization': f'Bearer {token}'}
    
    # URLs de test
    test_urls = [
        "https://www.lemonde.fr",
        "https://www.lefigaro.fr", 
        "https://www.leparisien.fr",
        "https://www.liberation.fr",
        "https://www.20minutes.fr"
    ]
    
    print("🔄 Génération de données de test...")
    
    for i, url in enumerate(test_urls):
        try:
            print(f"  📄 Test {i+1}/5: {url}")
            response = requests.post(SCRAPING_URL, 
                json={'url': url, 'method': 'scrapedo', 'max_articles': 5},
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"    ✅ Succès")
            else:
                print(f"    ❌ Échec: {response.status_code}")
                
            time.sleep(1)  # Pause entre les requêtes
            
        except Exception as e:
            print(f"    ❌ Erreur: {e}")

def check_dashboard_data(token):
    """Vérifier les données du dashboard"""
    headers = {'Authorization': f'Bearer {token}'}
    
    print("\n📊 Vérification des données du dashboard...")
    
    # Vérifier les stats
    try:
        response = requests.get(STATS_URL, headers=headers)
        if response.status_code == 200:
            stats = response.json()
            if stats.get('success'):
                user_stats = stats.get('user_stats', {})
                print(f"✅ Stats récupérées:")
                print(f"   📈 Total requêtes: {user_stats.get('total_requests', 0)}")
                print(f"   ✅ Succès: {user_stats.get('successful_requests', 0)}")
                print(f"   ❌ Échecs: {user_stats.get('failed_requests', 0)}")
                print(f"   📊 Taux de succès: {user_stats.get('success_rate', 0)}%")
                print(f"   ⏱️ Temps de réponse: {user_stats.get('avg_response_time', 0)}s")
                
                if user_stats.get('top_domains'):
                    print(f"   🌐 Domaines populaires: {len(user_stats['top_domains'])}")
                
                if user_stats.get('weekly_history'):
                    print(f"   📅 Historique hebdomadaire: {len(user_stats['weekly_history'])} jours")
                
                if user_stats.get('recent_requests'):
                    print(f"   🔄 Activité récente: {len(user_stats['recent_requests'])} requêtes")
            else:
                print("❌ Erreur dans la réponse des stats")
        else:
            print(f"❌ Erreur HTTP pour les stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des stats: {e}")
    
    # Vérifier les analytics
    try:
        response = requests.get(ANALYTICS_URL, headers=headers)
        if response.status_code == 200:
            analytics = response.json()
            if analytics.get('success'):
                print(f"✅ Analytics récupérées:")
                if analytics.get('domain_stats'):
                    print(f"   📊 Stats par domaine: {len(analytics['domain_stats'])}")
                if analytics.get('scraping_history'):
                    print(f"   📄 Historique scraping: {len(analytics['scraping_history'])}")
            else:
                print("❌ Erreur dans la réponse des analytics")
        else:
            print(f"❌ Erreur HTTP pour les analytics: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des analytics: {e}")

def main():
    """Fonction principale"""
    print("🚀 Test du Dashboard FinData IA-M.K")
    print("=" * 50)
    
    # Connexion
    print("🔐 Connexion...")
    token = login()
    if not token:
        print("❌ Impossible de se connecter. Arrêt du test.")
        return
    
    print("✅ Connexion réussie!")
    
    # Générer des données de test
    generate_test_data(token)
    
    # Vérifier les données du dashboard
    check_dashboard_data(token)
    
    print("\n🎉 Test terminé!")
    print("💡 Vous pouvez maintenant vérifier le dashboard dans votre navigateur:")
    print("   Frontend: http://localhost:3000")
    print("   Backend: http://localhost:5000")

if __name__ == "__main__":
    main() 