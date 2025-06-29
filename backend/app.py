from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash, generate_password_hash
import os
import requests
from bs4 import BeautifulSoup, Tag
from dotenv import load_dotenv
import json
from urllib.parse import urljoin, quote_plus, urlparse
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import redis
from functools import wraps
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from playwright.sync_api import sync_playwright
from langchain_groq import ChatGroq
import re
import logging.handlers
import sys
from typing import Optional, Tuple, Any, Dict, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import hashlib

# Prometheus monitoring
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Sentry error tracking
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Créer le dossier logs s'il n'existe pas
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configuration du logging avancé
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'  # Ajouter l'encodage UTF-8
        ),
        logging.StreamHandler(sys.stdout)  # Utiliser stdout au lieu de stderr
    ]
)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv(override=True)

# Initialisation de Sentry
SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN and SENTRY_DSN != 'your_sentry_dsn_here' and SENTRY_DSN.strip():
    try:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
            environment=os.getenv('FLASK_ENV', 'development')
        )
        logger.info("Sentry initialise pour le tracking des erreurs")
    except Exception as e:
        logger.warning(f"Sentry ne peut pas etre initialise: {e}")
else:
    logger.info("Sentry non configure - tracking des erreurs desactive")

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Configuration CORS pour permettre les requêtes depuis les frontends
CORS(app, origins=['http://localhost:3000', 'http://localhost:5173', 'http://localhost:8080'])

jwt = JWTManager(app)

# Configuration du rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Métriques Prometheus
REQUEST_COUNT = Counter('http_requests_total', 'Total des requêtes HTTP', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Latence des requêtes HTTP', ['method', 'endpoint'])
SCRAPING_REQUESTS = Counter('scraping_requests_total', 'Total des requêtes de scraping', ['method', 'status'])
API_USAGE = Counter('api_usage_total', 'Utilisation de l\'API', ['endpoint', 'user_id'])

# Variables globales
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SCRAPEDO_API_KEY = os.getenv("SCRAPEDO_API_KEY")
HAS_GROQ = bool(GROQ_API_KEY)
HAS_SCRAPEDO = bool(SCRAPEDO_API_KEY and len(SCRAPEDO_API_KEY) > 10)

# Configuration utilisateur (en production, utiliser une base de données)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

# Validation des identifiants
if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    logger.warning("ATTENTION: Identifiants admin non configures dans .env - Utilisation des valeurs par defaut")
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    logger.warning("SECURITE: Changez IMMEDIATEMENT ces identifiants en production !")

ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD)

# Configuration MySQL
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
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

# Configuration SMTP pour l'envoi d'emails
SMTP_CONFIG = {
    'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
    'port': int(os.getenv('SMTP_PORT', 587)),
    'username': os.getenv('SMTP_USERNAME', ''),
    'password': os.getenv('SMTP_PASSWORD', ''),
    'use_tls': os.getenv('SMTP_USE_TLS', 'True').lower() == 'true',
    'use_ssl': os.getenv('SMTP_USE_SSL', 'False').lower() == 'true'
}

# Variables globales pour les connexions
mysql_connection = None
redis_client = None

def get_mysql_connection():
    """Obtenir une connexion MySQL avec gestion d'erreur"""
    global mysql_connection
    try:
        if mysql_connection is None:
            mysql_connection = mysql.connector.connect(**MYSQL_CONFIG)
            logger.info("Connexion MySQL etablie")
        elif not mysql_connection.is_connected():
            mysql_connection = mysql.connector.connect(**MYSQL_CONFIG)
            logger.info("Reconnexion MySQL etablie")
        return mysql_connection
    except Error as e:
        logger.error(f"Erreur de connexion MySQL: {e}")
        mysql_connection = None
        return None

def get_redis_connection():
    """Obtenir une connexion Redis avec gestion d'erreur"""
    global redis_client
    try:
        if redis_client is None:
            redis_client = redis.Redis(**REDIS_CONFIG)
            # Test de connexion
            redis_client.ping()
            logger.info("Connexion Redis etablie")
        return redis_client
    except Exception as e:
        logger.error(f"Erreur de connexion Redis: {e}")
        return None

# Base de données MySQL pour les statistiques
def init_db():
    """Initialiser la base de données MySQL"""
    try:
        conn = get_mysql_connection()
        if not conn:
            logger.error("Impossible de se connecter a MySQL")
            return False
            
        cursor = conn.cursor()
        
        # Table pour les utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE,
                role VARCHAR(50) DEFAULT 'user',
                subscription_plan VARCHAR(50) DEFAULT 'free',
                subscription_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subscription_end_date TIMESTAMP NULL,
                monthly_requests_used INT DEFAULT 0,
                monthly_requests_limit INT DEFAULT 30,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Table pour l'utilisation de l'API
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_usage (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                endpoint VARCHAR(255) NOT NULL,
                status_code INT NOT NULL,
                domain VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Table pour l'historique des scraping
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                url TEXT NOT NULL,
                method VARCHAR(50) NOT NULL,
                articles_count INT DEFAULT 0,
                status VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Table pour les tokens de réinitialisation de mot de passe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_token (token),
                INDEX idx_user_id (user_id),
                INDEX idx_expires_at (expires_at),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Insérer l'utilisateur admin s'il n'existe pas
        cursor.execute('SELECT id FROM users WHERE username = %s', (ADMIN_USERNAME,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, role)
                VALUES (%s, %s, %s, %s)
            ''', (ADMIN_USERNAME, ADMIN_PASSWORD_HASH, 'admin@findata.com', 'admin'))
            logger.info(f"Utilisateur admin créé: {ADMIN_USERNAME}")
        
        conn.commit()
        logger.info("Base de données MySQL initialisée avec succès")
        return True
    except Error as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données MySQL: {e}")
        return False

def get_user_by_username(username):
    """Récupérer un utilisateur par son nom d'utilisateur"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        # Essayer d'abord avec les colonnes d'abonnement
        try:
            cursor.execute('''
                SELECT id, username, password_hash, email, role, 
                       subscription_plan, subscription_start_date, subscription_end_date,
                       monthly_requests_used, monthly_requests_limit
                FROM users WHERE username = %s
            ''', (username,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': int(row[0]) if row[0] is not None else None,
                    'username': str(row[1]) if row[1] is not None else '',
                    'password_hash': str(row[2]) if row[2] is not None else '',
                    'email': str(row[3]) if row[3] is not None else None,
                    'role': str(row[4]) if row[4] is not None else 'user',
                    'subscription_plan': str(row[5]) if row[5] is not None else 'free',
                    'subscription_start_date': row[6],
                    'subscription_end_date': row[7],
                    'monthly_requests_used': int(row[8]) if row[8] is not None else 0,
                    'monthly_requests_limit': int(row[9]) if row[9] is not None else 30
                }
        except Error as e:
            if "Unknown column" in str(e):
                # Les colonnes d'abonnement n'existent pas, utiliser une requête simple
                logger.info("Colonnes d'abonnement non trouvées, utilisation du fallback")
                cursor.execute('''
                    SELECT id, username, password_hash, email, role
                    FROM users WHERE username = %s
                ''', (username,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'id': int(row[0]) if row[0] is not None else None,
                        'username': str(row[1]) if row[1] is not None else '',
                        'password_hash': str(row[2]) if row[2] is not None else '',
                        'email': str(row[3]) if row[3] is not None else None,
                        'role': str(row[4]) if row[4] is not None else 'user',
                        'subscription_plan': 'free',
                        'subscription_start_date': None,
                        'subscription_end_date': None,
                        'monthly_requests_used': 0,
                        'monthly_requests_limit': 30
                    }
            else:
                # Autre erreur, la relancer
                raise e
        
        return None
    except Error as e:
        logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
        return None

def create_user(username, password, email=None):
    """Créer un nouvel utilisateur"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        password_hash = generate_password_hash(password)
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, role)
            VALUES (%s, %s, %s, %s)
        ''', (username, password_hash, email, 'user'))
        
        conn.commit()
        logger.info(f"Nouvel utilisateur créé: {username}")
        return True
    except Error as e:
        logger.error(f"Erreur lors de la création de l'utilisateur: {e}")
        return False

def update_last_login(username):
    """Mettre à jour la dernière connexion d'un utilisateur"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = %s', (username,))
        conn.commit()
        return True
    except Error as e:
        logger.error(f"Erreur lors de la mise à jour de la dernière connexion: {e}")
        return False

def check_subscription_limits(username):
    """Vérifier les limites d'abonnement d'un utilisateur"""
    try:
        user = get_user_by_username(username)
        if not user:
            return {'allowed': False, 'reason': 'Utilisateur non trouvé'}
        
        # Vérifier si l'abonnement est expiré
        if user['subscription_end_date'] and user['subscription_end_date'] < datetime.now():
            return {'allowed': False, 'reason': 'Abonnement expiré'}
        
        # Vérifier les limites de requêtes mensuelles
        if user['monthly_requests_used'] >= user['monthly_requests_limit']:
            return {
                'allowed': False, 
                'reason': f'Limite mensuelle atteinte ({user["monthly_requests_used"]}/{user["monthly_requests_limit"]} requêtes)',
                'used': user['monthly_requests_used'],
                'limit': user['monthly_requests_limit']
            }
        
        return {
            'allowed': True,
            'used': user['monthly_requests_used'],
            'limit': user['monthly_requests_limit'],
            'remaining': user['monthly_requests_limit'] - user['monthly_requests_used'],
            'plan': user['subscription_plan']
        }
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des limites d'abonnement: {e}")
        return {'allowed': False, 'reason': 'Erreur lors de la vérification des limites'}

def increment_request_usage(username):
    """Incrémenter le compteur de requêtes utilisées"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET monthly_requests_used = monthly_requests_used + 1 
            WHERE username = %s
        ''', (username,))
        
        conn.commit()
        return True
    except Error as e:
        logger.error(f"Erreur lors de l'incrémentation du compteur de requêtes: {e}")
        return False

def reset_monthly_usage():
    """Réinitialiser les compteurs mensuels (à exécuter mensuellement)"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET monthly_requests_used = 0')
        conn.commit()
        logger.info("Compteurs mensuels réinitialisés")
        return True
    except Error as e:
        logger.error(f"Erreur lors de la réinitialisation des compteurs: {e}")
        return False

def upgrade_user_subscription(username, plan, requests_limit):
    """Mettre à jour l'abonnement d'un utilisateur"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Calculer la date de fin d'abonnement (1 mois)
        end_date = datetime.now() + timedelta(days=30)
        
        cursor.execute('''
            UPDATE users 
            SET subscription_plan = %s, 
                monthly_requests_limit = %s,
                subscription_start_date = CURRENT_TIMESTAMP,
                subscription_end_date = %s,
                monthly_requests_used = 0
            WHERE username = %s
        ''', (plan, requests_limit, end_date, username))
        
        conn.commit()
        logger.info(f"Abonnement mis à jour pour {username}: {plan} ({requests_limit} requêtes)")
        return True
    except Error as e:
        logger.error(f"Erreur lors de la mise à jour de l'abonnement: {e}")
        return False

def log_api_usage(user_id, endpoint, status_code, domain=None):
    """Enregistrer l'utilisation de l'API"""
    try:
        conn = get_mysql_connection()
        if not conn:
            logger.warning(f"Impossible de logger l'utilisation API - pas de connexion MySQL")
            return False
            
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO api_usage (user_id, endpoint, status_code, domain)
            VALUES (%s, %s, %s, %s)
        ''', (user_id, endpoint, status_code, domain))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de l'utilisation API: {e}")
        return False

def get_user_stats(user_id):
    """Obtenir les statistiques d'un utilisateur"""
    conn = None
    try:
        # Créer une nouvelle connexion locale pour éviter les problèmes de connexion perdue
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        if not conn:
            return {}

        # Statistiques générales
        cursor1 = conn.cursor(buffered=True)
        cursor1.execute('''
            SELECT 
                COUNT(*) as total_requests,
                COUNT(CASE WHEN status_code = 200 THEN 1 END) as successful_requests,
                COUNT(CASE WHEN status_code != 200 THEN 1 END) as failed_requests
            FROM api_usage 
            WHERE user_id = %s
        ''', (user_id,))
        general_stats_row = cursor1.fetchone()
        cursor1.close()
        general_stats = {
            'total_requests': int(general_stats_row[0]) if general_stats_row and general_stats_row[0] is not None else 0,  # type: ignore
            'successful_requests': int(general_stats_row[1]) if general_stats_row and general_stats_row[1] is not None else 0,  # type: ignore
            'failed_requests': int(general_stats_row[2]) if general_stats_row and general_stats_row[2] is not None else 0  # type: ignore
        }

        # Statistiques par endpoint
        cursor2 = conn.cursor(buffered=True)
        cursor2.execute('''
            SELECT 
                endpoint,
                COUNT(*) as count,
                COUNT(CASE WHEN status_code = 200 THEN 1 END) as success_count
            FROM api_usage 
            WHERE user_id = %s
            GROUP BY endpoint
            ORDER BY count DESC
        ''', (user_id,))
        endpoint_stats = []
        for row in cursor2.fetchall():
            endpoint_stats.append({
                'endpoint': str(row[0]) if row[0] is not None else '',  # type: ignore
                'count': int(row[1]) if row[1] is not None else 0,  # type: ignore
                'success_count': int(row[2]) if row[2] is not None else 0  # type: ignore
            })
        cursor2.close()

        # Statistiques de scraping
        cursor3 = conn.cursor(buffered=True)
        cursor3.execute('''
            SELECT 
                COUNT(*) as total_scraping,
                COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_scraping,
                SUM(articles_count) as total_articles
            FROM scraping_history 
            WHERE user_id = %s
        ''', (user_id,))
        scraping_stats_row = cursor3.fetchone()
        cursor3.close()
        scraping_stats = {
            'total_scraping': int(scraping_stats_row[0]) if scraping_stats_row and scraping_stats_row[0] is not None else 0,  # type: ignore
            'successful_scraping': int(scraping_stats_row[1]) if scraping_stats_row and scraping_stats_row[1] is not None else 0,  # type: ignore
            'total_articles': int(scraping_stats_row[2]) if scraping_stats_row and scraping_stats_row[2] is not None else 0  # type: ignore
        }

        # Statistiques par domaine
        cursor4 = conn.cursor(buffered=True)
        cursor4.execute('''
            SELECT 
                domain,
                COUNT(*) as count
            FROM api_usage 
            WHERE user_id = %s AND domain IS NOT NULL
            GROUP BY domain
            ORDER BY count DESC
            LIMIT 10
        ''', (user_id,))
        domain_stats = []
        for row in cursor4.fetchall():
            domain_stats.append({
                'domain': str(row[0]) if row[0] is not None else '',  # type: ignore
                'count': int(row[1]) if row[1] is not None else 0  # type: ignore
            })
        cursor4.close()

        return {
            'general': general_stats,
            'endpoints': endpoint_stats,
            'scraping': scraping_stats,
            'domains': domain_stats
        }
    except Error as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        return {}
    finally:
        # Toujours fermer la connexion locale
        if conn and conn.is_connected():
            conn.close()

def log_scraping_history(user_id, url, method, articles_count, status):
    """Enregistrer l'historique de scraping"""
    try:
        conn = get_mysql_connection()
        if not conn:
            logger.warning(f"Impossible de logger l'historique de scraping - pas de connexion MySQL")
            return False
            
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scraping_history (user_id, url, method, articles_count, status)
            VALUES (%s, %s, %s, %s, %s)
        ''', (user_id, url, method, articles_count, status))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de l'historique de scraping: {e}")
        return False

# Cache Redis pour améliorer les performances
def get_cached_data(key):
    """Récupérer des données du cache Redis"""
    try:
        redis_conn = get_redis_connection()
        if redis_conn:
            data = redis_conn.get(key)
            if data is not None:
                return json.loads(str(data))
            return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du cache: {e}")
    return None

def set_cached_data(key, data, expire_time=3600):
    """Mettre des données en cache Redis"""
    try:
        redis_conn = get_redis_connection()
        if redis_conn:
            redis_conn.setex(key, expire_time, json.dumps(data))
            return True
    except Exception as e:
        logger.error(f"Erreur lors de la mise en cache: {e}")
    return False

# --- SCRAPEDO FUNCTIONS ---
def scrape_with_scrapedo(url: str, params: dict = {}) -> dict:
    """Utilise l'API Scrape.do pour récupérer le contenu d'une page web"""
    if not SCRAPEDO_API_KEY:
        raise ValueError("Token Scrape.do manquant dans le fichier .env")
    
    # Validation de l'URL
    if not url or not url.startswith(('http://', 'https://')):
        raise ValueError("URL invalide")
    
    query = {
        "token": SCRAPEDO_API_KEY,
        "url": quote_plus(url)
    }
    query.update(params)
    full_url = "https://api.scrape.do/?" + "&".join(f"{k}={v}" for k, v in query.items())
    
    try:
        response = requests.get(full_url, timeout=60, headers={
            'User-Agent': 'FinData-IA-MK/1.0'
        })
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return response.json()
        else:
            return {"html": response.text}
    except requests.exceptions.Timeout:
        raise Exception("Timeout lors de la requête Scrape.do")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erreur Scrape.do: {e}")

def get_site_content_professional(url: str) -> str:
    """Récupère le contenu d'un site de manière professionnelle avec Scrape.do"""
    try:
        result = scrape_with_scrapedo(url)
        return result.get('html', '')
    except Exception as e:
        logger.warning(f"Erreur Scrape.do: {e}")
        logger.info("Fallback vers requests standard...")
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            return response.text
        except Exception as e2:
            logger.error(f"Erreur requests: {e2}")
            return ""

def get_site_content_selenium(url: str, max_wait: int = 10) -> str:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(max_wait)
        html = driver.page_source
        return html
    finally:
        driver.quit()

def get_site_content_playwright(url: str, max_wait: int = 10) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=max_wait * 1000)
        page.wait_for_timeout(max_wait * 1000)
        html = page.content()
        browser.close()
        return html

def find_next_page_url(soup, base_url):
    next_selectors = [
        'a[rel="next"]',
        'a.next',
        'a[aria-label*="next"]',
        'a:contains(">")',
        'a:contains("Suivant")',
        'a:contains("Next")',
        'li.next > a',
        'li.pagination-next > a',
    ]
    for selector in next_selectors:
        link = soup.select_one(selector)
        if link and link.get('href'):
            return urljoin(base_url, link['href'])
    for a in soup.find_all('a'):
        txt = a.get_text(strip=True).lower()
        if txt in ('next', 'suivant', '>') and a.get('href'):
            return urljoin(base_url, a['href'])
    return None

# --- AUTHENTICATION ENDPOINTS ---
@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("3 per minute")
def register():
    """Endpoint d'inscription"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données JSON requises'}), 400
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Nom d\'utilisateur et mot de passe requis'}), 400
        
        # Validation basique
        if len(username) < 3:
            return jsonify({'success': False, 'message': 'Le nom d\'utilisateur doit contenir au moins 3 caractères'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
        
        # Créer l'utilisateur
        success = create_user(username, password, email)
        
        if success:
            log_api_usage(username, 'register', 200)
            logger.info(f"Nouvel utilisateur inscrit: {username}")
            return jsonify({
                'success': True,
                'message': 'Inscription réussie ! Vous pouvez maintenant vous connecter.'
            }), 201
        else:
            log_api_usage(username, 'register', 400)
            return jsonify({'success': False, 'message': 'Erreur lors de la création de l\'utilisateur'}), 400
            
    except Exception as e:
        logger.error(f"Erreur lors de l'inscription: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Endpoint de connexion"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données JSON requises'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Nom d\'utilisateur et mot de passe requis'}), 400
        
        # Vérifier d'abord l'utilisateur admin (pour la compatibilité)
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            access_token = create_access_token(identity=username)
            update_last_login(username)
            log_api_usage(username, 'login', 200)
            logger.info(f"Connexion admin réussie: {username}")
            return jsonify({
                'success': True,
                'access_token': access_token,
                'user': {
                    'username': username,
                    'role': 'admin'
                }
            }), 200
        
        # Vérifier dans la base de données des utilisateurs
        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            access_token = create_access_token(identity=username)
            update_last_login(username)
            log_api_usage(username, 'login', 200)
            logger.info(f"Connexion utilisateur réussie: {username}")
            return jsonify({
                'success': True,
                'access_token': access_token,
                'user': {
                    'username': username,
                    'role': user['role'],
                    'email': user['email']
                }
            }), 200
        else:
            log_api_usage(username or 'unknown', 'login', 401)
            logger.warning(f"Tentative de connexion échouée pour l'utilisateur: {username}")
            return jsonify({'success': False, 'message': 'Identifiants invalides'}), 401
    except Exception as e:
        logger.error(f"Erreur lors de la connexion: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Endpoint de déconnexion"""
    try:
        current_user = get_jwt_identity()
        log_api_usage(current_user, 'logout', 200)
        logger.info(f"Déconnexion de l'utilisateur: {current_user}")
        return jsonify({'success': True, 'message': 'Déconnexion réussie'}), 200
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@app.route('/api/auth/forgot-password', methods=['POST'])
@limiter.limit("3 per hour")
def forgot_password():
    """Endpoint pour demander la réinitialisation du mot de passe"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données JSON requises'}), 400
        
        email = data.get('email')
        if not email:
            return jsonify({'success': False, 'message': 'Email requis'}), 400
        
        # Validation basique de l'email
        if '@' not in email or '.' not in email:
            return jsonify({'success': False, 'message': 'Format d\'email invalide'}), 400
        
        # Rechercher l'utilisateur par email
        user = get_user_by_email(email)
        if not user:
            # Pour des raisons de sécurité, ne pas révéler si l'email existe ou non
            logger.info(f"Demande de réinitialisation pour un email inexistant: {email}")
            return jsonify({
                'success': True,
                'message': 'Si cet email existe dans notre base de données, vous recevrez un lien de réinitialisation.'
            }), 200
        
        # Créer un token de réinitialisation
        token = create_password_reset_token(user['id'])
        if not token:
            return jsonify({'success': False, 'message': 'Erreur lors de la création du token'}), 500
        
        # Construire l'URL de réinitialisation
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        reset_url = f"{frontend_url}/reset-password?token={token}"
        
        # Envoyer l'email
        email_sent = send_password_reset_email(email, user['username'], reset_url)
        
        if email_sent:
            log_api_usage(user['username'], 'forgot_password', 200)
            logger.info(f"Demande de réinitialisation traitée pour: {email}")
            return jsonify({
                'success': True,
                'message': 'Si cet email existe dans notre base de données, vous recevrez un lien de réinitialisation.'
            }), 200
        else:
            log_api_usage(user['username'], 'forgot_password', 500)
            return jsonify({'success': False, 'message': 'Erreur lors de l\'envoi de l\'email'}), 500
            
    except Exception as e:
        logger.error(f"Erreur lors de la demande de réinitialisation: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@app.route('/api/auth/reset-password', methods=['POST'])
@limiter.limit("5 per hour")
def reset_password():
    """Endpoint pour réinitialiser le mot de passe avec un token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données JSON requises'}), 400
        
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not token or not new_password:
            return jsonify({'success': False, 'message': 'Token et nouveau mot de passe requis'}), 400
        
        # Validation du mot de passe
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
        
        # Vérifier le token
        user_id = verify_password_reset_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 400
        
        # Mettre à jour le mot de passe
        success = update_user_password(user_id, new_password)
        if not success:
            return jsonify({'success': False, 'message': 'Erreur lors de la mise à jour du mot de passe'}), 500
        
        # Marquer le token comme utilisé
        mark_token_as_used(token)
        
        # Récupérer les informations de l'utilisateur pour le logging
        user = None
        try:
            conn = get_mysql_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('SELECT username FROM users WHERE id = %s', (user_id,))
                row = cursor.fetchone()
                if row and row[0] is not None:
                    user = str(row[0])
        except Exception as e:
            logger.warning(f"Impossible de récupérer le nom d'utilisateur: {e}")
            user = 'unknown'
        
        log_api_usage(user, 'reset_password', 200)
        logger.info(f"Mot de passe réinitialisé avec succès pour l'utilisateur {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Mot de passe réinitialisé avec succès. Vous pouvez maintenant vous connecter.'
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation du mot de passe: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@app.route('/api/auth/verify-reset-token', methods=['POST'])
def verify_reset_token():
    """Endpoint pour vérifier la validité d'un token de réinitialisation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données JSON requises'}), 400
        
        token = data.get('token')
        if not token:
            return jsonify({'success': False, 'message': 'Token requis'}), 400
        
        # Vérifier le token
        user_id = verify_password_reset_token(token)
        if user_id:
            return jsonify({
                'success': True,
                'message': 'Token valide',
                'valid': True
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': 'Token invalide ou expiré',
                'valid': False
            }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du token: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@app.route('/api/subscription/upgrade', methods=['POST'])
@jwt_required()
def upgrade_subscription():
    """Endpoint pour mettre à niveau l'abonnement d'un utilisateur"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'Données JSON requises'}), 400
        
        plan = data.get('plan')
        if not plan or plan not in ['free', 'pro']:
            return jsonify({'success': False, 'message': 'Plan invalide'}), 400
        
        # Définir les limites selon le plan
        plan_limits = {
            'free': 30,
            'pro': 10000
        }
        
        requests_limit = plan_limits.get(plan, 30)
        
        # Mettre à jour l'abonnement
        success = upgrade_user_subscription(current_user, plan, requests_limit)
        
        if success:
            log_api_usage(current_user, 'subscription_upgrade', 200)
            return jsonify({
                'success': True,
                'message': f'Abonnement mis à niveau vers {plan} avec succès',
                'plan': plan,
                'requests_limit': requests_limit
            }), 200
        else:
            log_api_usage(current_user, 'subscription_upgrade', 500)
            return jsonify({'success': False, 'message': 'Erreur lors de la mise à niveau'}), 500
            
    except Exception as e:
        logger.error(f"Erreur lors de la mise à niveau de l'abonnement: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@app.route('/api/subscription/status', methods=['GET'])
@jwt_required()
def get_subscription_status():
    """Endpoint pour obtenir le statut de l'abonnement d'un utilisateur"""
    try:
        current_user = get_jwt_identity()
        
        # Vérifier les limites d'abonnement
        subscription_check = check_subscription_limits(current_user)
        
        # Récupérer les informations détaillées de l'utilisateur
        user = get_user_by_username(current_user)
        
        if user:
            subscription_info = {
                'plan': user['subscription_plan'],
                'used': user['monthly_requests_used'],
                'limit': user['monthly_requests_limit'],
                'remaining': user['monthly_requests_limit'] - user['monthly_requests_used'],
                'subscription_start_date': user['subscription_start_date'],
                'subscription_end_date': user['subscription_end_date'],
                'allowed': subscription_check['allowed']
            }
        else:
            subscription_info = subscription_check
        
        log_api_usage(current_user, 'subscription_status', 200)
        
        return jsonify({
            'success': True,
            'subscription': subscription_info
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut d'abonnement: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

# --- DASHBOARD ENDPOINTS ---
@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Obtenir les statistiques du dashboard"""
    try:
        current_user = get_jwt_identity()
        
        # Statistiques utilisateur
        user_stats = get_user_stats(current_user)
        
        # Récupérer les informations d'abonnement réelles
        user = get_user_by_username(current_user)
        
        # Configuration API
        api_config = {
            'has_scrapedo': HAS_SCRAPEDO,
            'has_groq': HAS_GROQ,
            'scrapedo_token': SCRAPEDO_API_KEY[:10] + '...' if SCRAPEDO_API_KEY else None,
            'groq_token': GROQ_API_KEY[:10] + '...' if GROQ_API_KEY else None
        }
        
        # Informations d'abonnement réelles
        if user:
            subscription = {
                'plan': user['subscription_plan'].capitalize(),
                'api_calls_used': user['monthly_requests_used'],
                'api_calls_limit': user['monthly_requests_limit'],
                'concurrent_calls_used': 0,  # Pas encore implémenté
                'concurrent_calls_limit': 5,  # Pas encore implémenté
                'renew_date': user['subscription_end_date'].strftime('%d.%m.%Y %H:%M') if user['subscription_end_date'] else (datetime.now() + timedelta(days=30)).strftime('%d.%m.%Y %H:%M'),
                'owner': user.get('email', 'diandiallo974@gmail.com')
            }
        else:
            # Fallback si l'utilisateur n'est pas trouvé
            subscription = {
                'plan': 'Free',
                'api_calls_used': user_stats['general']['total_requests'],
                'api_calls_limit': 30,
                'concurrent_calls_used': 0,
                'concurrent_calls_limit': 5,
                'renew_date': (datetime.now() + timedelta(days=30)).strftime('%d.%m.%Y %H:%M'),
                'owner': 'diandiallo974@gmail.com'
            }
        
        log_api_usage(current_user, 'dashboard_stats', 200)
        
        return jsonify({
            'success': True,
            'user_stats': user_stats,
            'api_config': api_config,
            'subscription': subscription
        }), 200
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@app.route('/api/dashboard/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """Obtenir les analytics détaillées pour le dashboard"""
    try:
        current_user = get_jwt_identity()
        
        conn = get_mysql_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erreur de connexion à la base de données'}), 500
            
        cursor = conn.cursor()
        
        # Analytics par domaine
        cursor.execute('''
            SELECT domain, status_code, COUNT(*) as requests_count
            FROM api_usage 
            WHERE user_id = %s AND domain IS NOT NULL
            GROUP BY domain, status_code
            ORDER BY requests_count DESC
        ''', (current_user,))
        
        domain_stats = []
        for row in cursor.fetchall():
            domain_stats.append({
                'domain': str(row[0]) if row[0] is not None else '',  # type: ignore
                'status_code': int(row[1]) if row[1] is not None else 0,  # type: ignore
                'requests_count': int(row[2]) if row[2] is not None else 0  # type: ignore
            })
        
        # Historique des scraping
        cursor.execute('''
            SELECT url, method, articles_count, status, timestamp
            FROM scraping_history 
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT 20
        ''', (current_user,))
        
        scraping_history = []
        for row in cursor.fetchall():
            scraping_history.append({
                'url': str(row[0]) if row[0] is not None else '',  # type: ignore
                'method': str(row[1]) if row[1] is not None else '',  # type: ignore
                'articles_count': int(row[2]) if row[2] is not None else 0,  # type: ignore
                'status': str(row[3]) if row[3] is not None else '',  # type: ignore
                'timestamp': str(row[4]) if row[4] is not None else ''  # type: ignore
            })
        
        log_api_usage(current_user, 'analytics', 200)
        
        return jsonify({
            'success': True,
            'domain_stats': domain_stats,
            'scraping_history': scraping_history
        }), 200
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des analytics: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

# --- SCRAPING ENDPOINTS ---
@app.route('/api/scraping/extract', methods=['POST'])
@limiter.limit("10 per minute")
@jwt_required()
def extract_articles():
    """Scraping multi-fallback (Scrape.do, requests, Selenium, Playwright) + pagination + résumé IA + fallback extraction IA"""
    try:
        current_user = get_jwt_identity()
        
        # Vérifier les limites d'abonnement
        subscription_check = check_subscription_limits(current_user)
        if not subscription_check['allowed']:
            return jsonify({
                'success': False, 
                'message': subscription_check['reason'],
                'subscription_info': subscription_check
            }), 429  # Too Many Requests
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données JSON requises'}), 400
        site_url = data.get('url')
        method = data.get('method', 'scrapedo')
        if not site_url:
            return jsonify({'success': False, 'message': 'URL requise'}), 400
        if not site_url.startswith(('http://', 'https://')):
            site_url = 'https://' + site_url
        try:
            domain = urlparse(site_url).netloc
        except Exception:
            domain = 'unknown'
        articles = []
        url_to_scrape = site_url
        method_used = ''
        feedback = ''
        html_pages = []
        max_articles = data.get('max_articles', 20)
        try:
            max_articles = int(max_articles)
            if max_articles < 1:
                max_articles = 1
            if max_articles > 100:
                max_articles = 100
        except Exception:
            max_articles = 20
        start_time = time.time()
        for page_num in range(5):  # max 5 pages
            html = ""
            # Pipeline de fallback
            try:
                html = get_site_content_professional(url_to_scrape)
                method_used = 'scrapedo'
            except Exception as e1:
                logger.warning(f"Scrape.do échoué: {e1}")
                try:
                    response = requests.get(url_to_scrape, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    response.raise_for_status()
                    html = response.text
                    method_used = 'requests'
                except Exception as e2:
                    logger.warning(f"Requests fallback échoué: {e2}")
                    try:
                        html = get_site_content_selenium(url_to_scrape)
                        method_used = 'selenium'
                    except Exception as e3:
                        logger.warning(f"Selenium fallback échoué: {e3}")
                        try:
                            html = get_site_content_playwright(url_to_scrape)
                            method_used = 'playwright'
                        except Exception as e4:
                            logger.error(f"Playwright fallback échoué: {e4}")
                            feedback = f"Impossible de récupérer le contenu du site: {e4}"
                            html = ""
            if not html:
                break
            html_pages.append(html)
            try:
                soup = BeautifulSoup(html, 'html.parser')
                # Sélecteurs CSS pour trouver les articles
                selectors = [
                    # Sélecteurs génériques
                    'article', 'div.news-item', 'div.post', 'div.blog-post',
                    'li.news-item', 'div.article', 'div.story',
                    # Sélecteurs supplémentaires pour sites tech/actualités
                    'div.news', 'div.actualite', 'div.news-article',
                    'li.article', 'div.entry', 'div.content-article',
                    'section.article', 'div.news-content', 'div.article-content',
                    'div.news-block', 'div.article-block', 'div.post-content',
                    'div.news-summary', 'div.article-summary', 'div.news-excerpt',
                    # Sélecteurs spécifiques pour sites français
                    'div.article-item', 'div.news-card', 'div.article-card',
                    'li.news', 'div.actualite-item', 'div.article-preview',
                    'div.article-teaser', 'div.news-teaser', 'div.article-snippet',
                    # Sélecteurs pour sites d'actualités
                    'div.article-list-item', 'div.news-list-item', 'div.article-entry',
                    'article.article', 'div.article-wrapper', 'div.news-wrapper',
                    # Sélecteurs pour sites de blogs
                    'div.blog-entry', 'div.post-item', 'div.blog-item',
                    'li.blog-post', 'div.blog-article', 'div.post-article'
                ]
                logger.info(f"Page {page_num + 1}: Recherche d'articles avec {len(selectors)} sélecteurs")
                
                # Set pour éviter les doublons
                seen_titles = set()
                
                for selector in selectors:
                    elements = soup.select(selector)
                    logger.info(f"Sélecteur '{selector}': {len(elements)} éléments trouvés")
                    for element in elements[:max_articles]:  # Limiter par page
                        try:
                            title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
                            link_elem = element.find('a')
                            if title_elem:  # Seulement vérifier le titre, pas le lien
                                title = title_elem.get_text(strip=True)
                                
                                # Filtrer les titres trop courts ou non pertinents
                                if len(title) < 10 or title.lower() in ['accueil', 'menu', 'navigation', 'footer', 'boutique', 'services']:
                                    continue
                                
                                # Éviter les doublons
                                title_normalized = title.lower().strip()
                                if title_normalized in seen_titles:
                                    logger.info(f"Titre dupliqué ignoré: {title[:50]}...")
                                    continue
                                seen_titles.add(title_normalized)
                                
                                logger.info(f"Titre trouvé: {title[:50]}...")
                                url = ""
                                if link_elem and isinstance(link_elem, Tag):
                                    href_value = link_elem.get('href')
                                    if href_value:
                                        url = str(href_value)
                                        try:
                                            url = urljoin(url_to_scrape, url)
                                        except Exception:
                                            url = ""
                                if not url:  # Si pas de lien trouvé, utiliser l'URL courante
                                    url = url_to_scrape
                                if title:  # Ajouter l'article si on a au moins un titre
                                    # Amélioration de l'extraction du contenu - Approche plus agressive
                                    content_parts = []
                                    date_str = ""
                                    
                                    # Priorité 1: Paragraphes principaux
                                    paragraphs = element.find_all('p')
                                    for p in paragraphs:
                                        txt = p.get_text(strip=True)
                                        if txt and len(txt) > 15 and txt != title:
                                            # Éviter les doublons
                                            if not any(txt in existing for existing in content_parts):
                                                content_parts.append(txt)
                                    
                                    # Priorité 2: Contenu des divs avec classe spécifique
                                    content_divs = element.find_all('div', class_=lambda x: x and any(keyword in x.lower() for keyword in [
                                        'content', 'text', 'body', 'article', 'post', 'entry', 'description', 'excerpt', 'summary'
                                    ]))
                                    for div in content_divs:
                                        txt = div.get_text(strip=True)
                                        if txt and len(txt) > 30 and txt != title:
                                            if not any(txt in existing for existing in content_parts):
                                                content_parts.append(txt)
                                    
                                    # Priorité 3: Sous-titres et intertitres
                                    subtitles = element.find_all(['h2', 'h3', 'h4', 'h5', 'h6'])
                                    for subtitle in subtitles:
                                        txt = subtitle.get_text(strip=True)
                                        if txt and len(txt) > 10 and txt != title:
                                            if not any(txt in existing for existing in content_parts):
                                                content_parts.append(txt)
                                    
                                    # Priorité 4: Listes (ul, ol)
                                    lists = element.find_all(['ul', 'ol'])
                                    for list_elem in lists:
                                        if isinstance(list_elem, Tag):
                                            items = list_elem.find_all('li')
                                            for item in items:
                                                txt = item.get_text(strip=True)
                                                if txt and len(txt) > 10:
                                                    if not any(txt in existing for existing in content_parts):
                                                        content_parts.append(txt)
                                    
                                    # Priorité 5: Spans avec contenu textuel
                                    spans = element.find_all('span')
                                    for span in spans:
                                        txt = span.get_text(strip=True)
                                        if txt and len(txt) > 20 and txt != title:
                                            if not any(txt in existing for existing in content_parts):
                                                content_parts.append(txt)
                                    
                                    # Priorité 6: Contenu des sections
                                    sections = element.find_all('section')
                                    for section in sections:
                                        txt = section.get_text(strip=True)
                                        if txt and len(txt) > 50 and txt != title:
                                            if not any(txt in existing for existing in content_parts):
                                                content_parts.append(txt)
                                    
                                    # Priorité 7: Contenu des articles imbriqués
                                    nested_articles = element.find_all('article')
                                    for nested_article in nested_articles:
                                        if nested_article != element:  # Éviter la récursion
                                            txt = nested_article.get_text(strip=True)
                                            if txt and len(txt) > 30 and txt != title:
                                                if not any(txt in existing for existing in content_parts):
                                                    content_parts.append(txt)
                                    
                                    # Assembler le contenu
                                    content = '\n\n'.join(content_parts)
                                    
                                    # Nettoyer le contenu
                                    content = re.sub(r'\n{3,}', '\n\n', content)  # Supprimer les sauts de ligne multiples
                                    content = re.sub(r'\s+', ' ', content)  # Normaliser les espaces
                                    content = content.strip()
                                    
                                    # Si le contenu est insuffisant, essayer d'extraire depuis l'URL de l'article
                                    if not content or len(content) < 100:
                                        if url and url != url_to_scrape:
                                            logger.info(f"Contenu insuffisant, tentative d'extraction depuis l'URL: {url}")
                                            full_article = extract_article_from_url(url, url_to_scrape)
                                            if full_article and full_article.get('content'):
                                                content = full_article['content']
                                                # Mettre à jour le titre si meilleur
                                                if full_article.get('title') and len(full_article['title']) > len(title):
                                                    title = full_article['title']
                                                # Mettre à jour la date si disponible
                                                if full_article.get('date'):
                                                    date_str = full_article['date']
                                    
                                    # Vérifier que le contenu est suffisant
                                    if content and len(content) > 30:  # Réduit pour être moins strict
                                        # Ajouter une date si disponible
                                        if not date_str:
                                            date_elem = element.find(['time', 'span.date', 'div.date', 'span.timestamp', 'span.time', 'div.time'])
                                            if date_elem:
                                                date_str = date_elem.get_text(strip=True)
                                                # Nettoyer la date
                                                date_str = re.sub(r'[^\w\s\-/]', '', date_str)
                                        
                                        article_data = {
                                            'title': title,
                                            'url': url,
                                            'content': content
                                        }
                                        
                                        if date_str:
                                            article_data['date'] = date_str
                                        
                                        articles.append(article_data)
                                        logger.info(f"Article ajouté: {title[:50]}... (contenu: {len(content)} chars)")
                                    else:
                                        logger.info(f"Article ignoré (contenu insuffisant): {title[:50]}...")
                            if len(articles) >= max_articles:
                                break
                        except Exception as e:
                            logger.warning(f"Erreur lors de l'extraction d'un article: {e}")
                            continue
                    if len(articles) >= max_articles:
                        break
                if len(articles) >= max_articles:
                    break
                next_url = find_next_page_url(soup, url_to_scrape)
                if not next_url or next_url == url_to_scrape:
                    break
                url_to_scrape = next_url
            except Exception as e:
                logger.error(f"Erreur lors du parsing HTML: {e}")
                break
        # Fallback IA si aucun article trouvé
        if not articles and html_pages:
            logger.info("Aucun article trouvé, fallback extraction IA...")
            logger.info(f"HTML de la première page (premiers 500 caractères): {html_pages[0][:500]}")
            try:
                llm = ChatGroq(model="llama3-8b-8192", temperature=0.0)
                prompt = f"""
Voici le HTML d'une page d'actualité :
---
{html_pages[0][:10000]}
---
Ta mission : extraire tous les articles (titre, url, date, contenu principal) et retourne une liste JSON. Ne génère aucun code, ne donne que les données extraites.
"""
                ia_response = llm.invoke(prompt)
                try:
                    ia_articles = json.loads(ia_response.text() if hasattr(ia_response, 'text') else str(ia_response))
                    if isinstance(ia_articles, list):
                        articles = ia_articles
                        method_used += "+ia-fallback"
                        feedback += "Extraction IA fallback utilisée. "
                except Exception as parse_err:
                    logger.warning(f"Erreur parsing JSON IA fallback: {parse_err}")
                    logger.warning(f"Réponse brute IA fallback: {ia_response}")
                    
                    # Tentative d'extraction JSON depuis le texte (même avec backticks)
                    try:
                        response_text = ia_response.text() if hasattr(ia_response, 'text') else str(ia_response)
                        # Chercher du JSON entre backticks ou dans le texte
                        json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response_text, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                            ia_articles = json.loads(json_str)
                            if isinstance(ia_articles, list):
                                articles = ia_articles
                                method_used += "+ia-fallback"
                                feedback += "Extraction IA fallback utilisée (JSON extrait). "
                        else:
                            # Chercher directement un tableau JSON dans le texte
                            json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
                            if json_match:
                                json_str = json_match.group(0)
                                ia_articles = json.loads(json_str)
                                if isinstance(ia_articles, list):
                                    articles = ia_articles
                                    method_used += "+ia-fallback"
                                    feedback += "Extraction IA fallback utilisée (JSON trouvé). "
                    except Exception as extract_err:
                        logger.warning(f"Échec extraction JSON depuis texte: {extract_err}")
                        feedback += f"IA fallback n'a pas pu extraire les articles."
            except Exception as ia_err:
                logger.error(f"Erreur lors du fallback IA: {ia_err}")
                feedback += f"Erreur IA fallback: {ia_err}"
        # Résumé IA pour chaque article (si pas déjà présent)
        if HAS_GROQ and articles:  # Vérifier que Groq est disponible
            try:
                llm = ChatGroq(model="llama3-8b-8192", temperature=0.0)
                max_resume_articles = min(10, len(articles))  # Limite adaptative
                
                logger.info(f"Génération des résumés IA pour {max_resume_articles} articles...")
                
                for idx, article in enumerate(articles[:max_resume_articles]):
                    if 'resume' not in article or not article.get('resume'):
                        try:
                            # Préparer le contenu pour l'IA
                            content_for_ia = article.get('content', '')
                            if not content_for_ia or len(content_for_ia.strip()) < 50:
                                article['resume'] = "Résumé non disponible (contenu insuffisant)."
                                continue
                            
                            # Limiter la taille du contenu pour éviter les timeouts
                            content_for_ia = content_for_ia[:800]  # Réduit de 1000 à 800
                            
                            prompt = (
                                "Résume ce texte d'actualité en 2-3 phrases claires et synthétiques. "
                                "Ne mets pas de phrase d'introduction comme 'Voici un résumé' ou 'Résumé :'. "
                                "Va directement au contenu du résumé :\n\n"
                                f"{content_for_ia}"
                            )
                            
                            ia_response = llm.invoke(prompt)
                            resume = ia_response.text() if hasattr(ia_response, 'text') else str(ia_response)
                            
                            # Nettoyer le résumé
                            resume = resume.strip()
                            # Supprimer les phrases d'introduction courantes
                            resume = re.sub(r"^(voici un résumé[^:]*:|résumé\s*:)\s*", "", resume, flags=re.IGNORECASE)
                            resume = re.sub(r"^(ce texte parle de|il s'agit de|l'article traite de)\s*", "", resume, flags=re.IGNORECASE)
                            
                            # Vérifier que le résumé n'est pas vide après nettoyage
                            if resume and len(resume.strip()) > 10:
                                article['resume'] = resume[:350] + '...' if len(resume) > 350 else resume
                            else:
                                article['resume'] = "Résumé non disponible (réponse IA invalide)."
                                
                        except Exception as e:
                            logger.warning(f"Erreur résumé IA pour article {idx}: {e}")
                            article['resume'] = "Résumé non disponible (erreur technique)."
                        
                        # Pause plus courte entre les appels IA
                        time.sleep(0.5)  # Réduit de 1s à 0.5s
                
                # Pour les articles restants, ajouter un message explicatif
                for idx in range(max_resume_articles, len(articles)):
                    articles[idx]['resume'] = "Résumé non disponible (limite de traitement atteinte)."
                    
            except Exception as e:
                logger.error(f"Erreur globale lors de la génération des résumés IA: {e}")
                # Ajouter un résumé par défaut pour tous les articles
                for article in articles:
                    if 'resume' not in article or not article.get('resume'):
                        article['resume'] = "Résumé non disponible (service IA indisponible)."
        else:
            # Si Groq n'est pas disponible, ajouter un message explicatif
            for article in articles:
                if 'resume' not in article or not article.get('resume'):
                    article['resume'] = "Résumé non disponible (service IA non configuré)."
        # Logger le scraping
        log_scraping_history(current_user, site_url, method_used, len(articles), 'success')
        logger.info(f"Scraping terminé avec succès: {len(articles)} articles extraits via {method_used}")
        
        # Incrémenter le compteur de requêtes utilisées
        increment_request_usage(current_user)
        
        log_api_usage(current_user, 'scraping_extract', 200, domain)
        
        # Préparer la réponse avec des informations détaillées
        response_data = {
            'success': True,
            'articles': articles,
            'total_articles': len(articles),
            'method_used': method_used,
            'domain': domain,
            'feedback': feedback,
            'processing_time': f"{time.time() - start_time:.2f}s",
            'articles_with_summaries': sum(1 for a in articles if a.get('resume') and 'non disponible' not in a.get('resume', '')),
            'subscription_info': subscription_check
        }
        
        return jsonify(response_data), 200
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de requête lors du scraping: {e}")
        return jsonify({'success': False, 'message': f'Erreur de connexion: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Erreur lors du scraping: {e}")
        log_scraping_history(current_user, site_url, method, 0, f'error: {str(e)}')
        log_api_usage(current_user, 'scraping_extract', 500, domain)
        return jsonify({'success': False, 'message': 'Erreur lors du scraping'}), 500

# --- HEALTH CHECK ---
@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de santé de l'API"""
    try:
        # Vérifier la base de données
        conn = get_mysql_connection()
        if not conn:
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': 'Impossible de se connecter à MySQL'
            }), 500
            
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()  # Récupérer le résultat
        cursor.close()
        
        # Vérifier que le résultat est valide
        if result:
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'services': {
                    'database': 'ok',
                    'scrapedo': HAS_SCRAPEDO,
                    'groq': HAS_GROQ
                },
                'version': '1.0.0'
            }), 200
        else:
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': 'Test de base de données échoué'
            }), 500
    except Exception as e:
        logger.error(f"Erreur lors du health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

# Middleware pour collecter les métriques Prometheus
@app.before_request
def before_request():
    # Stocker le temps de début dans g (contexte Flask)
    from flask import g
    g.start_time = time.time()

@app.after_request
def after_request(response):
    # Récupérer le temps de début depuis g
    from flask import g
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        REQUEST_LATENCY.labels(method=request.method, endpoint=request.endpoint).observe(duration)
        REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint, status=response.status_code).inc()
    return response

# Endpoint pour les métriques Prometheus
@app.route('/api/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# Gestionnaire d'erreurs global
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Endpoint non trouvé'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erreur interne du serveur: {error}")
    return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

def get_user_by_email(email):
    """Récupérer un utilisateur par son email"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash, email, role FROM users WHERE email = %s', (email,))
        row = cursor.fetchone()
        
        if row:
            return {
                'id': int(row[0]) if row[0] is not None else None,
                'username': str(row[1]) if row[1] is not None else '',
                'password_hash': str(row[2]) if row[2] is not None else '',
                'email': str(row[3]) if row[3] is not None else None,
                'role': str(row[4]) if row[4] is not None else 'user'
            }
        return None
    except Error as e:
        logger.error(f"Erreur lors de la récupération de l'utilisateur par email: {e}")
        return None

def create_password_reset_token(user_id):
    """Créer un token de réinitialisation de mot de passe"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        # Générer un token sécurisé
        token = secrets.token_urlsafe(32)
        
        # Expiration dans 1 heure
        expires_at = datetime.now() + timedelta(hours=1)
        
        # Supprimer les anciens tokens non utilisés pour cet utilisateur
        cursor.execute('DELETE FROM password_reset_tokens WHERE user_id = %s AND used = FALSE', (user_id,))
        
        # Insérer le nouveau token
        cursor.execute('''
            INSERT INTO password_reset_tokens (user_id, token, expires_at)
            VALUES (%s, %s, %s)
        ''', (user_id, token, expires_at))
        
        conn.commit()
        logger.info(f"Token de réinitialisation créé pour l'utilisateur {user_id}")
        return token
    except Error as e:
        logger.error(f"Erreur lors de la création du token de réinitialisation: {e}")
        return None

def verify_password_reset_token(token):
    """Vérifier un token de réinitialisation de mot de passe"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        # Vérifier le token
        cursor.execute('''
            SELECT user_id, expires_at, used 
            FROM password_reset_tokens 
            WHERE token = %s
        ''', (token,))
        
        row = cursor.fetchone()
        if not row:
            return None
            
        user_id = int(row[0]) if row[0] is not None else None
        expires_at = row[1]
        used = bool(row[2])
        
        # Vérifier si le token est expiré ou déjà utilisé
        if used or expires_at < datetime.now():
            return None
            
        return user_id
    except Error as e:
        logger.error(f"Erreur lors de la vérification du token: {e}")
        return None

def mark_token_as_used(token):
    """Marquer un token comme utilisé"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        cursor.execute('UPDATE password_reset_tokens SET used = TRUE WHERE token = %s', (token,))
        conn.commit()
        return True
    except Error as e:
        logger.error(f"Erreur lors du marquage du token comme utilisé: {e}")
        return False

def update_user_password(user_id, new_password):
    """Mettre à jour le mot de passe d'un utilisateur"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        password_hash = generate_password_hash(new_password)
        
        cursor.execute('UPDATE users SET password_hash = %s WHERE id = %s', (password_hash, user_id))
        conn.commit()
        
        logger.info(f"Mot de passe mis à jour pour l'utilisateur {user_id}")
        return True
    except Error as e:
        logger.error(f"Erreur lors de la mise à jour du mot de passe: {e}")
        return False

def send_password_reset_email(email, username, reset_url):
    """Envoyer un email de réinitialisation de mot de passe"""
    try:
        # Vérifier la configuration SMTP
        if not SMTP_CONFIG['username'] or not SMTP_CONFIG['password']:
            logger.warning("Configuration SMTP manquante - email non envoyé")
            return False
        
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = SMTP_CONFIG['username']
        msg['To'] = email
        msg['Subject'] = 'Réinitialisation de votre mot de passe - FinData'
        
        # Corps du message
        body = f"""
        <html>
        <body>
            <h2>Bonjour {username},</h2>
            <p>Vous avez demandé la réinitialisation de votre mot de passe pour votre compte FinData.</p>
            <p>Cliquez sur le lien ci-dessous pour définir un nouveau mot de passe :</p>
            <p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Réinitialiser mon mot de passe</a></p>
            <p>Ce lien expirera dans 1 heure.</p>
            <p>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</p>
            <br>
            <p>Cordialement,<br>L'équipe FinData</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connexion SMTP
        if SMTP_CONFIG['use_ssl']:
            server = smtplib.SMTP_SSL(SMTP_CONFIG['host'], SMTP_CONFIG['port'])
        else:
            server = smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port'])
            if SMTP_CONFIG['use_tls']:
                server.starttls()
        
        # Authentification
        server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
        
        # Envoi de l'email
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email de réinitialisation envoyé à {email}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {e}")
        return False

def extract_full_article_content(element, title):
    """
    Extrait le contenu complet d'un article avec une approche hiérarchique
    """
    content_parts = []
    
    # 1. Paragraphes principaux (priorité haute)
    paragraphs = element.find_all('p')
    for p in paragraphs:
        txt = p.get_text(strip=True)
        if txt and len(txt) > 15 and txt != title:
            # Éviter les doublons
            if not any(txt in existing for existing in content_parts):
                content_parts.append(txt)
    
    # 2. Contenu des divs avec classe spécifique
    content_divs = element.find_all('div', class_=lambda x: x and any(keyword in x.lower() for keyword in [
        'content', 'text', 'body', 'article', 'post', 'entry', 'description', 'excerpt', 'summary'
    ]))
    for div in content_divs:
        txt = div.get_text(strip=True)
        if txt and len(txt) > 30 and txt != title:
            if not any(txt in existing for existing in content_parts):
                content_parts.append(txt)
    
    # 3. Sous-titres et intertitres
    subtitles = element.find_all(['h2', 'h3', 'h4', 'h5', 'h6'])
    for subtitle in subtitles:
        txt = subtitle.get_text(strip=True)
        if txt and len(txt) > 10 and txt != title:
            if not any(txt in existing for existing in content_parts):
                content_parts.append(txt)
    
    # 4. Listes (ul, ol)
    lists = element.find_all(['ul', 'ol'])
    for list_elem in lists:
        if isinstance(list_elem, Tag):
            items = list_elem.find_all('li')
            for item in items:
                txt = item.get_text(strip=True)
                if txt and len(txt) > 10:
                    if not any(txt in existing for existing in content_parts):
                        content_parts.append(txt)
    
    # 5. Spans avec contenu textuel
    spans = element.find_all('span')
    for span in spans:
        txt = span.get_text(strip=True)
        if txt and len(txt) > 20 and txt != title:
            if not any(txt in existing for existing in content_parts):
                content_parts.append(txt)
    
    # 6. Contenu des sections
    sections = element.find_all('section')
    for section in sections:
        txt = section.get_text(strip=True)
        if txt and len(txt) > 50 and txt != title:
            if not any(txt in existing for existing in content_parts):
                content_parts.append(txt)
    
    # 7. Contenu des articles imbriqués
    nested_articles = element.find_all('article')
    for nested_article in nested_articles:
        if nested_article != element:  # Éviter la récursion
            txt = nested_article.get_text(strip=True)
            if txt and len(txt) > 30 and txt != title:
                if not any(txt in existing for existing in content_parts):
                    content_parts.append(txt)
    
    # Assembler le contenu
    content = '\n\n'.join(content_parts)
    
    # Nettoyer le contenu
    content = re.sub(r'\n{3,}', '\n\n', content)  # Supprimer les sauts de ligne multiples
    content = re.sub(r'\s+', ' ', content)  # Normaliser les espaces
    content = content.strip()
    
    return content

def extract_article_from_url(article_url, base_url):
    """
    Tente d'extraire le contenu complet d'un article depuis son URL
    """
    try:
        # Essayer d'abord avec Scrape.do
        try:
            html = get_site_content_professional(article_url)
        except:
            # Fallback avec requests
            response = requests.get(article_url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            html = response.text
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Chercher le contenu principal de l'article
        content_selectors = [
            'article', 'main', '.article-content', '.post-content', '.entry-content',
            '.content', '.article-body', '.post-body', '.entry-body',
            '.article-text', '.post-text', '.entry-text', '.article-main',
            '.post-main', '.entry-main', '.article-wrapper', '.post-wrapper',
            '.entry-wrapper', '.article-container', '.post-container', '.entry-container'
        ]
        
        content_element = None
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                break
        
        if not content_element:
            # Fallback: chercher le plus grand bloc de texte
            text_blocks = soup.find_all(['div', 'section', 'article'])
            max_length = 0
            for block in text_blocks:
                text = block.get_text(strip=True)
                if len(text) > max_length:
                    max_length = len(text)
                    content_element = block
        
        if content_element:
            # Extraire le titre
            title_elem = content_element.find(['h1', 'h2', 'h3']) or soup.find(['h1', 'h2', 'h3'])
            title = title_elem.get_text(strip=True) if title_elem else "Article"
            
            # Extraire le contenu complet
            content = extract_full_article_content(content_element, title)
            
            # Extraire la date
            date_elem = content_element.find(['time', 'span.date', 'div.date', 'span.timestamp', 'span.time', 'div.time']) or soup.find(['time', 'span.date', 'div.date', 'span.timestamp', 'span.time', 'div.time'])
            date_str = ""
            if date_elem:
                date_str = date_elem.get_text(strip=True)
                date_str = re.sub(r'[^\w\s\-/]', '', date_str)
            
            return {
                'title': title,
                'url': article_url,
                'content': content,
                'date': date_str if date_str else None
            }
    
    except Exception as e:
        logger.warning(f"Erreur lors de l'extraction de l'article {article_url}: {e}")
    
    return None

if __name__ == '__main__':
    # Initialiser la base de données au démarrage
    init_db()
    
    # Démarrer l'application
    app.run(debug=True, host='127.0.0.1', port=8080) 