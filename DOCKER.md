# 🐳 Docker - FinData IA-M.K

Guide complet pour déployer FinData IA-M.K avec Docker et Docker Compose.

## 📋 Prérequis

- Docker Engine 20.10+
- Docker Compose 2.0+
- Au moins 4GB de RAM disponible
- 10GB d'espace disque libre

## 🚀 Démarrage Rapide

### 1. Cloner le projet
```bash
git clone <votre-repo>
cd findata-ia-mk
```

### 2. Configurer l'environnement
```bash
# Copier le fichier d'exemple
cp env.example .env

# Éditer le fichier .env avec vos API keys
nano .env
```

### 3. Démarrer l'application
```bash
# Option 1: Script automatique
chmod +x docker-start.sh
./docker-start.sh

# Option 2: Commande manuelle
docker-compose up --build -d
```

## 📊 Services Disponibles

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| Frontend | 80 | http://localhost | Interface utilisateur React |
| Backend | 8080 | http://localhost:8080 | API Flask |
| Grafana | 3001 | http://localhost:3001 | Dashboards de monitoring |
| Prometheus | 9090 | http://localhost:9090 | Métriques et alertes |
| Sentry | 9000 | http://localhost:9000 | Tracking des erreurs |

## 🔧 Configuration

### Variables d'Environnement

```env
# API Keys (OBLIGATOIRES)
SCRAPEDO_API_KEY=your_scrapedo_token_here
GROQ_API_KEY=your_groq_token_here

# Sécurité (CHANGEZ EN PRODUCTION)
JWT_SECRET_KEY=your_jwt_secret_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
PROMETHEUS_ENABLED=true
LOG_LEVEL=INFO
```

### Volumes Persistants

- `./backend/logs` : Logs de l'application
- `./backend/stats.db` : Base de données SQLite
- `prometheus_data` : Données Prometheus
- `grafana_data` : Dashboards et configurations Grafana
- `sentry_data` : Données Sentry

## 📈 Monitoring

### Grafana Dashboards

1. Accédez à http://localhost:3001
2. Connectez-vous avec `admin/admin123`
3. Dashboards disponibles :
   - **FinData IA-M.K Dashboard** : Métriques principales
   - **Requêtes HTTP** : Performance des API
   - **Scraping Analytics** : Statistiques de scraping

### Prometheus Métriques

- `http_requests_total` : Nombre total de requêtes
- `http_request_duration_seconds` : Latence des requêtes
- `scraping_requests_total` : Requêtes de scraping
- `api_usage_total` : Utilisation de l'API

### Sentry Error Tracking

- Tracking automatique des erreurs Flask
- Groupement intelligent des erreurs
- Alertes en temps réel
- Stack traces détaillées

## 🔍 Commandes Utiles

### Gestion des Services
```bash
# Voir le statut des services
docker-compose ps

# Voir les logs en temps réel
docker-compose logs -f backend
docker-compose logs -f frontend

# Redémarrer un service
docker-compose restart backend

# Arrêter l'application
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

### Maintenance
```bash
# Mettre à jour les images
docker-compose pull

# Reconstruire les images
docker-compose build --no-cache

# Nettoyer les images non utilisées
docker system prune -a

# Voir l'utilisation des ressources
docker stats
```

### Debugging
```bash
# Accéder au shell du backend
docker-compose exec backend bash

# Voir les logs d'un service spécifique
docker-compose logs backend | grep ERROR

# Tester la connectivité
docker-compose exec backend curl http://localhost:8080/api/health
```

## 🚀 Déploiement en Production

### 1. Configuration Production
```env
FLASK_ENV=production
FLASK_DEBUG=false
ADMIN_PASSWORD=your_secure_password_here
JWT_SECRET_KEY=your_very_secure_secret_key
```

### 2. Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://localhost:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. SSL/TLS avec Let's Encrypt
```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir un certificat
sudo certbot --nginx -d your-domain.com

# Renouvellement automatique
sudo crontab -e
# Ajouter: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔒 Sécurité

### Bonnes Pratiques
- ✅ Changez les mots de passe par défaut
- ✅ Utilisez des secrets sécurisés pour JWT
- ✅ Activez HTTPS en production
- ✅ Limitez l'accès aux ports de monitoring
- ✅ Surveillez les logs régulièrement

### Firewall
```bash
# Autoriser seulement les ports nécessaires
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

## 📊 Performance

### Optimisations Recommandées
- **Backend** : 2 vCPU, 2GB RAM minimum
- **Frontend** : 1 vCPU, 1GB RAM minimum
- **Monitoring** : 1 vCPU, 2GB RAM minimum
- **Base de données** : SSD recommandé

### Monitoring des Ressources
```bash
# Voir l'utilisation des ressources
docker stats

# Voir les métriques système
docker-compose exec backend top

# Vérifier l'espace disque
docker system df
```

## 🆘 Dépannage

### Problèmes Courants

#### Service ne démarre pas
```bash
# Vérifier les logs
docker-compose logs backend

# Vérifier la configuration
docker-compose config

# Redémarrer le service
docker-compose restart backend
```

#### Problème de connectivité
```bash
# Tester la connectivité réseau
docker-compose exec backend ping prometheus

# Vérifier les ports
netstat -tulpn | grep :8080
```

#### Problème de permissions
```bash
# Corriger les permissions
sudo chown -R $USER:$USER ./backend/logs
sudo chown -R $USER:$USER ./backend/stats.db
```

## 📚 Ressources Additionnelles

- [Documentation Docker](https://docs.docker.com/)
- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Sentry Documentation](https://docs.sentry.io/) 