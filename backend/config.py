"""
Configuration centralisée pour l'application Findata IA
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv(override=True)

class Config:
    """Configuration de base"""
    
    # Configuration Flask
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Configuration CORS
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173', 'http://localhost:8080']
    
    # Configuration Rate Limiting
    RATE_LIMIT_DEFAULT = ["200 per day", "50 per hour"]
    RATE_LIMIT_STORAGE = "memory://"
    
    # Configuration Sentry
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    SENTRY_ENVIRONMENT = os.getenv('FLASK_ENV', 'development')
    
    # Configuration API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    SCRAPEDO_API_KEY = os.getenv("SCRAPEDO_API_KEY")
    
    # Validation des API Keys
    HAS_GROQ = bool(GROQ_API_KEY)
    HAS_SCRAPEDO = bool(SCRAPEDO_API_KEY and len(SCRAPEDO_API_KEY) > 10)
    
    # Configuration Admin
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Configuration MySQL
    MYSQL_CONFIG = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', 'root123'),
        'database': os.getenv('MYSQL_DATABASE', 'findata'),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
        'autocommit': True,
        'pool_name': 'mypool',
        'pool_size': 5
    }
    
    # Configuration Redis
    REDIS_CONFIG = {
        'host': os.getenv('REDIS_HOST', 'localhost'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'db': int(os.getenv('REDIS_DB', 0)),
        'decode_responses': True
    }
    
    # Configuration SMTP
    SMTP_CONFIG = {
        'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
        'port': int(os.getenv('SMTP_PORT', 587)),
        'username': os.getenv('SMTP_USERNAME', ''),
        'password': os.getenv('SMTP_PASSWORD', ''),
        'use_tls': os.getenv('SMTP_USE_TLS', 'True').lower() == 'true',
        'use_ssl': os.getenv('SMTP_USE_SSL', 'False').lower() == 'true'
    }
    
    # Configuration Logging
    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    LOG_LEVEL = 'INFO'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Configuration Scraping
    SCRAPING_TIMEOUT = 15
    SCRAPING_MAX_ARTICLES = 100
    SCRAPING_MAX_PAGES = 5
    
    # Configuration IA
    IA_MODEL = "llama3-8b-8192"
    IA_TEMPERATURE = 0.0
    IA_MAX_CONTENT_LENGTH = 800
    
    # Configuration Cache
    CACHE_DEFAULT_EXPIRE = 3600  # 1 heure
    
    # Configuration Monitoring
    PROMETHEUS_ENABLED = True
    
    @classmethod
    def validate_config(cls):
        """Valider la configuration"""
        warnings = []
        
        if cls.ADMIN_PASSWORD == 'admin123':
            warnings.append("ATTENTION: Mot de passe admin par défaut détecté - Changez-le en production !")
        
        if not cls.HAS_GROQ:
            warnings.append("GROQ_API_KEY non configuré - Fonctionnalités IA limitées")
        
        if not cls.HAS_SCRAPEDO:
            warnings.append("SCRAPEDO_API_KEY non configuré - Scraping limité")
        
        return warnings

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
config = DevelopmentConfig if os.getenv('FLASK_ENV') == 'development' else ProductionConfig 

# Configuration SMTP pour l'envoi d'emails (Gmail)
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER', 'votre.email@gmail.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'votre_mot_de_passe_app')
RESET_TOKEN_SECRET = os.getenv('RESET_TOKEN_SECRET', 'reset-secret-key')
RESET_TOKEN_EXPIRATION_MINUTES = int(os.getenv('RESET_TOKEN_EXPIRATION_MINUTES', 30)) 