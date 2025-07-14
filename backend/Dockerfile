# Utiliser une image Python officielle comme base
FROM python:3.10-slim

# Définir les variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     FLASK_APP=app.py     FLASK_ENV=production     PORT=8080     PYTHONPATH=/app

# Créer et définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Installer Playwright
RUN python -m playwright install chromium &&     python -m playwright install-deps chromium

# Copier le code source
COPY . .

# Créer le dossier logs
RUN mkdir -p logs

# Créer un utilisateur non-root pour la sécurité
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Exposer le port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Commande de démarrage
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:create_app()"] 