"""Fonctions helpers utilitaires"""

import os
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, urljoin, quote_plus
import re
from database.mysql_connector import mysql_connector
from config import Config
from flask_jwt_extended import create_access_token

logger = logging.getLogger(__name__)


def generate_secure_token(length: int = 32) -> str:
    """Générer un token sécurisé"""
    return secrets.token_hex(length)


def extract_domain_from_url(url: str) -> str:
    """Extraire le domaine d'une URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return "unknown"


def clean_text(text: str) -> str:
    """Nettoyer un texte"""
    if not text:
        return ""

    # Supprimer les espaces multiples
    text = re.sub(r"\s+", " ", text)

    # Supprimer les caractères de contrôle
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    return text.strip()


def truncate_text(text: str, max_length: int = 500) -> str:
    """Tronquer un texte à une longueur maximale"""
    if not text or len(text) <= max_length:
        return text

    # Tronquer et ajouter "..."
    return text[: max_length - 3] + "..."


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
    safe_name = re.sub(r"[^\w\-_\.]", "_", filename)

    # Limiter la longueur
    if len(safe_name) > 100:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[: 100 - len(ext)] + ext

    return safe_name


def get_user_agent() -> str:
    """Obtenir un User-Agent réaliste"""
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


def build_url(base_url: str, path: str) -> str:
    """Construire une URL complète"""
    return urljoin(base_url, path)


def encode_url_params(params: Dict[str, Any]) -> str:
    """Encoder des paramètres d'URL"""
    return "&".join(
        [f"{key}={quote_plus(str(value))}" for key, value in params.items()]
    )


def parse_http_headers(headers_str: str) -> Dict[str, str]:
    """Parser des en-têtes HTTP"""
    headers = {}
    if headers_str:
        for line in headers_str.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()
    return headers


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Récupérer un utilisateur par son email"""
    query = "SELECT id, username, email FROM users WHERE email = %s"
    result = mysql_connector.execute_query(query, (email,))
    return result[0] if result else None


def create_password_reset_token(user_id: int) -> Optional[str]:
    """Créer un token de réinitialisation de mot de passe"""
    token = generate_secure_token()
    expires_at = datetime.now() + timedelta(
        minutes=Config.RESET_TOKEN_EXPIRATION_MINUTES
    )
    query = (
        "INSERT INTO password_resets (user_id, token, expires_at) VALUES (%s, %s, %s)"
    )
    try:
        mysql_connector.execute_query(query, (user_id, token, expires_at))
        return token
    except Exception as e:
        logger.error(f"Erreur lors de la création du token de réinitialisation: {e}")
        return None


def verify_password_reset_token(token: str) -> Optional[int]:
    """Vérifier un token de réinitialisation de mot de passe"""
    query = "SELECT user_id FROM password_resets WHERE token = %s AND expires_at > NOW() AND used = FALSE"
    result = mysql_connector.execute_query(query, (token,))
    return result[0]["user_id"] if result else None


def update_user_password(user_id: int, new_password: str) -> bool:
    """Mettre à jour le mot de passe d'un utilisateur"""
    from werkzeug.security import (
        generate_password_hash,
    )  # Import here to avoid circular dependency

    hashed_password = generate_password_hash(new_password)
    query = "UPDATE users SET password_hash = %s WHERE id = %s"
    try:
        mysql_connector.execute_query(query, (hashed_password, user_id))
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du mot de passe: {e}")
        return False


def mark_token_as_used(token: str) -> bool:
    """Marquer un token de réinitialisation comme utilisé"""
    query = "UPDATE password_resets SET used = TRUE WHERE token = %s"
    try:
        mysql_connector.execute_query(query, (token,))
        return True
    except Exception as e:
        logger.error(f"Erreur lors du marquage du token comme utilisé: {e}")
        return False
