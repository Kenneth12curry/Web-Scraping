# Système de Limitation des Requêtes par Abonnement

## 📋 Vue d'ensemble

Le système de limitation des requêtes garantit que les utilisateurs respectent les limites de leur plan d'abonnement. Les utilisateurs du plan gratuit sont limités à 30 requêtes par mois, tandis que les utilisateurs Pro bénéficient de 10 000 requêtes.

## 🔧 Fonctionnalités Implémentées

### 1. Vérification Automatique des Limites
- **Avant chaque requête** : Le système vérifie si l'utilisateur a encore des requêtes disponibles
- **Blocage automatique** : Les requêtes sont rejetées avec le code HTTP 429 (Too Many Requests) si la limite est atteinte
- **Comptage en temps réel** : Chaque requête de scraping incrémente automatiquement le compteur

### 2. Plans d'Abonnement

#### Plan Gratuit (Free)
- **Limite** : 30 requêtes/mois
- **Fonctionnalités** :
  - Résumés IA basiques
  - Export JSON uniquement
  - Support communautaire
  - Interface intuitive

#### Plan Pro
- **Limite** : 10 000 requêtes/mois
- **Fonctionnalités** :
  - Résumés IA avancés
  - Export JSON, CSV & Excel
  - Analytics avancées
  - Support prioritaire 24/7
  - API complète

### 3. Gestion des Compteurs
- **Réinitialisation mensuelle** : Les compteurs se remettent à 0 le 1er de chaque mois
- **Persistance** : Les données sont stockées en base de données MySQL
- **Suivi détaillé** : Historique complet des utilisations

## 🗄️ Structure de la Base de Données

### Table `users` (mise à jour)
```sql
CREATE TABLE users (
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
);
```

### Nouveaux Champs
- `subscription_plan` : Plan d'abonnement ('free', 'pro')
- `subscription_start_date` : Date de début d'abonnement
- `subscription_end_date` : Date de fin d'abonnement (pour les abonnements payants)
- `monthly_requests_used` : Nombre de requêtes utilisées ce mois
- `monthly_requests_limit` : Limite de requêtes pour ce mois

## 🚀 Endpoints API

### 1. Vérification des Limites (Automatique)
```http
POST /api/scraping/extract
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://example.com",
  "max_articles": 20
}
```

**Réponse en cas de limite atteinte :**
```json
{
  "success": false,
  "message": "Limite mensuelle atteinte (30/30 requêtes)",
  "subscription_info": {
    "allowed": false,
    "used": 30,
    "limit": 30,
    "reason": "Limite mensuelle atteinte (30/30 requêtes)"
  }
}
```

### 2. Statut de l'Abonnement
```http
GET /api/subscription/status
Authorization: Bearer <token>
```

**Réponse :**
```json
{
  "success": true,
  "subscription": {
    "plan": "free",
    "used": 15,
    "limit": 30,
    "remaining": 15,
    "subscription_start_date": "2024-01-01T00:00:00",
    "subscription_end_date": null,
    "allowed": true
  }
}
```

### 3. Mise à Niveau d'Abonnement
```http
POST /api/subscription/upgrade
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan": "pro"
}
```

**Réponse :**
```json
{
  "success": true,
  "message": "Abonnement mis à niveau vers pro avec succès",
  "plan": "pro",
  "requests_limit": 10000
}
```

## 🔒 Logique de Vérification

### Fonction `check_subscription_limits(username)`
1. **Récupération des données utilisateur** depuis la base de données
2. **Vérification de l'expiration** de l'abonnement
3. **Comparaison** des requêtes utilisées vs limite
4. **Retour** du statut avec informations détaillées

### Fonction `increment_request_usage(username)`
1. **Incrémentation** du compteur `monthly_requests_used`
2. **Mise à jour** en base de données
3. **Logging** de l'utilisation

## 📊 Monitoring et Analytics

### Métriques Disponibles
- **Utilisation par utilisateur** : Requêtes utilisées vs limite
- **Taux de dépassement** : Pourcentage d'utilisateurs qui atteignent leur limite
- **Distribution des plans** : Nombre d'utilisateurs par plan
- **Tendances mensuelles** : Évolution de l'utilisation

### Logs Disponibles
```bash
# Voir les logs de limitation
grep -i "limite\|subscription" backend/logs/app.log

# Voir les erreurs 429
grep -i "429" backend/logs/app.log

# Voir les mises à niveau d'abonnement
grep -i "upgrade\|subscription" backend/logs/app.log
```

## 🔄 Réinitialisation Mensuelle

### Script Automatique
Le script `reset_monthly_usage.py` permet de réinitialiser tous les compteurs :

```bash
# Exécution manuelle
python backend/reset_monthly_usage.py

# Configuration cron (Linux/Mac)
# Ajouter dans crontab : 0 0 1 * * /path/to/python /path/to/reset_monthly_usage.py

# Configuration Task Scheduler (Windows)
# Créer une tâche planifiée pour exécuter le script le 1er de chaque mois
```

### Fonction `reset_monthly_usage()`
1. **Connexion** à la base de données
2. **Mise à jour** de tous les compteurs à 0
3. **Logging** de l'opération
4. **Vérification** du succès

## 🧪 Tests

### Script de Test Complet
```bash
python test_subscription_limits.py
```

### Tests Inclus
1. **Création d'utilisateur** avec plan gratuit
2. **Vérification** du statut initial
3. **Requêtes de scraping** jusqu'à la limite
4. **Blocage** après dépassement
5. **Mise à niveau** vers le plan Pro
6. **Vérification** du nouveau statut

### Test Manuel avec curl
```bash
# 1. Se connecter
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# 2. Vérifier le statut (avec le token reçu)
curl -X GET http://localhost:8080/api/subscription/status \
  -H "Authorization: Bearer <token>"

# 3. Tester le scraping
curl -X POST http://localhost:8080/api/scraping/extract \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## 🎯 Messages d'Erreur

### Limite Atteinte
```
Limite mensuelle atteinte (30/30 requêtes)
```

### Abonnement Expiré
```
Abonnement expiré
```

### Utilisateur Non Trouvé
```
Utilisateur non trouvé
```

## 📱 Intégration Frontend

### Affichage du Statut
```jsx
const SubscriptionStatus = () => {
  const [subscription, setSubscription] = useState(null);
  
  useEffect(() => {
    // Récupérer le statut d'abonnement
    fetch('/api/subscription/status', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => setSubscription(data.subscription));
  }, []);
  
  return (
    <div className="subscription-status">
      <h3>Plan {subscription?.plan}</h3>
      <div className="usage-bar">
        <div 
          className="usage-fill" 
          style={{width: `${(subscription?.used / subscription?.limit) * 100}%`}}
        />
      </div>
      <p>{subscription?.used} / {subscription?.limit} requêtes utilisées</p>
      <p>{subscription?.remaining} requêtes restantes</p>
    </div>
  );
};
```

### Gestion des Erreurs 429
```jsx
const handleScraping = async (url) => {
  try {
    const response = await fetch('/api/scraping/extract', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url })
    });
    
    if (response.status === 429) {
      const error = await response.json();
      alert(`Limite atteinte: ${error.message}`);
      // Afficher le modal de mise à niveau
      showUpgradeModal();
    } else if (response.ok) {
      const data = await response.json();
      setResults(data.articles);
    }
  } catch (error) {
    console.error('Erreur:', error);
  }
};
```

## 🔧 Configuration

### Variables d'Environnement
```bash
# Limites par défaut (optionnel)
FREE_PLAN_LIMIT=30
PRO_PLAN_LIMIT=10000
```

### Personnalisation des Limites
Pour modifier les limites, éditez la fonction `upgrade_subscription()` dans `app.py` :

```python
plan_limits = {
    'free': 30,      # Limite plan gratuit
    'pro': 10000     # Limite plan pro
}
```

## 🎉 Résumé

Le système de limitation des requêtes est maintenant **entièrement fonctionnel** :

✅ **Vérification automatique** avant chaque requête  
✅ **Comptage en temps réel** des utilisations  
✅ **Blocage automatique** après dépassement de limite  
✅ **Mise à niveau d'abonnement** via API  
✅ **Réinitialisation mensuelle** automatique  
✅ **Monitoring complet** et logs détaillés  
✅ **Tests automatisés** pour validation  

Les utilisateurs du plan gratuit ne pourront plus envoyer de requêtes une fois leurs 30 requêtes mensuelles atteintes, exactement comme vous le souhaitiez ! 🎯 