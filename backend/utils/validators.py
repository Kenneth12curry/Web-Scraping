"""
Validateurs pour l'application
"""
import re
import logging
from urllib.parse import urlparse
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

def validate_email(email: str) -> Tuple[bool, str]:
    """Valider un email"""
    if not email:
        return False, "Email requis"
    
    # Regex pour valider l'email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Format d'email invalide"
    
    return True, "Email valide"

def validate_password(password: str) -> Tuple[bool, str]:
    """Valider un mot de passe"""
    if not password:
        return False, "Mot de passe requis"
    
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    
    if not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    
    if not re.search(r'\d', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    
    return True, "Mot de passe valide"

def validate_username(username: str) -> Tuple[bool, str]:
    """Valider un nom d'utilisateur"""
    if not username:
        return False, "Nom d'utilisateur requis"
    
    if len(username) < 3:
        return False, "Le nom d'utilisateur doit contenir au moins 3 caractères"
    
    if len(username) > 50:
        return False, "Le nom d'utilisateur ne peut pas dépasser 50 caractères"
    
    # Autoriser lettres, chiffres, tirets et underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Le nom d'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores"
    
    return True, "Nom d'utilisateur valide"

def validate_url(url: str) -> Tuple[bool, str]:
    """Valider une URL"""
    if not url:
        return False, "URL requise"
    
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            # Essayer avec https://
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                parsed = urlparse(url)
        
        if not parsed.scheme or not parsed.netloc:
            return False, "URL invalide"
        
        return True, "URL valide"
        
    except Exception as e:
        logger.error(f"Erreur lors de la validation de l'URL {url}: {e}")
        return False, "URL invalide"

def validate_subscription_plan(plan: str) -> Tuple[bool, str]:
    """Valider un plan d'abonnement"""
    valid_plans = ['free', 'basic', 'pro', 'enterprise']
    
    if not plan:
        return False, "Plan d'abonnement requis"
    
    if plan not in valid_plans:
        return False, f"Plan invalide. Plans autorisés: {', '.join(valid_plans)}"
    
    return True, "Plan valide"

def validate_request_limit(limit: int) -> Tuple[bool, str]:
    """Valider une limite de requêtes"""
    if not isinstance(limit, int):
        return False, "La limite doit être un nombre entier"
    
    if limit < 1:
        return False, "La limite doit être supérieure à 0"
    
    if limit > 10000:
        return False, "La limite ne peut pas dépasser 10000"
    
    return True, "Limite valide"

def validate_scraping_params(params: Dict[str, Any]) -> Tuple[bool, str]:
    """Valider les paramètres de scraping"""
    if not params:
        return False, "Paramètres requis"
    
    # Valider l'URL
    url = params.get('url')
    is_valid_url, url_message = validate_url(url)
    if not is_valid_url:
        return False, url_message
    
    # Valider max_articles
    max_articles = params.get('max_articles', 20)
    if not isinstance(max_articles, int) or max_articles < 1 or max_articles > 100:
        return False, "max_articles doit être un nombre entre 1 et 100"
    
    # Valider method
    method = params.get('method', 'scrapedo')
    valid_methods = ['scrapedo', 'selenium', 'playwright', 'requests']
    if method not in valid_methods:
        return False, f"Méthode invalide. Méthodes autorisées: {', '.join(valid_methods)}"
    
    return True, "Paramètres valides"

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Nettoyer et sanitizer un texte d'entrée"""
    if not text:
        return ""
    
    # Limiter la longueur
    if len(text) > max_length:
        text = text[:max_length]
    
    # Supprimer les caractères dangereux
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<.*?>', '', text)  # Supprimer les balises HTML
    
    # Échapper les caractères spéciaux
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    return text.strip()

def validate_token_format(token: str) -> Tuple[bool, str]:
    """Valider le format d'un token"""
    if not token:
        return False, "Token requis"
    
    # Vérifier la longueur minimale
    if len(token) < 32:
        return False, "Token trop court"
    
    # Vérifier qu'il ne contient que des caractères hexadécimaux
    if not re.match(r'^[a-fA-F0-9]+$', token):
        return False, "Format de token invalide"
    
    return True, "Token valide" 