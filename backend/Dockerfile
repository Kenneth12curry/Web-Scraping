# Utiliser une image Python officielle comme base
FROM python:3.10-slim

# Définir les variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     FLASK_APP=app.py     FLASK_ENV=production     PORT=8080     PYTHONPATH=/app

# Créer et définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y     gcc     g++     curl     fonts-liberation     libappindicator3-1     libasound2     libatk-bridge2.0-0     libatk1.0-0     libcairo2     libcups2     libdbus-1-3     libdrm-dev     libgbm-dev     libgconf-2-4     libgdk-pixbuf2.0-0     libglib2.0-0     libgtk-3-0     libnspr4     libnss3     libx11-6     libxcomposite1     libxcursor1     libxdamage1     libxext6     libxfixes3     libxi6     libxrandr2     libxrender1     libxss1     libxtst6     xdg-utils     chromium-driver     && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Installer Playwright
RUN python -m playwright install chromium

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
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "--timeout", "120", "app:create_app()"] 