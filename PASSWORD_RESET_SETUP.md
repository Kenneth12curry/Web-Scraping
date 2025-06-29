# Configuration de la fonctionnalité "Mot de passe oublié"

## 📋 Vue d'ensemble

Cette fonctionnalité permet aux utilisateurs de réinitialiser leur mot de passe en recevant un lien sécurisé par email. Le système utilise Gmail SMTP pour l'envoi d'emails.

## 🔧 Configuration

### 1. Configuration SMTP Gmail

#### Étape 1: Activer l'authentification à 2 facteurs
1. Allez sur [myaccount.google.com](https://myaccount.google.com)
2. Sécurité → Connexion à Google → Authentification à 2 facteurs
3. Activez l'authentification à 2 facteurs

#### Étape 2: Créer un mot de passe d'application
1. Sécurité → Connexion à Google → Mots de passe d'application
2. Sélectionnez "Autre (nom personnalisé)"
3. Nommez-le "FinData Password Reset"
4. Copiez le mot de passe généré (16 caractères)

#### Étape 3: Configurer le fichier .env
```bash
# Configuration SMTP pour l'envoi d'emails (mot de passe oublié)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre_email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_application_ici
SMTP_USE_TLS=true
SMTP_USE_SSL=false
FRONTEND_URL=http://localhost:3000
```

### 2. Variables d'environnement

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `SMTP_HOST` | Serveur SMTP | `smtp.gmail.com` |
| `SMTP_PORT` | Port SMTP | `587` |
| `SMTP_USERNAME` | Email Gmail | - |
| `SMTP_PASSWORD` | Mot de passe d'application | - |
| `SMTP_USE_TLS` | Utiliser TLS | `true` |
| `SMTP_USE_SSL` | Utiliser SSL | `false` |
| `FRONTEND_URL` | URL du frontend | `http://localhost:3000` |

## 🚀 Endpoints API

### 1. Demande de réinitialisation
```http
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "utilisateur@example.com"
}
```

**Réponse:**
```json
{
  "success": true,
  "message": "Si cet email existe dans notre base de données, vous recevrez un lien de réinitialisation."
}
```

### 2. Vérification de token
```http
POST /api/auth/verify-reset-token
Content-Type: application/json

{
  "token": "token_de_reinitialisation"
}
```

**Réponse:**
```json
{
  "success": true,
  "message": "Token valide",
  "valid": true
}
```

### 3. Réinitialisation du mot de passe
```http
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "token_de_reinitialisation",
  "new_password": "nouveau_mot_de_passe"
}
```

**Réponse:**
```json
{
  "success": true,
  "message": "Mot de passe réinitialisé avec succès. Vous pouvez maintenant vous connecter."
}
```

## 🔒 Sécurité

### Fonctionnalités de sécurité implémentées:

1. **Tokens sécurisés**: Génération de tokens cryptographiquement sécurisés
2. **Expiration**: Tokens valides pendant 1 heure maximum
3. **Usage unique**: Chaque token ne peut être utilisé qu'une seule fois
4. **Limites de taux**: 
   - 3 demandes de réinitialisation par heure
   - 5 tentatives de réinitialisation par heure
5. **Pas de fuite d'informations**: Réponse identique pour emails existants et inexistants
6. **Validation des mots de passe**: Minimum 6 caractères

### Base de données

Nouvelle table créée:
```sql
CREATE TABLE password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_token (token),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## 📧 Template d'email

L'email envoyé contient:
- Salutation personnalisée
- Explication de la demande
- Bouton de réinitialisation stylisé
- Information sur l'expiration (1 heure)
- Avertissement de sécurité
- Signature de l'équipe

## 🧪 Tests

### Test automatique
```bash
python test_password_reset.py
```

### Test manuel avec curl
```bash
# 1. Demande de réinitialisation
curl -X POST http://localhost:8080/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 2. Vérification de token (avec un token valide)
curl -X POST http://localhost:8080/api/auth/verify-reset-token \
  -H "Content-Type: application/json" \
  -d '{"token": "votre_token_ici"}'

# 3. Réinitialisation du mot de passe
curl -X POST http://localhost:8080/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token": "votre_token_ici", "new_password": "nouveau_mot_de_passe"}'
```

## 🔍 Dépannage

### Problèmes courants

1. **Erreur SMTP "Authentication failed"**
   - Vérifiez que l'authentification à 2 facteurs est activée
   - Utilisez un mot de passe d'application, pas votre mot de passe principal
   - Vérifiez que `SMTP_USERNAME` est votre email Gmail complet

2. **Erreur "Connection refused"**
   - Vérifiez que le port 587 n'est pas bloqué par votre pare-feu
   - Essayez le port 465 avec `SMTP_USE_SSL=true`

3. **Emails non reçus**
   - Vérifiez le dossier spam
   - Testez avec un email différent
   - Vérifiez les logs du serveur pour les erreurs SMTP

4. **Token invalide**
   - Les tokens expirent après 1 heure
   - Chaque token ne peut être utilisé qu'une fois
   - Vérifiez que l'URL de réinitialisation est correcte

### Logs utiles

```bash
# Voir les logs du serveur
tail -f backend/logs/app.log

# Rechercher les erreurs SMTP
grep -i smtp backend/logs/app.log

# Rechercher les demandes de réinitialisation
grep -i "forgot_password\|reset_password" backend/logs/app.log
```

## 📱 Intégration Frontend

### Flux utilisateur recommandé:

1. **Page de connexion**: Lien "Mot de passe oublié ?"
2. **Page de demande**: Formulaire avec email
3. **Page de confirmation**: Message de succès
4. **Page de réinitialisation**: Formulaire avec nouveau mot de passe
5. **Redirection**: Vers la page de connexion

### Exemple de composant React (à implémenter):

```jsx
// ForgotPassword.js
const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      
      const data = await response.json();
      setMessage(data.message);
    } catch (error) {
      setMessage('Erreur lors de la demande');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Votre email"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Envoi...' : 'Réinitialiser le mot de passe'}
      </button>
      {message && <p>{message}</p>}
    </form>
  );
};
```

## 🎯 Prochaines étapes

1. ✅ Backend implémenté
2. 🔄 Frontend à développer
3. 🔄 Tests d'intégration
4. 🔄 Documentation utilisateur
5. 🔄 Monitoring et alertes

## 📞 Support

Pour toute question ou problème:
1. Vérifiez cette documentation
2. Consultez les logs du serveur
3. Testez avec le script de test fourni
4. Vérifiez la configuration SMTP 