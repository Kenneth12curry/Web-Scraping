"""
Routes de scraping
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
import time
from services.scraping_service import scraping_service
from services.subscription_service import subscription_service
from config import Config
from database.mysql_connector import mysql_connector

logger = logging.getLogger(__name__)

scraping_bp = Blueprint("scraping", __name__)


@scraping_bp.route("/extract", methods=["POST"])
@jwt_required()
def extract_articles():
    """Scraping multi-fallback avec résumé IA"""
    try:
        current_user = get_jwt_identity()

        # Vérifier les limites d'abonnement
        subscription_check = subscription_service.check_subscription_limits(
            current_user
        )
        if not subscription_check["allowed"]:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": subscription_check["reason"],
                        "subscription_info": subscription_check,
                    }
                ),
                429,
            )

        data = request.get_json()
        logger.info(f"Données reçues pour le scraping: {data}")
        if not data:
            return jsonify({"success": False, "message": "Données JSON requises"}), 400

        site_url = data.get("url")
        method = data.get("method", "scrapedo")
        max_articles = data.get("max_articles", 20)
        max_ia_summaries = data.get("max_ia_summaries", 10)  # Added this line

        if not site_url:
            return jsonify({"success": False, "message": "URL requise"}), 400

        # Utiliser la logique complète du ScrapingService
        result = scraping_service.extract_articles_complete(
            site_url=site_url,
            method=method,
            max_articles=max_articles,
            max_ia_summaries=max_ia_summaries,  # Passed this parameter
        )

        if not result["success"]:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Erreur lors du scraping: {result.get('error', 'Erreur inconnue')}",
                    }
                ),
                500,
            )

        # Récupérer l'ID utilisateur à partir du username
        user_query = "SELECT id FROM users WHERE username = %s"
        user_data = mysql_connector.execute_query(user_query, (current_user,))
        if not user_data:
            return jsonify({"success": False, "message": "Utilisateur non trouvé"}), 404
        user_id = user_data[0]["id"]
        # Logger le scraping avec l'ID utilisateur
        scraping_service.log_scraping_history(
            user_id, site_url, method, result["total_articles"], "success"
        )

        # Incrémenter le compteur de requêtes
        subscription_service.increment_request_usage(current_user)

        # Préparer la réponse avec des informations détaillées
        response_data = {
            "success": True,
            "articles": result["articles"],
            "total_articles": result["total_articles"],
            "method_used": result["method_used"],
            "domain": result["domain"],
            "feedback": result["feedback"],
            "processing_time": result["processing_time"],
            "articles_with_summaries": result["articles_with_summaries"],
            "subscription_info": subscription_check,
        }

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Erreur lors du scraping: {e}")
        return jsonify({"success": False, "message": "Erreur lors du scraping"}), 500


def scraping_routes(app):
    app.register_blueprint(scraping_bp, url_prefix="/api/scraping")
