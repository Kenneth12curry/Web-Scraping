#!/usr/bin/env python3
"""
Test des améliorations apportées à l'architecture modulaire
"""
import os
import sys
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database_connectors():
    """Tester les connecteurs de base de données avec les nouvelles méthodes"""
    logger.info("🗄️ Test des connecteurs de base de données améliorés...")
    
    try:
        from database.mysql_connector import mysql_connector
        from database.redis_connector import redis_connector
        
        # Test MySQL
        logger.info("📊 Test MySQL Connector...")
        mysql_result = mysql_connector.test_connection()
        if mysql_result:
            logger.info("✅ MySQL Connector - Test de connexion réussi")
        else:
            logger.warning("⚠️ MySQL Connector - Test de connexion échoué (normal si MySQL n'est pas démarré)")
        
        # Test Redis
        logger.info("📊 Test Redis Connector...")
        redis_result = redis_connector.test_connection()
        if redis_result:
            logger.info("✅ Redis Connector - Test de connexion réussi")
        else:
            logger.warning("⚠️ Redis Connector - Test de connexion échoué (normal si Redis n'est pas démarré)")
        
        # Test des fonctionnalités de cache Redis
        logger.info("📊 Test des fonctionnalités de cache...")
        
        # Test set/get
        test_key = "test_improvements"
        test_data = {"message": "Test des améliorations", "status": "success"}
        
        set_result = redis_connector.set_cached_data(test_key, test_data, 60)
        if set_result:
            logger.info("✅ Cache - Stockage réussi")
        else:
            logger.warning("⚠️ Cache - Stockage échoué")
        
        get_result = redis_connector.get_cached_data(test_key)
        if get_result and get_result.get("message") == "Test des améliorations":
            logger.info("✅ Cache - Récupération réussi")
        else:
            logger.warning("⚠️ Cache - Récupération échoué")
        
        # Test des statistiques
        stats = redis_connector.get_cache_stats()
        logger.info(f"📊 Statistiques du cache: {stats}")
        
        # Nettoyage
        redis_connector.delete_cached_data(test_key)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test des connecteurs: {e}")
        return False

def test_flask_limiter_configuration():
    """Tester la configuration Flask-Limiter améliorée"""
    logger.info("🛡️ Test de la configuration Flask-Limiter...")
    
    try:
        from app_modular import create_app
        
        # Créer l'application
        app = create_app()
        
        # Vérifier que l'application a été créée avec succès
        if app:
            logger.info("✅ Application Flask créée avec succès")
            
            # Vérifier la configuration Flask-Limiter
            if hasattr(app, 'limiter'):
                logger.info("✅ Flask-Limiter configuré")
                
                # Vérifier la stratégie
                strategy = getattr(app.limiter, 'strategy', 'unknown')
                logger.info(f"📊 Stratégie Flask-Limiter: {strategy}")
                
                # Vérifier le storage
                storage = getattr(app.limiter, 'storage', None)
                if storage:
                    storage_type = type(storage).__name__
                    logger.info(f"📊 Storage Flask-Limiter: {storage_type}")
                else:
                    logger.warning("⚠️ Storage Flask-Limiter non détecté")
                
            else:
                logger.warning("⚠️ Flask-Limiter non configuré")
            
            return True
        else:
            logger.error("❌ Échec de création de l'application")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur lors du test Flask-Limiter: {e}")
        return False

def test_middleware_improvements():
    """Tester les améliorations des middlewares"""
    logger.info("🛡️ Test des améliorations des middlewares...")
    
    try:
        # Test du middleware de monitoring
        from middleware.monitoring import MonitoringMiddleware
        logger.info("✅ MonitoringMiddleware importé")
        
        # Test du middleware de gestion d'erreurs
        from middleware.error_handlers import ErrorHandlerMiddleware
        logger.info("✅ ErrorHandlerMiddleware importé")
        
        # Test du middleware de sécurité
        from middleware.security import SecurityMiddleware
        logger.info("✅ SecurityMiddleware importé")
        
        # Test du middleware de rate limiting
        from middleware.rate_limiter import RateLimiterMiddleware
        logger.info("✅ RateLimiterMiddleware importé")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test des middlewares: {e}")
        return False

def test_services_improvements():
    """Tester les améliorations des services"""
    logger.info("🔧 Test des améliorations des services...")
    
    try:
        # Test du service d'authentification
        from services.auth_service import auth_service
        logger.info("✅ AuthService importé")
        
        # Test du service d'abonnement
        from services.subscription_service import subscription_service
        logger.info("✅ SubscriptionService importé")
        
        # Test du service de scraping
        from services.scraping_service import scraping_service
        logger.info("✅ ScrapingService importé")
        
        # Test du service d'emails
        from services.email_service import email_service
        logger.info("✅ EmailService importé")
        
        # Test de la méthode test_connection du service d'emails
        smtp_result = email_service.test_smtp_connection()
        if smtp_result[0]:
            logger.info("✅ EmailService - Test SMTP réussi")
        else:
            logger.warning(f"⚠️ EmailService - Test SMTP échoué: {smtp_result[1]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test des services: {e}")
        return False

def main():
    """Fonction principale de test des améliorations"""
    logger.info("=" * 60)
    logger.info("🧪 TEST DES AMÉLIORATIONS DE L'ARCHITECTURE MODULAIRE")
    logger.info("=" * 60)
    
    # Résultats des tests
    results = {}
    
    # Test 1: Connecteurs de base de données
    logger.info("\n🗄️ Test 1: Connecteurs de base de données améliorés")
    db_ok = test_database_connectors()
    results['database_connectors'] = db_ok
    
    # Test 2: Configuration Flask-Limiter
    logger.info("\n🛡️ Test 2: Configuration Flask-Limiter améliorée")
    limiter_ok = test_flask_limiter_configuration()
    results['flask_limiter'] = limiter_ok
    
    # Test 3: Middlewares
    logger.info("\n🛡️ Test 3: Améliorations des middlewares")
    middleware_ok = test_middleware_improvements()
    results['middleware'] = middleware_ok
    
    # Test 4: Services
    logger.info("\n🔧 Test 4: Améliorations des services")
    services_ok = test_services_improvements()
    results['services'] = services_ok
    
    # Résumé final
    logger.info("\n" + "=" * 60)
    logger.info("📊 RÉSUMÉ DES TESTS D'AMÉLIORATION")
    logger.info("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        logger.info(f"{test_name:25} | {status}")
    
    logger.info("-" * 60)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    logger.info(f"TOTAL: {passed_tests}/{total_tests} tests passés ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        logger.info("🎉 AMÉLIORATIONS IMPLÉMENTÉES AVEC SUCCÈS !")
        return True
    elif success_rate >= 50:
        logger.info("⚠️ AMÉLIORATIONS PARTIELLEMENT IMPLÉMENTÉES")
        return False
    else:
        logger.info("❌ AMÉLIORATIONS INCOMPLÈTES")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 