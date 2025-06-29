#!/usr/bin/env python3
"""
Script de test pour diagnostiquer l'erreur 500 sur /api/dashboard/stats
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import get_user_stats, get_mysql_connection, init_db

def test_mysql_connection():
    """Test de la connexion MySQL"""
    print("=== Test de connexion MySQL ===")
    try:
        conn = get_mysql_connection()
        if conn:
            print("✅ Connexion MySQL OK")
            return True
        else:
            print("❌ Connexion MySQL échouée")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion MySQL: {e}")
        return False

def test_database_init():
    """Test de l'initialisation de la base de données"""
    print("\n=== Test d'initialisation de la base de données ===")
    try:
        success = init_db()
        if success:
            print("✅ Initialisation de la base de données OK")
            return True
        else:
            print("❌ Initialisation de la base de données échouée")
            return False
    except Exception as e:
        print(f"❌ Erreur initialisation DB: {e}")
        return False

def test_user_stats():
    """Test de la fonction get_user_stats"""
    print("\n=== Test de get_user_stats ===")
    try:
        # Test avec un utilisateur existant
        stats = get_user_stats('admin')
        print(f"✅ Stats pour 'admin': {stats}")
        
        # Test avec un utilisateur inexistant
        stats2 = get_user_stats('user_inexistant')
        print(f"✅ Stats pour 'user_inexistant': {stats2}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur get_user_stats: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dashboard_stats_logic():
    """Test de la logique du dashboard stats"""
    print("\n=== Test de la logique dashboard stats ===")
    try:
        current_user = 'admin'
        
        # Statistiques utilisateur
        user_stats = get_user_stats(current_user)
        print(f"✅ User stats récupérées: {user_stats}")
        
        # Configuration API
        from app import HAS_SCRAPEDO, HAS_GROQ, SCRAPEDO_API_KEY, GROQ_API_KEY
        api_config = {
            'has_scrapedo': HAS_SCRAPEDO,
            'has_groq': HAS_GROQ,
            'scrapedo_token': SCRAPEDO_API_KEY[:10] + '...' if SCRAPEDO_API_KEY else None,
            'groq_token': GROQ_API_KEY[:10] + '...' if GROQ_API_KEY else None
        }
        print(f"✅ API config: {api_config}")
        
        # Informations d'abonnement
        from datetime import datetime, timedelta
        subscription = {
            'plan': 'Free',
            'api_calls_used': user_stats.get('general', {}).get('total_requests', 0),
            'api_calls_limit': 1000,
            'concurrent_calls_used': 0,
            'concurrent_calls_limit': 5,
            'renew_date': (datetime.now() + timedelta(days=30)).strftime('%d.%m.%Y %H:%M'),
            'owner': 'diandiallo974@gmail.com'
        }
        print(f"✅ Subscription: {subscription}")
        
        # Réponse complète
        response_data = {
            'success': True,
            'user_stats': user_stats,
            'api_config': api_config,
            'subscription': subscription
        }
        print(f"✅ Response data: {response_data}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur logique dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Diagnostic de l'erreur 500 sur /api/dashboard/stats")
    print("=" * 60)
    
    # Tests en séquence
    mysql_ok = test_mysql_connection()
    if not mysql_ok:
        print("\n❌ Arrêt: Problème de connexion MySQL")
        sys.exit(1)
    
    db_init_ok = test_database_init()
    if not db_init_ok:
        print("\n❌ Arrêt: Problème d'initialisation de la base de données")
        sys.exit(1)
    
    user_stats_ok = test_user_stats()
    if not user_stats_ok:
        print("\n❌ Arrêt: Problème avec get_user_stats")
        sys.exit(1)
    
    dashboard_logic_ok = test_dashboard_stats_logic()
    if not dashboard_logic_ok:
        print("\n❌ Arrêt: Problème avec la logique dashboard")
        sys.exit(1)
    
    print("\n✅ Tous les tests sont passés !")
    print("Le problème pourrait être lié à l'authentification JWT ou à un autre aspect.") 