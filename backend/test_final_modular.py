#!/usr/bin/env python3
"""
Test final de l'architecture modulaire
Vérifie que tous les modules sont correctement importés et fonctionnels
"""
import os
import sys
import importlib
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Tester tous les imports des modules"""
    logger.info("🔍 Test des imports des modules...")
    
    modules_to_test = [
        # Configuration
        'config',
        
        # Base de données
        'database.mysql_connector',
        'database.redis_connector',
        
        # Services
        'services.auth_service',
        'services.subscription_service',
        'services.scraping_service',
        'services.email_service',
        
        # Routes
        'routes.auth_routes',
        'routes.subscription_routes',
        'routes.dashboard_routes',
        'routes.health_routes',
        'routes.scraping_routes',
        
        # Middleware
        'middleware.monitoring',
        'middleware.error_handlers',
        'middleware.security',
        'middleware.rate_limiter',
        
        # Utilitaires
        'utils.decorators',
        'utils.validators',
        'utils.helpers',
    ]
    
    failed_imports = []
    successful_imports = []
    
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            successful_imports.append(module_name)
            logger.info(f"✅ {module_name}")
        except Exception as e:
            failed_imports.append((module_name, str(e)))
            logger.error(f"❌ {module_name}: {e}")
    
    return successful_imports, failed_imports

def test_app_creation():
    """Tester la création de l'application Flask"""
    logger.info("🚀 Test de création de l'application Flask...")
    
    try:
        from app_modular import create_app
        app = create_app()
        
        # Vérifier que l'app a les bonnes propriétés
        assert hasattr(app, 'config'), "L'application doit avoir une configuration"
        assert hasattr(app, 'blueprints'), "L'application doit avoir des blueprints"
        
        logger.info("✅ Application Flask créée avec succès")
        logger.info(f"   - Blueprints enregistrés: {len(app.blueprints)}")
        logger.info(f"   - Configuration chargée: {app.config.get('ENV', 'unknown')}")
        
        return True, app
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de l'application: {e}")
        return False, None

def test_services():
    """Tester les services"""
    logger.info("🔧 Test des services...")
    
    services_tests = [
        ('AuthService', 'services.auth_service', 'auth_service'),
        ('SubscriptionService', 'services.subscription_service', 'subscription_service'),
        ('ScrapingService', 'services.scraping_service', 'scraping_service'),
        ('EmailService', 'services.email_service', 'email_service'),
    ]
    
    failed_services = []
    successful_services = []
    
    for service_name, module_name, instance_name in services_tests:
        try:
            module = importlib.import_module(module_name)
            service_instance = getattr(module, instance_name)
            
            # Vérifier que l'instance existe
            assert service_instance is not None, f"Instance {instance_name} non trouvée"
            
            successful_services.append(service_name)
            logger.info(f"✅ {service_name}")
            
        except Exception as e:
            failed_services.append((service_name, str(e)))
            logger.error(f"❌ {service_name}: {e}")
    
    return successful_services, failed_services

def test_database_connectors():
    """Tester les connecteurs de base de données"""
    logger.info("🗄️ Test des connecteurs de base de données...")
    
    try:
        from database.mysql_connector import mysql_connector
        from database.redis_connector import redis_connector
        
        # Tester MySQL
        try:
            # Test de connexion (peut échouer si MySQL n'est pas démarré)
            mysql_connector.test_connection()
            logger.info("✅ MySQL Connector - Connexion réussie")
        except Exception as e:
            logger.warning(f"⚠️ MySQL Connector - Connexion échouée (normal si MySQL n'est pas démarré): {e}")
        
        # Tester Redis
        try:
            # Test de connexion (peut échouer si Redis n'est pas démarré)
            redis_connector.test_connection()
            logger.info("✅ Redis Connector - Connexion réussie")
        except Exception as e:
            logger.warning(f"⚠️ Redis Connector - Connexion échouée (normal si Redis n'est pas démarré): {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test des connecteurs: {e}")
        return False

def test_configuration():
    """Tester la configuration"""
    logger.info("⚙️ Test de la configuration...")
    
    try:
        from config import Config
        
        # Vérifier les configurations essentielles
        required_configs = [
            'JWT_SECRET_KEY',
            'MYSQL_CONFIG',
            'REDIS_CONFIG',
            'SMTP_CONFIG',
            'GROQ_API_KEY',
            'SCRAPEDO_API_KEY'
        ]
        
        for config_name in required_configs:
            assert hasattr(Config, config_name), f"Configuration {config_name} manquante"
        
        logger.info("✅ Configuration chargée avec succès")
        logger.info(f"   - GROQ disponible: {Config.HAS_GROQ}")
        logger.info(f"   - Scrape.do disponible: {Config.HAS_SCRAPEDO}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test de la configuration: {e}")
        return False

def test_middleware():
    """Tester les middlewares"""
    logger.info("🛡️ Test des middlewares...")
    
    middleware_tests = [
        ('MonitoringMiddleware', 'middleware.monitoring', 'MonitoringMiddleware'),
        ('ErrorHandlerMiddleware', 'middleware.error_handlers', 'ErrorHandlerMiddleware'),
        ('SecurityMiddleware', 'middleware.security', 'SecurityMiddleware'),
        ('RateLimiterMiddleware', 'middleware.rate_limiter', 'RateLimiterMiddleware'),
    ]
    
    failed_middleware = []
    successful_middleware = []
    
    for middleware_name, module_name, class_name in middleware_tests:
        try:
            module = importlib.import_module(module_name)
            middleware_class = getattr(module, class_name)
            
            # Vérifier que la classe existe
            assert middleware_class is not None, f"Classe {class_name} non trouvée"
            
            successful_middleware.append(middleware_name)
            logger.info(f"✅ {middleware_name}")
            
        except Exception as e:
            failed_middleware.append((middleware_name, str(e)))
            logger.error(f"❌ {middleware_name}: {e}")
    
    return successful_middleware, failed_middleware

def test_routes():
    """Tester les routes"""
    logger.info("🛣️ Test des routes...")
    
    routes_tests = [
        ('Auth Routes', 'routes.auth_routes', 'auth_bp'),
        ('Subscription Routes', 'routes.subscription_routes', 'subscription_bp'),
        ('Dashboard Routes', 'routes.dashboard_routes', 'dashboard_bp'),
        ('Health Routes', 'routes.health_routes', 'health_bp'),
    ]
    
    failed_routes = []
    successful_routes = []
    
    for route_name, module_name, blueprint_name in routes_tests:
        try:
            module = importlib.import_module(module_name)
            blueprint = getattr(module, blueprint_name)
            
            # Vérifier que le blueprint existe
            assert blueprint is not None, f"Blueprint {blueprint_name} non trouvé"
            
            successful_routes.append(route_name)
            logger.info(f"✅ {route_name}")
            
        except Exception as e:
            failed_routes.append((route_name, str(e)))
            logger.error(f"❌ {route_name}: {e}")
    
    return successful_routes, failed_routes

def main():
    """Fonction principale de test"""
    logger.info("=" * 60)
    logger.info("🧪 TEST FINAL DE L'ARCHITECTURE MODULAIRE")
    logger.info("=" * 60)
    
    # Résultats des tests
    results = {}
    
    # Test 1: Imports
    logger.info("\n📦 Test 1: Imports des modules")
    successful_imports, failed_imports = test_imports()
    results['imports'] = {
        'successful': len(successful_imports),
        'failed': len(failed_imports),
        'total': len(successful_imports) + len(failed_imports)
    }
    
    # Test 2: Configuration
    logger.info("\n⚙️ Test 2: Configuration")
    config_ok = test_configuration()
    results['configuration'] = config_ok
    
    # Test 3: Connecteurs de base de données
    logger.info("\n🗄️ Test 3: Connecteurs de base de données")
    db_ok = test_database_connectors()
    results['database'] = db_ok
    
    # Test 4: Services
    logger.info("\n🔧 Test 4: Services")
    successful_services, failed_services = test_services()
    results['services'] = {
        'successful': len(successful_services),
        'failed': len(failed_services),
        'total': len(successful_services) + len(failed_services)
    }
    
    # Test 5: Middleware
    logger.info("\n🛡️ Test 5: Middleware")
    successful_middleware, failed_middleware = test_middleware()
    results['middleware'] = {
        'successful': len(successful_middleware),
        'failed': len(failed_middleware),
        'total': len(successful_middleware) + len(failed_middleware)
    }
    
    # Test 6: Routes
    logger.info("\n🛣️ Test 6: Routes")
    successful_routes, failed_routes = test_routes()
    results['routes'] = {
        'successful': len(successful_routes),
        'failed': len(failed_routes),
        'total': len(successful_routes) + len(failed_routes)
    }
    
    # Test 7: Création de l'application
    logger.info("\n🚀 Test 7: Création de l'application Flask")
    app_ok, app = test_app_creation()
    results['app_creation'] = app_ok
    
    # Résumé final
    logger.info("\n" + "=" * 60)
    logger.info("📊 RÉSUMÉ DES TESTS")
    logger.info("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    for test_name, result in results.items():
        if isinstance(result, dict):
            total = result['total']
            successful = result['successful']
            failed = result['failed']
            status = "✅ PASSÉ" if failed == 0 else "❌ ÉCHOUÉ"
            logger.info(f"{test_name:20} | {successful:2}/{total:2} | {status}")
            total_tests += total
            passed_tests += successful
        else:
            status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
            logger.info(f"{test_name:20} | {'':2}/{'':2} | {status}")
            total_tests += 1
            passed_tests += 1 if result else 0
    
    logger.info("-" * 60)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    logger.info(f"TOTAL: {passed_tests}/{total_tests} tests passés ({success_rate:.1f}%)")
    
    if success_rate >= 95:
        logger.info("🎉 ARCHITECTURE MODULAIRE PRÊTE POUR LA PRODUCTION !")
        return True
    elif success_rate >= 80:
        logger.info("⚠️ ARCHITECTURE MODULAIRE PRESQUE PRÊTE - Quelques ajustements nécessaires")
        return False
    else:
        logger.info("❌ ARCHITECTURE MODULAIRE INCOMPLÈTE - Corrections nécessaires")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 