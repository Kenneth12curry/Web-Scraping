# Utiliser l'image officielle de MySQL
FROM mysql:8.0

# Copier le script d'initialisation SQL dans le répertoire d'initialisation de MySQL
# Les scripts dans ce dossier sont exécutés au premier démarrage du conteneur
COPY init.sql /docker-entrypoint-initdb.d/
