"""
Routes du dashboard
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
import sys
import os

# Ajouter le répertoire parent au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from database.mysql_connector import mysql_connector
from services.subscription_service import subscription_service

logger = logging.getLogger(__name__)

# Créer le blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Obtenir les statistiques du dashboard"""
    try:
        current_user = get_jwt_identity()
        
        # Obtenir les statistiques de l'utilisateur
        query = """
            SELECT 
                COUNT(*) as total_requests,
                COUNT(DISTINCT DATE(timestamp)) as active_days,
                AVG(CASE WHEN status_code = 200 THEN 1 ELSE 0 END) * 100 as success_rate
            FROM api_usage 
            WHERE user_id = %s 
            AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """
        stats_result = mysql_connector.execute_query(query, (current_user,))
        
        # Obtenir les statistiques de scraping
        scraping_query = """
            SELECT 
                COUNT(*) as total_scraping,
                SUM(articles_count) as total_articles,
                AVG(articles_count) as avg_articles_per_scraping
            FROM scraping_history 
            WHERE user_id = %s 
            AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """
        scraping_stats = mysql_connector.execute_query(scraping_query, (current_user,))
        
        # Obtenir le statut de l'abonnement
        subscription_status = subscription_service.get_subscription_status(current_user)
        
        # Préparer la réponse
        stats = stats_result[0] if stats_result else {
            'total_requests': 0,
            'active_days': 0,
            'success_rate': 0
        }
        
        scraping = scraping_stats[0] if scraping_stats else {
            'total_scraping': 0,
            'total_articles': 0,
            'avg_articles_per_scraping': 0
        }
        
        return jsonify({
            'success': True,
            'stats': {
                'requests': stats,
                'scraping': scraping,
                'subscription': subscription_status
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

@dashboard_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """Obtenir les analytics détaillées"""
    try:
        current_user = get_jwt_identity()
        
        # Analytics des 7 derniers jours
        query = """
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as requests,
                COUNT(DISTINCT endpoint) as unique_endpoints,
                AVG(CASE WHEN status_code = 200 THEN 1 ELSE 0 END) * 100 as success_rate
            FROM api_usage 
            WHERE user_id = %s 
            AND timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """
        analytics = mysql_connector.execute_query(query, (current_user,))
        
        # Top des domaines scrapés
        domains_query = """
            SELECT 
                domain,
                COUNT(*) as count
            FROM api_usage 
            WHERE user_id = %s 
            AND domain IS NOT NULL
            AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY domain
            ORDER BY count DESC
            LIMIT 10
        """
        top_domains = mysql_connector.execute_query(domains_query, (current_user,))
        
        return jsonify({
            'success': True,
            'analytics': {
                'daily_stats': analytics,
                'top_domains': top_domains
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des analytics: {e}")
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500 