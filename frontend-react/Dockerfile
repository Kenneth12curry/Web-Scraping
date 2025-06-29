# Stage de build
FROM node:18-alpine AS build

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm ci --only=production

# Copier le code source
COPY . .

# Build de l'application
RUN npm run build

# Stage de production
FROM nginx:alpine

# Copier la configuration nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Copier les fichiers buildés
COPY --from=build /app/build /usr/share/nginx/html

# Exposer le port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1

# Commande de démarrage
CMD ["nginx", "-g", "daemon off;"] 