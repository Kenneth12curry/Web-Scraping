"""
Script de test complet pour l'architecture modulaire
"""
import os
import sys
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_all_modules():
    """Tester tous les modules de l'architecture modulaire"""
    try:
        logger.info("=== Test complet de l'architecture modulaire ===")
        
        # Test des imports de base
        logger.info("1. Test des imports de base...")
        from config import Config
        logger.info("✓ Config importé")
        
        # Test des connecteurs de base de données
        logger.info("2. Test des connecteurs de base de données...")
        from database.mysql_connector import mysql_connector
        logger.info("✓ MySQL connector importé")
        
        from database.redis_connector import redis_connector
        logger.info("✓ Redis connector importé")
        
        # Test des services
        logger.info("3. Test des services...")
        from services.auth_service import auth_service
        logger.info("✓ Auth service importé")
        
        from services.subscription_service import subscription_service
        logger.info("✓ Subscription service importé")
        
        from services.scraping_service import scraping_service
        logger.info("✓ Scraping service importé")
        
        # Test des routes
        logger.info("4. Test des routes...")
        from routes.auth_routes import auth_bp
        logger.info("✓ Auth routes importé")
        
        from routes.subscription_routes import subscription_bp
        logger.info("✓ Subscription routes importé")
        
        from routes.dashboard_routes import dashboard_bp
        logger.info("✓ Dashboard routes importé")
        
        from routes.health_routes import health_bp
        logger.info("✓ Health routes importé")
        
        from routes.scraping_routes import scraping_routes
        logger.info("✓ Scraping routes importé")
        
        # Test des utils
        logger.info("5. Test des utils...")
        from utils.decorators import monitor_request, validate_json
        logger.info("✓ Décorateurs importés")
        
        from utils.validators import validate_email, validate_password
        logger.info("✓ Validateurs importés")
        
        from utils.helpers import generate_secure_token, send_email
        logger.info("✓ Helpers importés")
        
        # Test du middleware
        logger.info("6. Test du middleware...")
        from middleware.monitoring import MonitoringMiddleware, get_metrics
        logger.info("✓ Middleware de monitoring importé")
        
        logger.info("✓ Tous les modules importés avec succès")
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur lors des imports: {e}")
        return False

def test_app_creation():
    """Tester la création de l'application"""
    try:
        logger.info("7. Test de création de l'application...")
        
        from app_modular import create_app
        app = create_app()
        
        logger.info("✓ Application créée avec succès")
        logger.info(f"✓ Nombre de blueprints enregistrés: {len(app.blueprints)}")
        
        # Vérifier les blueprints
        expected_blueprints = ['auth', 'subscription', 'dashboard', 'health']
        for blueprint_name in expected_blueprints:
            if blueprint_name in app.blueprints:
                logger.info(f"✓ Blueprint '{blueprint_name}' enregistré")
            else:
                logger.warning(f"⚠ Blueprint '{blueprint_name}' manquant")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur lors de la création de l'application: {e}")
        return False

def test_validation_functions():
    """Tester les fonctions de validation"""
    try:
        logger.info("8. Test des fonctions de validation...")
        
        from utils.validators import validate_email, validate_password, validate_url
        
        # Test validation email
        is_valid, message = validate_email("test@example.com")
        if is_valid:
            logger.info("✓ Validation email fonctionnelle")
        else:
            logger.error(f"✗ Validation email échouée: {message}")
            return False
        
        # Test validation mot de passe
        is_valid, message = validate_password("Test123!")
        if is_valid:
            logger.info("✓ Validation mot de passe fonctionnelle")
        else:
            logger.error(f"✗ Validation mot de passe échouée: {message}")
            return False
        
        # Test validation URL
        is_valid, message = validate_url("https://example.com")
        if is_valid:
            logger.info("✓ Validation URL fonctionnelle")
        else:
            logger.error(f"✗ Validation URL échouée: {message}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur lors des tests de validation: {e}")
        return False

def main():
    """Fonction principale de test"""
    logger.info("=== Test complet de l'architecture modulaire ===")
    
    # Test des imports
    if not test_all_modules():
        logger.error("❌ Échec des tests d'import")
        return False
    
    # Test de création d'application
    if not test_app_creation():
        logger.error("❌ Échec du test de création d'application")
        return False
    
    # Test des fonctions de validation
    if not test_validation_functions():
        logger.error("❌ Échec des tests de validation")
        return False
    
    logger.info("✅ Tous les tests ont réussi!")
    logger.info("🎉 L'architecture modulaire est complète et fonctionnelle!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 