"""
Script de test pour l'application modulaire
"""
import os
import sys
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Tester les imports des modules"""
    try:
        logger.info("Test des imports...")
        
        # Test des imports de base
        from config import Config
        logger.info("✓ Config importé avec succès")
        
        # Test des connecteurs de base de données
        from database.mysql_connector import mysql_connector
        logger.info("✓ MySQL connector importé avec succès")
        
        from database.redis_connector import redis_connector
        logger.info("✓ Redis connector importé avec succès")
        
        # Test des services
        from services.auth_service import auth_service
        logger.info("✓ Auth service importé avec succès")
        
        from services.subscription_service import subscription_service
        logger.info("✓ Subscription service importé avec succès")
        
        from services.scraping_service import scraping_service
        logger.info("✓ Scraping service importé avec succès")
        
        # Test des routes
        from routes.auth_routes import auth_bp
        logger.info("✓ Auth routes importé avec succès")
        
        from routes.subscription_routes import subscription_bp
        logger.info("✓ Subscription routes importé avec succès")
        
        from routes.dashboard_routes import dashboard_bp
        logger.info("✓ Dashboard routes importé avec succès")
        
        from routes.health_routes import health_bp
        logger.info("✓ Health routes importé avec succès")
        
        from routes.scraping_routes import scraping_routes
        logger.info("✓ Scraping routes importé avec succès")
        
        logger.info("✓ Tous les imports fonctionnent correctement")
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur lors des imports: {e}")
        return False

def test_app_creation():
    """Tester la création de l'application"""
    try:
        logger.info("Test de création de l'application...")
        
        from app_modular import create_app
        app = create_app()
        
        logger.info("✓ Application créée avec succès")
        logger.info(f"✓ Nombre de blueprints enregistrés: {len(app.blueprints)}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur lors de la création de l'application: {e}")
        return False

def main():
    """Fonction principale de test"""
    logger.info("=== Test de l'application modulaire ===")
    
    # Test des imports
    if not test_imports():
        logger.error("❌ Échec des tests d'import")
        return False
    
    # Test de création de l'application
    if not test_app_creation():
        logger.error("❌ Échec du test de création d'application")
        return False
    
    logger.info("✅ Tous les tests ont réussi!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 