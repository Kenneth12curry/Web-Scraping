import os
from datetime import timedelta
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(override=True)

class Config:
    """Configuration de l'application Flask"""
    
    # Configuration Flask
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Configuration CORS
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5173', 
        'http://localhost:8080'
    ]
    
    # Configuration API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    SCRAPEDO_API_KEY = os.getenv("SCRAPEDO_API_KEY")
    
    # Configuration Base de données
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stats.db')
    
    # Configuration Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'app.log')
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Configuration Rate Limiting
    RATE_LIMIT_DEFAULT = ["200 per day", "50 per hour"]
    RATE_LIMIT_LOGIN = "5 per minute"
    RATE_LIMIT_SCRAPING = "10 per minute"
    
    # Configuration Scraping
    SCRAPING_TIMEOUT = 60
    SCRAPING_MAX_ARTICLES = 50
    SCRAPING_MAX_PAGES = 3
    
    # Configuration Sécurité
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Validation des identifiants
    @classmethod
    def validate_credentials(cls):
        """Valider que les identifiants sont configurés"""
        if not cls.ADMIN_USERNAME or not cls.ADMIN_PASSWORD:
            return False
        return True
    
    # Configuration Serveur
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8080))
    DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    # Configuration Environnement
    ENV = os.getenv('FLASK_ENV', 'production')
    
    @classmethod
    def is_production(cls):
        """Vérifier si on est en production"""
        return cls.ENV == 'production'
    
    @classmethod
    def is_development(cls):
        """Vérifier si on est en développement"""
        return cls.ENV == 'development'

# Configuration par environnement
class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    ENV = 'production'
    
    # En production, exiger des identifiants sécurisés
    @classmethod
    def validate_credentials(cls):
        if not cls.ADMIN_USERNAME or not cls.ADMIN_PASSWORD:
            raise ValueError("Les identifiants admin doivent être configurés en production")
        if cls.ADMIN_PASSWORD == 'admin123':
            raise ValueError("Le mot de passe par défaut n'est pas autorisé en production")
        return True

# Configuration par défaut
config = DevelopmentConfig if Config.is_development() else ProductionConfig 