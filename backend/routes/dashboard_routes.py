"""
Routes du dashboard
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
import sys
import os
import requests
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from database.mysql_connector import mysql_connector
from config import Config

logger = logging.getLogger(__name__)

# Créer le blueprint
dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_dashboard_stats():
    """Obtenir les statistiques du dashboard"""
    try:
        current_user = get_jwt_identity()
        # Récupérer l'ID utilisateur et la limite de scraping
        user_query = "SELECT id, subscription_plan, requests_limit FROM users WHERE username = %s"
        user_data = mysql_connector.execute_query(user_query, (current_user,))
        if not user_data:
            return jsonify({"success": False, "message": "Utilisateur non trouvé"}), 404
        user_id = user_data[0]["id"]
        scraping_limit = user_data[0].get("requests_limit", 30)
        # Obtenir les statistiques de scraping (utilisation du quota)
        scraping_query = """
            SELECT 
                COUNT(*) as total_scraping,
                SUM(articles_count) as total_articles,
                AVG(articles_count) as avg_articles_per_scraping
            FROM scraping_history 
            WHERE user_id = %s 
            AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """
        scraping_stats = mysql_connector.execute_query(scraping_query, (user_id,))
        scraping = (
            scraping_stats[0]
            if scraping_stats and len(scraping_stats) > 0
            else {
                "total_scraping": 0,
                "total_articles": 0,
                "avg_articles_per_scraping": 0,
            }
        )
        # Obtenir les requêtes récentes de scraping
        recent_scraping_query = """
            SELECT 
                url as endpoint,
                method,
                status,
                articles_count,
                processing_time,
                timestamp
            FROM scraping_history 
            WHERE user_id = %s 
            ORDER BY timestamp DESC
            LIMIT 10
        """
        recent_scraping = mysql_connector.execute_query(
            recent_scraping_query, (user_id,)
        )
        return (
            jsonify(
                {
                    "success": True,
                    "user_stats": {
                        "total_scraping": scraping.get("total_scraping", 0) or 0,
                        "scraping_limit": scraping_limit,
                        "total_articles": scraping.get("total_articles", 0) or 0,
                        "avg_articles_per_scraping": scraping.get(
                            "avg_articles_per_scraping", 0
                        )
                        or 0,
                        "recent_scraping": recent_scraping or [],
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@dashboard_bp.route("/analytics", methods=["GET"])
@jwt_required()
def get_analytics():
    """Obtenir les données d'analytics pour le dashboard"""
    try:
        current_user = get_jwt_identity()

        # Récupérer l'ID utilisateur
        user_query = "SELECT id FROM users WHERE username = %s"
        user_data = mysql_connector.execute_query(user_query, (current_user,))

        if not user_data or len(user_data) == 0:
            return jsonify({"success": False, "message": "Utilisateur non trouvé"}), 404

        user_id = user_data[0]["id"]

        # Statistiques des 7 derniers jours
        weekly_stats_query = """
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as requests,
                COUNT(CASE WHEN status_code = 200 THEN 1 END) as success,
                AVG(response_time) as avg_time
            FROM api_usage 
            WHERE user_id = %s 
            AND timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(timestamp)
            ORDER BY date
        """
        weekly_stats = mysql_connector.execute_query(weekly_stats_query, (user_id,))

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
            LIMIT 5
        """
        top_domains = mysql_connector.execute_query(top_domains_query, (user_id,))

        # Activité récente (dernières 24h)
        recent_activity_query = """
            SELECT 
                endpoint,
                method,
                status_code,
                response_time,
                domain,
                timestamp
            FROM api_usage 
            WHERE user_id = %s 
            AND timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY timestamp DESC
            LIMIT 10
        """
        recent_activity = mysql_connector.execute_query(
            recent_activity_query, (user_id,)
        )

        # Statistiques de scraping
        scraping_stats_query = """
            SELECT 
                COUNT(*) as total_scraping,
                COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_scraping,
                AVG(processing_time) as avg_processing_time,
                SUM(articles_count) as total_articles
            FROM scraping_history 
            WHERE user_id = %s
        """
        scraping_stats = mysql_connector.execute_query(scraping_stats_query, (user_id,))

        # Préparer les données pour les graphiques
        chart_data = {"labels": [], "requests": [], "success": []}

        # Remplir les données manquantes avec des zéros
        for i in range(7):
            date = (datetime.now() - timedelta(days=6 - i)).strftime("%Y-%m-%d")
            chart_data["labels"].append(date)

            # Chercher les données existantes
            day_data = None
            if weekly_stats:
                for day in weekly_stats:
                    if day.get("date") and day["date"].strftime("%Y-%m-%d") == date:
                        day_data = day
                        break

            if day_data:
                chart_data["requests"].append(day_data.get("requests", 0))
                chart_data["success"].append(day_data.get("success", 0))
            else:
                chart_data["requests"].append(0)
                chart_data["success"].append(0)

        # Utiliser scraping_stats pour les widgets
        scraping_total = (
            scraping_stats[0]["total_scraping"]
            if scraping_stats and len(scraping_stats) > 0
            else 0
        )
        scraping_success = (
            scraping_stats[0]["successful_scraping"]
            if scraping_stats and len(scraping_stats) > 0
            else 0
        )
        scraping_errors = scraping_total - scraping_success

        # Récupérer les 10 derniers scrapings
        recent_scraping_query = """
            SELECT 
                url,
                status,
                articles_count,
                processing_time,
                timestamp
            FROM scraping_history 
            WHERE user_id = %s 
            ORDER BY timestamp DESC
            LIMIT 10
        """
        recent_scraping = mysql_connector.execute_query(
            recent_scraping_query, (user_id,)
        )

        # Générer les tendances de scraping (succès/erreur par jour sur 7 jours)
        scraping_trends_query = """
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN status != 'success' THEN 1 ELSE 0 END) as error
            FROM scraping_history
            WHERE user_id = %s
            AND timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(timestamp)
            ORDER BY date
        """
        scraping_trends = mysql_connector.execute_query(
            scraping_trends_query, (user_id,)
        )
        # Formater pour le frontend (remplir les jours manquants)
        trends_labels = []
        trends_success = []
        trends_error = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=6 - i)).strftime("%Y-%m-%d")
            trends_labels.append(date)
            day_data = next(
                (
                    d
                    for d in scraping_trends
                    if d.get("date") and d["date"].strftime("%Y-%m-%d") == date
                ),
                None,
            )
            if day_data:
                trends_success.append(day_data.get("success", 0))
                trends_error.append(day_data.get("error", 0))
            else:
                trends_success.append(0)
                trends_error.append(0)

        return (
            jsonify(
                {
                    "success": True,
                    "chart_data": chart_data,
                    "top_domains": top_domains or [],
                    "recent_activity": recent_activity or [],
                    "scraping_stats": (
                        scraping_stats[0]
                        if scraping_stats and len(scraping_stats) > 0
                        else {
                            "total_scraping": 0,
                            "successful_scraping": 0,
                            "avg_processing_time": 0,
                            "total_articles": 0,
                        }
                    ),
                    "stats": {
                        "total_requests": scraping_total,
                        "total_success": scraping_success,
                        "total_errors": scraping_errors,
                    },
                    "recent_scraping": recent_scraping or [],
                    "scraping_trends": {
                        "labels": trends_labels,
                        "success": trends_success,
                        "error": trends_error,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des analytics: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@dashboard_bp.route("/weather", methods=["GET"])
@jwt_required()
def get_weather():
    """Obtenir la météo du Maroc en temps réel"""
    try:
        # Utiliser OpenWeatherMap API pour la météo du Maroc
        # Villes principales du Maroc
        moroccan_cities = [
            {"name": "Casablanca", "lat": 33.5731, "lon": -7.5898},
            {"name": "Rabat", "lat": 34.0209, "lon": -6.8416},
            {"name": "Marrakech", "lat": 31.6295, "lon": -7.9811},
            {"name": "Fès", "lat": 34.0181, "lon": -5.0078},
            {"name": "Agadir", "lat": 30.4278, "lon": -9.5981},
            {"name": "Tanger", "lat": 35.7595, "lon": -5.8340},
            {"name": "Meknès", "lat": 33.8935, "lon": -5.5473},
            {"name": "Oujda", "lat": 34.6814, "lon": -1.9086},
        ]

        # Sélectionner une ville aléatoire ou utiliser Casablanca par défaut
        import random

        selected_city = random.choice(moroccan_cities)

        # API OpenWeatherMap (gratuite)
        api_key = os.getenv("OPENWEATHER_API_KEY", "demo_key")
        if api_key == "demo_key":
            # Données simulées pour le Maroc
            weather_conditions = [
                {
                    "condition": "Ensoleillé",
                    "icon": "fas fa-sun",
                    "temp_range": (18, 28),
                },
                {
                    "condition": "Nuageux",
                    "icon": "fas fa-cloud",
                    "temp_range": (15, 25),
                },
                {
                    "condition": "Pluvieux",
                    "icon": "fas fa-cloud-rain",
                    "temp_range": (12, 22),
                },
                {"condition": "Venteux", "icon": "fas fa-wind", "temp_range": (16, 26)},
            ]

            selected_weather = random.choice(weather_conditions)
            temp_min, temp_max = selected_weather["temp_range"]
            temperature = random.randint(temp_min, temp_max)

            weather_data = {
                "city": selected_city["name"],
                "temperature": temperature,
                "condition": selected_weather["condition"],
                "icon": selected_weather["icon"],
                "humidity": random.randint(40, 80),
                "wind": random.randint(5, 25),
                "feels_like": temperature + random.randint(-2, 2),
                "pressure": random.randint(1010, 1020),
                "visibility": random.randint(8, 12),
                "updated_at": datetime.now().isoformat(),
            }
        else:
            # Vraie API OpenWeatherMap
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": selected_city["lat"],
                "lon": selected_city["lon"],
                "appid": api_key,
                "units": "metric",
                "lang": "fr",
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()

                # Mapper les conditions météo aux icônes
                weather_icons = {
                    "Clear": "fas fa-sun",
                    "Clouds": "fas fa-cloud",
                    "Rain": "fas fa-cloud-rain",
                    "Snow": "fas fa-snowflake",
                    "Thunderstorm": "fas fa-bolt",
                    "Drizzle": "fas fa-cloud-drizzle",
                    "Mist": "fas fa-smog",
                    "Fog": "fas fa-smog",
                    "Haze": "fas fa-smog",
                }

                weather_data = {
                    "city": selected_city["name"],
                    "temperature": round(data["main"]["temp"]),
                    "condition": data["weather"][0]["description"].capitalize(),
                    "icon": weather_icons.get(
                        data["weather"][0]["main"], "fas fa-cloud"
                    ),
                    "humidity": data["main"]["humidity"],
                    "wind": round(data["wind"]["speed"] * 3.6),  # m/s to km/h
                    "feels_like": round(data["main"]["feels_like"]),
                    "pressure": data["main"]["pressure"],
                    "visibility": round(
                        data.get("visibility", 10000) / 1000
                    ),  # m to km
                    "updated_at": datetime.now().isoformat(),
                }
            else:
                # Fallback en cas d'erreur API
                weather_data = {
                    "city": "Casablanca",
                    "temperature": 22,
                    "condition": "Ensoleillé",
                    "icon": "fas fa-sun",
                    "humidity": 65,
                    "wind": 12,
                    "feels_like": 24,
                    "pressure": 1015,
                    "visibility": 10,
                    "updated_at": datetime.now().isoformat(),
                }

        return jsonify({"success": True, "weather": weather_data}), 200

    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la météo: {e}")
        # Données de fallback
        return (
            jsonify(
                {
                    "success": True,
                    "weather": {
                        "city": "Casablanca",
                        "temperature": 22,
                        "condition": "Ensoleillé",
                        "icon": "fas fa-sun",
                        "humidity": 65,
                        "wind": 12,
                        "feels_like": 24,
                        "pressure": 1015,
                        "visibility": 10,
                        "updated_at": datetime.now().isoformat(),
                    },
                }
            ),
            200,
        )


@dashboard_bp.route("/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    """Obtenir les notifications en temps réel de l'utilisateur"""
    try:
        from datetime import datetime

        current_user = get_jwt_identity()
        # Récupérer l'ID utilisateur et les quotas
        user_query = (
            "SELECT id, requests_used, requests_limit FROM users WHERE username = %s"
        )
        user_data = mysql_connector.execute_query(user_query, (current_user,))
        if not user_data:
            return jsonify({"success": False, "message": "Utilisateur non trouvé"}), 404
        user_id = user_data[0]["id"]
        used = user_data[0].get("requests_used", 0)
        limit = user_data[0].get("requests_limit", 30)

        # Récupérer les dernières activités pour créer des notifications
        recent_activity_query = """
            SELECT 
                endpoint,
                method,
                status_code,
                response_time,
                domain,
                timestamp
            FROM api_usage 
            WHERE user_id = %s 
            AND timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY timestamp DESC
            LIMIT 5
        """
        recent_activity = mysql_connector.execute_query(
            recent_activity_query, (user_id,)
        )

        # Récupérer les dernières tâches de scraping
        scraping_activity_query = """
            SELECT 
                url,
                status,
                articles_count,
                processing_time,
                timestamp
            FROM scraping_history 
            WHERE user_id = %s 
            AND timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY timestamp DESC
            LIMIT 3
        """
        scraping_activity = mysql_connector.execute_query(
            scraping_activity_query, (user_id,)
        )

        notifications = []

        # Créer des notifications basées sur l'activité API
        for i, activity in enumerate(recent_activity or []):
            if activity.get("status_code") == 200:
                notification = {
                    "id": f"api_{i}",
                    "type": "success",
                    "title": f"Requête {activity.get('method', 'GET')} réussie",
                    "message": f"API {activity.get('domain', 'générale')} - {activity.get('response_time', 0):.2f}s",
                    "time": format_time_ago(activity.get("timestamp", datetime.now())),
                    "icon": "fas fa-check-circle",
                    "timestamp": activity.get("timestamp", datetime.now()).isoformat(),
                }
            else:
                notification = {
                    "id": f"api_{i}",
                    "type": "error",
                    "title": f"Erreur {activity.get('method', 'GET')}",
                    "message": f"API {activity.get('domain', 'générale')} - {activity.get('status_code', 500)}",
                    "time": format_time_ago(activity.get("timestamp", datetime.now())),
                    "icon": "fas fa-exclamation-triangle",
                    "timestamp": activity.get("timestamp", datetime.now()).isoformat(),
                }
            notifications.append(notification)

        # Créer des notifications basées sur l'activité de scraping
        for i, scraping in enumerate(scraping_activity or []):
            if scraping.get("status") == "success":
                notification = {
                    "id": f"scraping_{i}",
                    "type": "success",
                    "title": f"Scraping terminé",
                    "message": f"{scraping.get('articles_count', 0)} articles extraits de {scraping.get('url', 'URL')}",
                    "time": format_time_ago(scraping.get("timestamp", datetime.now())),
                    "icon": "fas fa-spider",
                    "timestamp": scraping.get("timestamp", datetime.now()).isoformat(),
                }
            else:
                notification = {
                    "id": f"scraping_{i}",
                    "type": "error",
                    "title": f"Échec du scraping",
                    "message": f"Erreur lors de l'extraction de {scraping.get('url', 'URL')}",
                    "time": format_time_ago(scraping.get("timestamp", datetime.now())),
                    "icon": "fas fa-exclamation-triangle",
                    "timestamp": scraping.get("timestamp", datetime.now()).isoformat(),
                }
            notifications.append(notification)

        # Ajouter une notification système si la limite est atteinte
        if used >= limit:
            notifications.insert(
                0,
                {
                    "id": "system_limit",
                    "type": "warning",
                    "title": "Limite gratuite atteinte",
                    "message": "Vous avez atteint la limite de 30 requêtes gratuites. Passez au plan Pro pour continuer à utiliser toutes les fonctionnalités.",
                    "time": "Maintenant",
                    "icon": "fas fa-crown",
                    "timestamp": datetime.now().isoformat(),
                    "action": {
                        "label": "Passer au plan Pro",
                        "url": "/account?upgrade=pro",
                    },
                },
            )

        # Ajouter des notifications système si aucune activité récente
        if not notifications:
            notifications = [
                {
                    "id": "system_1",
                    "type": "info",
                    "title": "Bienvenue sur FinData IA",
                    "message": "Commencez par faire votre première requête API",
                    "time": "Maintenant",
                    "icon": "fas fa-info-circle",
                    "timestamp": datetime.now().isoformat(),
                }
            ]

        # Trier par timestamp décroissant
        notifications.sort(key=lambda x: x["timestamp"], reverse=True)

        return (
            jsonify(
                {
                    "success": True,
                    "notifications": notifications[:10],  # Limiter à 10 notifications
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des notifications: {e}")
        return (
            jsonify(
                {
                    "success": True,
                    "notifications": [
                        {
                            "id": "fallback_1",
                            "type": "info",
                            "title": "Système opérationnel",
                            "message": "FinData IA fonctionne correctement",
                            "time": "Maintenant",
                            "icon": "fas fa-info-circle",
                            "timestamp": datetime.now().isoformat(),
                        }
                    ],
                }
            ),
            200,
        )


@dashboard_bp.route("/scraping-tasks", methods=["GET"])
@jwt_required()
def get_scraping_tasks():
    """Obtenir les tâches de scraping de l'utilisateur"""
    try:
        current_user = get_jwt_identity()

        # Récupérer l'ID utilisateur
        user_query = "SELECT id FROM users WHERE username = %s"
        user_data = mysql_connector.execute_query(user_query, (current_user,))

        if not user_data:
            return jsonify({"success": False, "message": "Utilisateur non trouvé"}), 404

        user_id = user_data[0]["id"]

        # Récupérer les tâches de scraping récentes
        tasks_query = """
            SELECT 
                id,
                url,
                method,
                articles_count,
                status,
                processing_time,
                timestamp
            FROM scraping_history 
            WHERE user_id = %s 
            ORDER BY timestamp DESC
            LIMIT 10
        """
        tasks = mysql_connector.execute_query(tasks_query, (user_id,))

        # Formater les tâches pour le frontend
        formatted_tasks = []
        for task in tasks:
            # Déterminer le statut de la tâche
            if task["status"] == "success":
                status = "completed"
                status_icon = "fas fa-check"
                status_text = "Terminé"
            elif task["status"] == "failed":
                status = "failed"
                status_icon = "fas fa-times"
                status_text = "Échoué"
            else:
                status = "running"
                status_icon = "fas fa-spinner fa-spin"
                status_text = "En cours"

            # Calculer le temps écoulé
            from datetime import datetime

            task_time = task["timestamp"]
            if isinstance(task_time, str):
                task_time = datetime.fromisoformat(task_time.replace("Z", "+00:00"))

            time_diff = datetime.now() - task_time
            if time_diff.days > 0:
                time_ago = f"Il y a {time_diff.days} jour(s)"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                time_ago = f"Il y a {hours}h"
            elif time_diff.seconds > 60:
                minutes = time_diff.seconds // 60
                time_ago = f"Il y a {minutes}min"
            else:
                time_ago = "À l'instant"

            formatted_task = {
                "id": task["id"],
                "title": f"Scraping {task['url'].split('//')[1].split('/')[0] if '//' in task['url'] else task['url']}",
                "description": f"Extraction via {task['method']}",
                "status": status,
                "status_icon": status_icon,
                "status_text": status_text,
                "articles_count": task["articles_count"] or 0,
                "processing_time": task["processing_time"] or 0,
                "time_ago": time_ago,
                "url": task["url"],
            }
            formatted_tasks.append(formatted_task)

        return jsonify({"success": True, "tasks": formatted_tasks}), 200

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tâches de scraping: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Erreur lors de la récupération des tâches",
                    "tasks": [],
                }
            ),
            500,
        )


@dashboard_bp.route("/monitored-sites", methods=["GET"])
@jwt_required()
def get_monitored_sites():
    """Obtenir les sites surveillés de l'utilisateur"""
    try:
        current_user = get_jwt_identity()

        # Récupérer l'ID utilisateur
        user_query = "SELECT id FROM users WHERE username = %s"
        user_data = mysql_connector.execute_query(user_query, (current_user,))

        if not user_data:
            return jsonify({"success": False, "message": "Utilisateur non trouvé"}), 404

        user_id = user_data[0]["id"]

        # Récupérer les sites surveillés depuis scraping_history
        sites_query = """
            SELECT 
                url,
                MAX(timestamp) as last_check,
                COUNT(*) as check_count,
                AVG(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_rate
            FROM scraping_history 
            WHERE user_id = %s 
            GROUP BY url
            ORDER BY last_check DESC
            LIMIT 10
        """
        sites_data = mysql_connector.execute_query(sites_query, (user_id,))

        # Formater les données
        monitored_sites = []
        for site in sites_data:
            from urllib.parse import urlparse

            domain = urlparse(site["url"]).netloc if site["url"] else "unknown"

            # Déterminer le statut basé sur le taux de succès
            status = "online" if site["success_rate"] > 0.5 else "offline"

            # Calculer le temps écoulé
            time_ago = format_time_ago(site["last_check"])

            monitored_sites.append(
                {
                    "domain": domain,
                    "url": site["url"],
                    "status": status,
                    "last_check": time_ago,
                    "success_rate": round(site["success_rate"] * 100, 1),
                    "check_count": site["check_count"],
                }
            )

        return jsonify({"success": True, "sites": monitored_sites}), 200

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des sites surveillés: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


@dashboard_bp.route("/exports", methods=["GET"])
@jwt_required()
def get_exports():
    """Obtenir l'historique des exports de l'utilisateur"""
    try:
        current_user = get_jwt_identity()

        # Récupérer l'ID utilisateur
        user_query = "SELECT id FROM users WHERE username = %s"
        user_data = mysql_connector.execute_query(user_query, (current_user,))

        if not user_data:
            return jsonify({"success": False, "message": "Utilisateur non trouvé"}), 404

        user_id = user_data[0]["id"]

        # Pour l'instant, simuler des exports basés sur scraping_history
        # En production, il faudrait une table exports
        exports_query = """
            SELECT 
                id,
                url,
                articles_count,
                status,
                timestamp,
                'CSV' as format_type,
                ROUND(articles_count * 0.05, 2) as file_size_mb
            FROM scraping_history 
            WHERE user_id = %s 
            AND status = 'success'
            ORDER BY timestamp DESC
            LIMIT 10
        """
        exports_data = mysql_connector.execute_query(exports_query, (user_id,))

        # Formater les exports
        exports = []
        for export_item in exports_data:
            from urllib.parse import urlparse

            domain = (
                urlparse(export_item["url"]).netloc if export_item["url"] else "unknown"
            )

            exports.append(
                {
                    "id": export_item["id"],
                    "title": f"Export {domain} - {export_item['format_type']}",
                    "description": f"{export_item['articles_count']} articles exportés au format {export_item['format_type']}",
                    "format": export_item["format_type"],
                    "file_size": f"{export_item['file_size_mb']} MB",
                    "articles_count": export_item["articles_count"],
                    "status": "completed",
                    "time_ago": format_time_ago(export_item["timestamp"]),
                    "timestamp": export_item["timestamp"].isoformat(),
                }
            )

        # Calculer les statistiques d'export
        total_exports = len(exports)
        total_size = sum(float(exp["file_size"].replace(" MB", "")) for exp in exports)
        total_articles = sum(exp["articles_count"] for exp in exports)

        return (
            jsonify(
                {
                    "success": True,
                    "exports": exports,
                    "stats": {
                        "total_exports": total_exports,
                        "total_size_mb": round(total_size, 1),
                        "total_articles": total_articles,
                        "formats_supported": 3,  # CSV, Excel, JSON
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des exports: {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500


def format_time_ago(timestamp):
    """Formater le temps écoulé depuis un timestamp"""
    now = datetime.now()
    diff = now - timestamp

    if diff.days > 0:
        return f"Il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"Il y a {hours} heure{'s' if hours > 1 else ''}"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"Il y a {minutes} minute{'s' if minutes > 1 else ''}"
    else:
        return "À l'instant"
