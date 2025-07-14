"""
Routes d'authentification
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import os
import sys
import json
from datetime import datetime
import re
from database.mysql_connector import mysql_connector
from utils.validators import validate_email
from utils.helpers import (
    get_user_by_email,
    create_password_reset_token,
    verify_password_reset_token,
    update_user_password,
    mark_token_as_used,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config import Config

logger = logging.getLogger(__name__)

# Créer le blueprint
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Données JSON requises"}), 400

        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        first_name = data.get("first_name", None)
        last_name = data.get("last_name", None)
        company = data.get("company", None)

        if not username or not password:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Nom d'utilisateur et mot de passe requis",
                    }
                ),
                400,
            )

        if len(username) < 3:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Le nom d'utilisateur doit contenir au moins 3 caractères",
                    }
                ),
                400,
            )

        if len(password) < 6:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Le mot de passe doit contenir au moins 6 caractères",
                    }
                ),
                400,
            )

        if not email:
            return jsonify({"success": False, "message": "Email requis"}), 400

        is_valid_email, email_validation_message = validate_email(email)
        if not is_valid_email:
            return jsonify({"success": False, "message": email_validation_message}), 400

        # Vérifier si l'utilisateur existe déjà
        check_query = "SELECT id FROM users WHERE username = %s OR email = %s"
        existing_user = mysql_connector.execute_query(check_query, (username, email))

        if existing_user:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Nom d'utilisateur ou email déjà utilisé",
                    }
                ),
                400,
            )

        # Créer l'utilisateur
        password_hash = generate_password_hash(password)
        insert_query = """
            INSERT INTO users (username, email, password_hash, first_name, last_name, company, subscription_plan, requests_limit, requests_used, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'free', 30, 0, NOW())
        """
        mysql_connector.execute_query(
            insert_query,
            (username, email, password_hash, first_name, last_name, company),
        )

        return (
            jsonify({"success": True, "message": "Utilisateur créé avec succès"}),
            201,
        )

    except Exception as e:
        import traceback

        logger.error(f"Erreur lors de l'inscription: {e}\n{traceback.format_exc()}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """Connexion d'un utilisateur"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Données JSON requises"}), 400

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Nom d'utilisateur et mot de passe requis",
                    }
                ),
                400,
            )

        # Récupérer l'utilisateur
        query = "SELECT username, email, password_hash, subscription_plan as role FROM users WHERE username = %s"
        user_data = mysql_connector.execute_query(query, (username,))

        if not user_data:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Nom d'utilisateur ou mot de passe incorrect",
                    }
                ),
                401,
            )

        user = user_data[0]

        # Vérifier le mot de passe
        if not check_password_hash(user["password_hash"], password):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Nom d'utilisateur ou mot de passe incorrect",
                    }
                ),
                401,
            )

        # Créer le token JWT
        access_token = create_access_token(identity=username)

        # Enregistrer la connexion dans login_history
        try:
            # Récupérer l'ID utilisateur
            user_id_query = "SELECT id FROM users WHERE username = %s"
            user_id_data = mysql_connector.execute_query(user_id_query, (username,))
            user_id = user_id_data[0]["id"] if user_id_data else None
            if user_id:
                ip_address = request.remote_addr or ""
                user_agent = request.headers.get("User-Agent", "")
                # Optionnel: géolocalisation ou parsing user_agent
                insert_query = """
                    INSERT INTO login_history (user_id, ip_address, device, status)
                    VALUES (%s, %s, %s, %s)
                """
                mysql_connector.execute_query(
                    insert_query, (user_id, ip_address, user_agent, "success")
                )
        except Exception as log_exc:
            logger.warning(
                f"Impossible d'enregistrer l'historique de connexion: {log_exc}"
            )

        # Obtenir le statut de l'abonnement (simplifié)
        subscription_status = {
            "plan": user["role"],
            "requests_limit": 100,
            "requests_used": 0,
        }

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Connexion réussie",
                    "access_token": access_token,
                    "user": {
                        "username": user["username"],
                        "email": user["email"],
                        "role": user["role"],
                        "subscription": subscription_status,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur lors de la connexion: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Déconnexion d'un utilisateur"""
    try:
        # En JWT, la déconnexion se fait côté client en supprimant le token
        # Ici on peut ajouter une logique de blacklist si nécessaire
        return jsonify({"success": True, "message": "Déconnexion réussie"}), 200
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


# ===== NOUVELLES ROUTES POUR LA GESTION DU COMPTE =====


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Obtenir le profil de l'utilisateur connecté"""
    try:
        current_user = get_jwt_identity()

        # Récupérer les informations du profil
        query = """
            SELECT 
                username,
                email,
                role,
                created_at,
                last_login,
                subscription_plan,
                monthly_requests_used,
                monthly_requests_limit,
                subscription_end_date,
                first_name,
                last_name
            FROM users 
            WHERE username = %s
        """
        user_data = mysql_connector.execute_query(query, (current_user,))

        if not user_data or len(user_data) == 0:
            return jsonify({"success": False, "message": "Utilisateur non trouvé"}), 404

        user = user_data[0]

        return (
            jsonify(
                {
                    "success": True,
                    "profile": {
                        "username": user.get("username"),
                        "email": user.get("email"),
                        "role": user.get("role"),
                        "created_at": (
                            user.get("created_at").isoformat()
                            if user.get("created_at")
                            else None
                        ),
                        "last_login": (
                            user.get("last_login").isoformat()
                            if user.get("last_login")
                            else None
                        ),
                        "subscription_plan": user.get("subscription_plan", "free"),
                        "monthly_requests_used": user.get("monthly_requests_used", 0),
                        "monthly_requests_limit": user.get(
                            "monthly_requests_limit", 30
                        ),
                        "subscription_end_date": (
                            user.get("subscription_end_date").isoformat()
                            if user.get("subscription_end_date")
                            else None
                        ),
                        "first_name": user.get("first_name"),
                        "last_name": user.get("last_name"),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur lors de la récupération du profil: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Mettre à jour le profil de l'utilisateur"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()

        # Validation des données
        if not data or "email" not in data:
            return jsonify({"success": False, "message": "Email requis"}), 400

        email = data["email"]
        is_valid, email_msg = validate_email(email)
        if not is_valid:
            return jsonify({"success": False, "message": email_msg}), 400

        # Vérifier si l'email existe déjà
        check_query = "SELECT id FROM users WHERE email = %s AND username != %s"
        existing_user = mysql_connector.execute_query(
            check_query, (email, current_user)
        )

        if existing_user and len(existing_user) > 0:
            return (
                jsonify({"success": False, "message": "Cet email est déjà utilisé"}),
                400,
            )

        # Mettre à jour le profil
        update_query = "UPDATE users SET email = %s WHERE username = %s"
        mysql_connector.execute_query(update_query, (email, current_user))

        return (
            jsonify({"success": True, "message": "Profil mis à jour avec succès"}),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du profil: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """Changer le mot de passe de l'utilisateur"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()

        # Validation des données
        if not data or "current_password" not in data or "new_password" not in data:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Ancien et nouveau mot de passe requis",
                    }
                ),
                400,
            )

        current_password = data["current_password"]
        new_password = data["new_password"]

        # Validation du nouveau mot de passe
        if len(new_password) < 8:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Le nouveau mot de passe doit contenir au moins 8 caractères",
                    }
                ),
                400,
            )

        # Vérifier l'ancien mot de passe
        user_query = "SELECT password_hash FROM users WHERE username = %s"
        user_data = mysql_connector.execute_query(user_query, (current_user,))

        if not user_data or len(user_data) == 0:
            return jsonify({"success": False, "message": "Utilisateur non trouvé"}), 404

        stored_hash = user_data[0]["password_hash"]

        if not check_password_hash(current_password, stored_hash):
            return (
                jsonify({"success": False, "message": "Ancien mot de passe incorrect"}),
                400,
            )

        # Hasher et sauvegarder le nouveau mot de passe
        new_hash = generate_password_hash(new_password)
        update_query = "UPDATE users SET password_hash = %s WHERE username = %s"
        mysql_connector.execute_query(update_query, (new_hash, current_user))

        return (
            jsonify({"success": True, "message": "Mot de passe changé avec succès"}),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur lors du changement de mot de passe: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@auth_bp.route("/api-config", methods=["GET"])
@jwt_required()
def get_api_config():
    """Obtenir la configuration API de l'utilisateur"""
    try:
        current_user = get_jwt_identity()

        # Récupérer les clés API de l'utilisateur (si stockées)
        query = """
            SELECT 
                scrapedo_api_key,
                groq_api_key
            FROM users 
            WHERE username = %s
        """
        user_data = mysql_connector.execute_query(query, (current_user,))

        if not user_data or len(user_data) == 0:
            return jsonify({"success": False, "message": "Utilisateur non trouvé"}), 404

        user = user_data[0]

        return (
            jsonify(
                {
                    "success": True,
                    "config": {
                        "has_scrapedo": bool(user.get("scrapedo_api_key")),
                        "has_groq": bool(user.get("groq_api_key")),
                        "scrapedo_token": (
                            user.get("scrapedo_api_key")[:10] + "..."
                            if user.get("scrapedo_api_key")
                            else None
                        ),
                        "groq_token": (
                            user.get("groq_api_key")[:10] + "..."
                            if user.get("groq_api_key")
                            else None
                        ),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la config API: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@auth_bp.route("/api-config", methods=["POST"])
@jwt_required()
def update_api_config():
    """Mettre à jour la configuration API de l'utilisateur"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()

        # Validation des données
        scrapedo_key = data.get("scrapedo", "").strip()
        groq_key = data.get("groq", "").strip()

        # Mettre à jour les clés API
        update_query = """
            UPDATE users 
            SET scrapedo_api_key = %s, groq_api_key = %s 
            WHERE username = %s
        """
        mysql_connector.execute_query(
            update_query,
            (
                scrapedo_key if scrapedo_key else None,
                groq_key if groq_key else None,
                current_user,
            ),
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Configuration API mise à jour avec succès",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la config API: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@auth_bp.route("/export-data", methods=["GET"])
@jwt_required()
def export_user_data():
    """Exporter les données d'utilisation de l'utilisateur"""
    try:
        current_user = get_jwt_identity()

        # Récupérer l'ID utilisateur
        user_query = "SELECT id FROM users WHERE username = %s"
        user_data = mysql_connector.execute_query(user_query, (current_user,))

        if not user_data or len(user_data) == 0:
            return jsonify({"success": False, "message": "Utilisateur non trouvé"}), 404

        user_id = user_data[0]["id"]

        # Statistiques d'utilisation
        usage_stats_query = """
            SELECT 
                COUNT(*) as total_requests,
                COUNT(CASE WHEN status_code = 200 THEN 1 END) as successful_requests,
                COUNT(CASE WHEN status_code != 200 THEN 1 END) as failed_requests,
                AVG(response_time) as avg_response_time,
                MIN(timestamp) as first_request,
                MAX(timestamp) as last_request
            FROM api_usage 
            WHERE user_id = %s
        """
        usage_stats = mysql_connector.execute_query(usage_stats_query, (user_id,))

        # Top domaines utilisés
        top_domains_query = """
            SELECT 
                domain,
                COUNT(*) as count,
                AVG(response_time) as avg_time
            FROM api_usage 
            WHERE user_id = %s AND domain IS NOT NULL
            GROUP BY domain
            ORDER BY count DESC
            LIMIT 10
        """
        top_domains = mysql_connector.execute_query(top_domains_query, (user_id,))

        # Historique des requêtes récentes
        recent_requests_query = """
            SELECT 
                endpoint,
                method,
                status_code,
                response_time,
                domain,
                timestamp,
                error_message
            FROM api_usage 
            WHERE user_id = %s 
            ORDER BY timestamp DESC
            LIMIT 50
        """
        recent_requests = mysql_connector.execute_query(
            recent_requests_query, (user_id,)
        )

        # Historique de scraping
        scraping_history_query = """
            SELECT 
                url,
                status,
                articles_count,
                processing_time,
                timestamp,
                error_message
            FROM scraping_history 
            WHERE user_id = %s 
            ORDER BY timestamp DESC
            LIMIT 20
        """
        scraping_history = mysql_connector.execute_query(
            scraping_history_query, (user_id,)
        )

        # Préparer les données d'export
        export_data = {
            "export_date": datetime.now().isoformat(),
            "user_id": user_id,
            "username": current_user,
            "usage_stats": (
                usage_stats[0]
                if usage_stats and len(usage_stats) > 0
                else {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "avg_response_time": 0,
                    "first_request": None,
                    "last_request": None,
                }
            ),
            "top_domains": top_domains or [],
            "recent_requests": recent_requests or [],
            "scraping_history": scraping_history or [],
        }

        return jsonify({"success": True, "data": export_data}), 200

    except Exception as e:
        import traceback

        logger.error(
            f"Erreur lors de l'export des données: {e}\n{traceback.format_exc()}"
        )
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@auth_bp.route("/delete-account", methods=["POST"])
@jwt_required()
def delete_account():
    """Supprimer le compte de l'utilisateur"""
    try:
        username = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "Données JSON requises"}), 400

        password = data.get("password")
        confirmation = data.get("confirmation")

        if not password:
            return jsonify({"success": False, "message": "Mot de passe requis"}), 400

        if confirmation != "DELETE":
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Confirmation invalide. Tapez DELETE pour confirmer",
                    }
                ),
                400,
            )

        # Supprimer le compte
        # Remplacer par la logique de suppression de compte si existante, sinon lever une erreur explicite
        return (
            jsonify(
                {"success": False, "message": "Suppression de compte non implémentée"}
            ),
            501,
        )

    except Exception as e:
        logger.error(f"Erreur lors de la suppression du compte: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """Demande de réinitialisation de mot de passe"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Données JSON requises"}), 400

        email = data.get("email")
        if not email:
            return jsonify({"success": False, "message": "Email requis"}), 400

        # Vérifier si l'utilisateur existe
        user = get_user_by_email(email)
        if not user or not user.get("id"):
            # Pour des raisons de sécurité, ne pas révéler si l'email existe
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Si cet email existe, un lien de réinitialisation a été envoyé",
                    }
                ),
                200,
            )

        # Créer le token de réinitialisation
        token = create_password_reset_token(user["id"])
        if not token:
            return (
                jsonify(
                    {"success": False, "message": "Erreur lors de la création du token"}
                ),
                500,
            )

        # TODO: Envoyer l'email avec le token
        # Pour l'instant, on retourne le token (en production, envoyer par email)

        # Envoyer l'email avec le token
        from services.email_service import email_service

        reset_url = f"{Config.FRONTEND_URL}/reset-password?token={token}"
        email_sent, email_message = email_service.send_password_reset_email(
            email, user["username"], reset_url
        )

        if email_sent:
            logger.info(f"Lien de réinitialisation envoye a {email}")
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Si cet email existe, un lien de réinitialisation a été envoyé",
                    }
                ),
                200,
            )
        else:
            logger.error(
                f"Erreur lors de l'envoi de l'email de réinitialisation: {email_message}"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Erreur lors de l'envoi de l'email de réinitialisation",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Erreur lors de la demande de réinitialisation: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Réinitialisation du mot de passe"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Données JSON requises"}), 400

        token = data.get("token")
        new_password = data.get("new_password")

        if not token or not new_password:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Token et nouveau mot de passe requis",
                    }
                ),
                400,
            )

        if len(new_password) < 6:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Le mot de passe doit contenir au moins 6 caractères",
                    }
                ),
                400,
            )

        # Réinitialiser le mot de passe
        user_id = verify_password_reset_token(token)
        if not user_id:
            return (
                jsonify({"success": False, "message": "Token invalide ou expiré"}),
                400,
            )
        success = update_user_password(user_id, new_password)
        if success:
            mark_token_as_used(token)
            return (
                jsonify({"success": True, "message": "Mot de passe réinitialisé"}),
                200,
            )
        else:
            return (
                jsonify(
                    {"success": False, "message": "Erreur lors de la réinitialisation"}
                ),
                400,
            )

    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@auth_bp.route("/verify-reset-token", methods=["POST"])
def verify_reset_token():
    """Vérifier un token de réinitialisation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Données JSON requises"}), 400

        token = data.get("token")
        if not token:
            return jsonify({"success": False, "message": "Token requis"}), 400

        # Vérifier le token
        user_id = verify_password_reset_token(token)

        if user_id:
            return (
                jsonify({"success": True, "message": "Token valide", "valid": True}),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Token invalide ou expiré",
                        "valid": False,
                    }
                ),
                200,
            )

    except Exception as e:
        logger.error(f"Erreur lors de la vérification du token: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@auth_bp.route("/login-history", methods=["GET"])
@jwt_required()
def get_login_history():
    """Obtenir l'historique de connexion de l'utilisateur"""
    try:
        current_user = get_jwt_identity()
        # Récupérer l'ID utilisateur
        user_query = "SELECT id FROM users WHERE username = %s"
        user_data = mysql_connector.execute_query(user_query, (current_user,))
        if not user_data:
            return jsonify({"success": False, "message": "Utilisateur non trouvé"}), 404
        user_id = user_data[0]["id"]
        # Vérifier si la table login_history existe
        try:
            mysql_connector.execute_query("DESCRIBE login_history")
            table_exists = True
        except Exception:
            table_exists = False
        if not table_exists:
            return jsonify({"success": True, "history": []}), 200
        # Récupérer l'historique de connexion
        query = """
            SELECT id, timestamp, ip_address, location, device, status
            FROM login_history
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT 20
        """
        history = mysql_connector.execute_query(query, (user_id,))
        return jsonify({"success": True, "history": history}), 200
    except Exception as e:
        logger.error(
            f"Erreur lors de la récupération de l'historique de connexion: {e}"
        )
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500
