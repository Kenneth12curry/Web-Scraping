"""
Fonctions helpers utilitaires
"""
import os
import sys
import logging
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, urljoin, quote_plus
import re

logger = logging.getLogger(__name__)

def generate_secure_token(length: int = 32) -> str:
    """Générer un token sécurisé"""
    return secrets.token_hex(length)

def hash_password(password: str) -> str:
    """Hasher un mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_password_reset_token(user_id: int) -> str:
    """Créer un token de réinitialisation de mot de passe"""
    # Combiner user_id, timestamp et secret
    timestamp = str(int(datetime.now().timestamp()))
    secret = os.getenv('RESET_TOKEN_SECRET', 'reset-secret-key')
    
    # Créer le token
    token_data = f"{user_id}:{timestamp}:{secret}"
    token = hashlib.sha256(token_data.encode()).hexdigest()
    
    return token

def verify_password_reset_token(token: str) -> Optional[int]:
    """Vérifier un token de réinitialisation de mot de passe"""
    try:
        # Récupérer les informations du token depuis la base de données
        from database.mysql_connector import mysql_connector
        
        query = """
            SELECT user_id, reset_token_expires 
            FROM users 
            WHERE reset_token = %s AND reset_token_expires > NOW()
        """
        result = mysql_connector.execute_query(query, (token,))
        
        if result and len(result) > 0:
            return result[0]['user_id']
        
        return None
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du token: {e}")
        return None

def send_email(to_email: str, subject: str, body: str, html_body: str = None) -> bool:
    """Envoyer un email"""
    try:
        from config import Config
        
        # Configuration SMTP
        smtp_config = Config.SMTP_CONFIG
        
        # Créer le message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_config['username']
        msg['To'] = to_email
        
        # Ajouter le contenu texte
        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # Ajouter le contenu HTML si fourni
        if html_body:
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
        
        # Connexion SMTP
        if smtp_config['use_ssl']:
            server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'])
        else:
            server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
            if smtp_config['use_tls']:
                server.starttls()
        
        # Authentification
        server.login(smtp_config['username'], smtp_config['password'])
        
        # Envoi
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email envoyé avec succès à {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi d'email à {to_email}: {e}")
        return False

def send_password_reset_email(email: str, username: str, reset_url: str) -> bool:
    """Envoyer un email de réinitialisation de mot de passe"""
    subject = "Réinitialisation de votre mot de passe - Findata IA"
    
    # Corps texte
    body = f"""
    Bonjour {username},
    
    Vous avez demandé la réinitialisation de votre mot de passe.
    
    Cliquez sur le lien suivant pour réinitialiser votre mot de passe :
    {reset_url}
    
    Ce lien expire dans 30 minutes.
    
    Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
    
    Cordialement,
    L'équipe Findata IA
    """
    
    # Corps HTML
    html_body = f"""
    <html>
    <body>
        <h2>Réinitialisation de votre mot de passe</h2>
        <p>Bonjour {username},</p>
        <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
        <p><a href="{reset_url}" style="background-color: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Réinitialiser le mot de passe</a></p>
        <p>Ce lien expire dans 30 minutes.</p>
        <p>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</p>
        <p>Cordialement,<br>L'équipe Findata IA</p>
    </body>
    </html>
    """
    
    return send_email(email, subject, body, html_body)

def extract_domain_from_url(url: str) -> str:
    """Extraire le domaine d'une URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return 'unknown'

def clean_text(text: str) -> str:
    """Nettoyer un texte"""
    if not text:
        return ""
    
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    
    # Supprimer les caractères de contrôle
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    return text.strip()

def truncate_text(text: str, max_length: int = 500) -> str:
    """Tronquer un texte à une longueur maximale"""
    if not text or len(text) <= max_length:
        return text
    
    # Tronquer et ajouter "..."
    return text[:max_length-3] + "..."

def format_date(date: datetime) -> str:
    """Formater une date"""
    return date.strftime("%Y-%m-%d %H:%M:%S")

def calculate_processing_time(start_time: float) -> str:
    """Calculer le temps de traitement"""
    end_time = datetime.now().timestamp()
    duration = end_time - start_time
    return f"{duration:.2f}s"

def get_file_extension(filename: str) -> str:
    """Obtenir l'extension d'un fichier"""
    return os.path.splitext(filename)[1].lower()

def is_valid_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Vérifier si un fichier a une extension autorisée"""
    extension = get_file_extension(filename)
    return extension in allowed_extensions

def create_safe_filename(filename: str) -> str:
    """Créer un nom de fichier sécurisé"""
    # Supprimer les caractères dangereux
    safe_name = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Limiter la longueur
    if len(safe_name) > 100:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:100-len(ext)] + ext
    
    return safe_name

def get_user_agent() -> str:
    """Obtenir un User-Agent réaliste"""
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def build_url(base_url: str, path: str) -> str:
    """Construire une URL complète"""
    return urljoin(base_url, path)

def encode_url_params(params: Dict[str, Any]) -> str:
    """Encoder des paramètres d'URL"""
    return "&".join([f"{key}={quote_plus(str(value))}" for key, value in params.items()])

def parse_http_headers(headers_str: str) -> Dict[str, str]:
    """Parser des en-têtes HTTP"""
    headers = {}
    if headers_str:
        for line in headers_str.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
    return headers

def get_user_by_email(email):
    """Récupérer un utilisateur par son email"""
    from database.mysql_connector import mysql_connector
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    import logging
    logger = logging.getLogger(__name__)
    try:
        conn = mysql_connector._get_connection()
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
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'utilisateur par email: {e}")
        return None

def create_password_reset_token(user_id):
    from database.mysql_connector import mysql_connector
    from datetime import datetime, timedelta
    import secrets
    import logging
    logger = logging.getLogger(__name__)
    try:
        conn = mysql_connector._get_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)
        cursor.execute('DELETE FROM password_reset_tokens WHERE user_id = %s AND used = FALSE', (user_id,))
        cursor.execute('''
            INSERT INTO password_reset_tokens (user_id, token, expires_at)
            VALUES (%s, %s, %s)
        ''', (user_id, token, expires_at))
        conn.commit()
        logger.info(f"Token de réinitialisation créé pour l'utilisateur {user_id}")
        return token
    except Exception as e:
        logger.error(f"Erreur lors de la création du token de réinitialisation: {e}")
        return None

def verify_password_reset_token(token):
    from database.mysql_connector import mysql_connector
    from datetime import datetime
    import logging
    logger = logging.getLogger(__name__)
    try:
        conn = mysql_connector._get_connection()
        if not conn:
            return None
        cursor = conn.cursor()
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
        if used or expires_at < datetime.now():
            return None
        return user_id
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du token: {e}")
        return None

def mark_token_as_used(token):
    from database.mysql_connector import mysql_connector
    import logging
    logger = logging.getLogger(__name__)
    try:
        conn = mysql_connector._get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute('UPDATE password_reset_tokens SET used = TRUE WHERE token = %s', (token,))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Erreur lors du marquage du token comme utilisé: {e}")
        return False

def update_user_password(user_id, new_password):
    from database.mysql_connector import mysql_connector
    from werkzeug.security import generate_password_hash
    import logging
    logger = logging.getLogger(__name__)
    try:
        conn = mysql_connector._get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        password_hash = generate_password_hash(new_password)
        cursor.execute('UPDATE users SET password_hash = %s WHERE id = %s', (password_hash, user_id))
        conn.commit()
        logger.info(f"Mot de passe mis à jour pour l'utilisateur {user_id}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du mot de passe: {e}")
        return False 