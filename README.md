# 🚀 FinData IA-M.K

**Plateforme moderne de scraping et d'analyse de données fintech**

Interface web professionnelle avec design dynamique et expérience utilisateur avancée.

## ✨ Fonctionnalités principales

- **Authentification sécurisée** (JWT)
- **Dashboard moderne** : statistiques, quotas, top domaines, historique
- **Scraping intelligent** : Scrape.do (API) + fallback requests
- **Analytics détaillées** : graphiques, tendances, erreurs récentes
- **Export CSV/JSON** des résultats
- **Interface React** ultra-moderne (glassmorphism, animations, responsive)
- **Expérience utilisateur dynamique** (animations, transitions, feedback visuel)
- **API REST complète** pour intégration
- **Base de données SQLite** pour les stats et l'historique

## 🎨 Design & Expérience Utilisateur

- **Glassmorphism** : Effet verre, flou, ombres et gradients
- **Animations** : Entrée, survol, transitions fluides, feedback visuel
- **Responsive** : Adapté mobile/tablette/desktop
- **Palette moderne** : Gradients violets/bleus, couleurs vives
- **Icônes FontAwesome** : UI riche et intuitive
- **Mode sombre automatique** (selon OS)
- **Accessibilité** : Contrastes, focus, navigation clavier

## 🛠️ Stack technique

- **Backend** : Flask, JWT, SQLite, Scrape.do, CORS
- **Frontend** : React, Bootstrap 5, Chart.js, FontAwesome
- **API** : RESTful, endpoints sécurisés, gestion d'erreurs
- **Scripts** : Batch Windows pour démarrage facile

## 📁 Structure du projet

```
Test/
├── backend/                 # API Flask
│   ├── app.py              # Application principale
│   ├── requirements.txt    # Dépendances Python
│   └── stats.db           # Base de données SQLite
├── frontend-react/         # Interface React
│   ├── src/
│   │   ├── components/     # Composants React
│   │   ├── services/       # Services API
│   │   ├── config.js       # Configuration centralisée
│   │   └── App.js         # Application principale
│   └── package.json       # Dépendances Node.js
├── .env                   # Variables d'environnement
├── test_app.py           # Script de test API
├── start.bat             # Script de démarrage Windows
└── README.md             # Ce fichier
```

## 🚀 Installation & Démarrage

### 1. Prérequis
- Python 3.8+
- Node.js 16+
- npm

### 2. Configuration de l'environnement
Créez un fichier `.env` à la racine du projet :

```env
SCRAPEDO_API_KEY=your_scrapedo_token_here
GROQ_API_KEY=your_groq_token_here
JWT_SECRET_KEY=your_jwt_secret_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### 3. Installation du backend
```bash
# Activer l'environnement virtuel
env\Scripts\activate

# Installer les dépendances Python
cd backend
pip install -r requirements.txt

# Démarrer l'API
python app.py
```

L'API sera disponible sur `http://localhost:8080`

### 4. Installation du frontend
```bash
# Dans un nouveau terminal
cd frontend-react

# Installer les dépendances
npm install

# Démarrer l'application React
npm start
```

L'interface sera disponible sur `http://localhost:3000`

### 5. Démarrage rapide (Windows)
Double-cliquez sur `start.bat` pour lancer backend + frontend automatiquement.

## 🔐 Authentification

**Identifiants par défaut :**
- **Utilisateur :** `admin`
- **Mot de passe :** `admin123`

⚠️ **Important :** Changez ces identifiants en production !

## 📊 Utilisation

### 1. Connexion
- Accédez à `http://localhost:3000`
- Connectez-vous avec vos identifiants

### 2. Dashboard
- **Statistiques API** : Utilisation, limites, quotas
- **Configuration** : Statut des services (Scrape.do, Groq)
- **Analytics** : Historique des opérations

### 3. Scraping
- **URL** : Entrez l'URL du site à scraper
- **Méthode** : Choisissez Scrape.do ou Requests
- **Résultats** : Articles extraits avec métadonnées
- **Export** : Téléchargez en CSV ou JSON

### 4. Analytics
- **Graphiques** : Visualisation des données
- **Tendances** : Évolution des performances
- **Erreurs récentes** : Monitoring des problèmes

### 5. Documentation
- **API Endpoints** : Documentation complète
- **Exemples** : Codes d'exemple pour l'intégration
- **Configuration** : Guide de configuration

## 🔧 API Endpoints

### Authentification
- `POST /api/auth/login` - Connexion
- `POST /api/auth/logout` - Déconnexion

### Dashboard
- `GET /api/dashboard/stats` - Statistiques
- `GET /api/dashboard/analytics` - Analytics

### Scraping
- `POST /api/scraping/extract` - Extraction d'articles

### Utilitaires
- `GET /api/health` - Vérification de santé

## 🎯 Exemples d'utilisation

### Extraction d'articles
```bash
curl -X POST http://localhost:8080/api/scraping/extract \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.finextra.com/news/latestnews.aspx?topic=fintech",
    "method": "scrapedo"
  }'
```

### Récupération des statistiques
```bash
curl -X GET http://localhost:8080/api/dashboard/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔒 Sécurité

- **JWT** pour l'authentification
- **CORS** configuré pour les frontends
- **Validation** des entrées utilisateur
- **Gestion d'erreurs** sécurisée

## 📈 Monitoring

- **Base de données SQLite** pour les statistiques
- **Logs** des opérations de scraping
- **Analytics** en temps réel
- **Historique** des domaines utilisés

## 🚀 Déploiement

### Production
1. Changez les identifiants par défaut
2. Utilisez un serveur WSGI (Gunicorn)
3. Configurez un reverse proxy (Nginx)
4. Utilisez HTTPS
5. Configurez les variables d'environnement

### Docker (optionnel)
```bash
# Backend
docker build -t findata-backend ./backend
docker run -p 8080:8080 findata-backend

# Frontend
docker build -t findata-frontend ./frontend-react
docker run -p 3000:3000 findata-frontend
```

## 🐛 Dépannage

### Problèmes courants

1. **Erreur de port** : Changez le port dans `backend/app.py`
2. **CORS** : Vérifiez la configuration dans `backend/app.py`
3. **Dépendances** : Relancez `npm install` ou `pip install -r requirements.txt`
4. **Base de données** : Supprimez `backend/stats.db` pour réinitialiser

### Logs
- **Backend** : Logs dans la console
- **Frontend** : Console du navigateur (F12)

## 📞 Support

- **Email** : diandiallo974@gmail.com
- **Documentation Scrape.do** : https://scrape.do/docs
- **Issues** : Créez une issue sur GitHub

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

**FinData IA-M.K** - Propulsé par Flask, React, Scrape.do et Groq AI 