#!/bin/bash

echo "🐳 Démarrage de FinData IA-M.K avec Docker"
echo "=========================================="

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé !"
    echo "Veuillez installer Docker depuis https://docker.com"
    exit 1
fi

# Vérifier si Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé !"
    exit 1
fi

# Vérifier si le fichier .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé !"
    echo "📝 Création d'un fichier .env avec les valeurs par défaut..."
    cp env.example .env
    echo "✅ Fichier .env créé"
    echo "⚠️  N'oubliez pas de configurer vos API keys !"
fi

# Construire et démarrer les services
echo "🚀 Construction et démarrage des services..."
docker-compose up --build -d

# Attendre que les services démarrent
echo "⏳ Attente du démarrage des services..."
sleep 30

# Vérifier le statut des services
echo "🔍 Vérification du statut des services..."
docker-compose ps

echo ""
echo "✅ Application démarrée avec succès !"
echo ""
echo "📍 URLs d'accès :"
echo "   🌐 Frontend: http://localhost"
echo "   🔧 Backend API: http://localhost:8080"
echo "   📊 Grafana: http://localhost:3001 (admin/admin123)"
echo "   📈 Prometheus: http://localhost:9090"
echo "   🚨 Sentry: http://localhost:9000"
echo ""
echo "🔐 Identifiants par défaut:"
echo "   Utilisateur: admin"
echo "   Mot de passe: admin123"
echo ""
echo "📋 Commandes utiles :"
echo "   docker-compose logs -f backend    # Voir les logs du backend"
echo "   docker-compose logs -f frontend   # Voir les logs du frontend"
echo "   docker-compose down               # Arrêter l'application"
echo "   docker-compose restart            # Redémarrer l'application"
echo "" 