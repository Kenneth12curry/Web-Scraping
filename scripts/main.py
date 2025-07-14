import os
import sys
import json
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import urllib.parse

# Charger les variables d'environnement depuis .env
load_dotenv()

# Nom du modèle Groq à utiliser (fintech-friendly, rapide et robuste)
MODEL_NAME = "llama3-8b-8192"

# Configuration Scrape.do
SCRAPEDO_API_KEY = os.getenv('SCRAPEDO_API_KEY')
SCRAPEDO_BASE_URL = "https://api.scraped.do"


def scrape_with_scrapedo(url: str, params: dict = {}) -> dict:
    """
    Utilise l'API Scrape.do pour récupérer le contenu d'une page web (conforme à la doc officielle).
    """
    if not SCRAPEDO_API_KEY:
        raise ValueError("Token Scrape.do manquant dans le fichier .env")

    # Construction de la query string
    query = {
        "token": SCRAPEDO_API_KEY,
        "url": urllib.parse.quote_plus(url)
    }
    query.update(params)
    full_url = "https://api.scrape.do/?" + "&".join(f"{k}={v}" for k, v in query.items())

    try:
        response = requests.get(full_url, timeout=60)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return response.json()
        else:
            return {"html": response.text}
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erreur Scrape.do: {e}")


def get_site_content_professional(url: str) -> str:
    """
    Récupère le contenu d'un site de manière professionnelle avec Scrape.do.
    """
    try:
        result = scrape_with_scrapedo(url)
        return result.get('html', '')
    except Exception as e:
        print(f"⚠️  Erreur Scrape.do: {e}")
        print("🔄 Fallback vers requests standard...")
        try:
            response = requests.get(url, timeout=10)
            return response.text
        except Exception as e2:
            print(f"❌ Erreur requests: {e2}")
            return ""


def test_scrapedo_connection() -> bool:
    """
    Teste la connexion à l'API Scrape.do.
    """
    if not SCRAPEDO_API_KEY:
        return False
    
    try:
        # Test simple avec une URL de test
        result = scrape_with_scrapedo("https://httpbin.org/html")
        return 'html' in result
    except Exception:
        return False


def is_dynamic_site(html: str) -> bool:
    """
    Détecte si une page est dynamique (React, Angular, Vue, etc.) pour adapter le prompt.
    """
    dynamic_keywords = [
        'window.__', 'React', 'angular', 'vue', 'data-layer', 'app-root',
        'next.js', 'nuxt', 'gatsby', 'spa', 'single-page',
        'api/', 'graphql', 'ajax', 'fetch', 'axios',
        'lazy-load', 'infinite-scroll', 'dynamic-content',
        'webpack', 'bundle', 'chunk', 'module',
        'hydration', 'vite', 'svelte', 'solidjs', 'remix', 'astro',
    ]
    script_count = html.count('<script')
    if script_count > 5:
        return True
    for kw in dynamic_keywords:
        if kw.lower() in html.lower():
            return True
    if html.count('data-') > 10:
        return True
    return False


def generate_scraping_prompt(site_url: str, is_dynamic: bool) -> str:
    """
    Génère un prompt détaillé pour obtenir un script de scraping web adapté à un site donné.
    Si le site est dynamique (React, Angular, etc.), propose Selenium ou Playwright.
    Inclut maintenant l'option Scrape.do pour un travail professionnel.
    """
    if is_dynamic:
        return f"""
Tu es un expert en scraping web pour la fintech. Génère un script Python complet qui :
- Utilise Selenium (ou Playwright si tu préfères) pour charger dynamiquement les pages du site : {site_url}
- OU utilise l'API Scrape.do (plus professionnel) avec le token dans .env
- Pour chaque article financier, extrait le titre, l'URL, la date si disponible
- Va sur la page de chaque article pour extraire le texte principal
- Utilise urllib.parse.urljoin pour construire les URLs complètes
- Vérifie l'existence de chaque élément avant d'y accéder
- Gère la pagination (maximum 3 pages)
- Affiche les résultats dans la console

IMPORTANT :
- Utilise des variables temporaires pour chaque extraction
- Gère les cas où les éléments n'existent pas
- N'inclus AUCUNE explication, seulement le code Python pur
- Le code doit être exécutable immédiatement
- Le script doit être robuste pour les sites fintech modernes (React, Angular, etc.)

Exemple de structure robuste avec Scrape.do :
```python
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import urllib.parse

load_dotenv()
SCRAPEDO_API_KEY = os.getenv('SCRAPEDO_API_KEY')

def scrape_with_scrapedo(url):
    headers = {{'Authorization': f'Bearer {{SCRAPEDO_API_KEY}}'}}
    response = requests.post('https://api.scraped.do/scrape', 
                           headers=headers,
                           json={{'url': url, 'render': 'true', 'wait': 3000}})
    return response.json()['html']

# Utilisation
html = scrape_with_scrapedo("{site_url}")
soup = BeautifulSoup(html, 'html.parser')
# Extraction...
```

Ou avec Selenium :
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import urllib.parse
import time

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get("{site_url}")
# Extraction dynamique...
```
"""
    else:
        return f"""
Tu es un expert en scraping web pour la fintech. Génère un script Python complet qui :
- Utilise requests et BeautifulSoup pour extraire les articles du site : {site_url}
- OU utilise l'API Scrape.do (plus professionnel) avec le token dans .env
- Pour chaque article, extrait le titre, l'URL, la date si disponible
- Va sur la page de chaque article pour extraire le texte principal
- Utilise urllib.parse.urljoin pour construire les URLs complètes
- Vérifie l'existence de chaque élément avant d'y accéder
- Gère la pagination (maximum 3 pages)
- Affiche les résultats dans la console

IMPORTANT :
- Utilise des variables temporaires pour chaque extraction
- Gère les cas où les éléments n'existent pas
- N'inclus AUCUNE explication, seulement le code Python pur
- Le code doit être exécutable immédiatement
- Le script doit être robuste pour les sites fintech

Exemple de structure robuste avec Scrape.do :
```python
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import urllib.parse

load_dotenv()
SCRAPEDO_API_KEY = os.getenv('SCRAPEDO_API_KEY')

def scrape_with_scrapedo(url):
    headers = {{'Authorization': f'Bearer {{SCRAPEDO_API_KEY}}'}}
    response = requests.post('https://api.scraped.do/scrape', 
                           headers=headers,
                           json={{'url': url, 'render': 'true'}})
    return response.json()['html']

# Utilisation
html = scrape_with_scrapedo("{site_url}")
soup = BeautifulSoup(html, 'html.parser')
# Extraction...
```

Ou avec requests standard :
```python
import requests
from bs4 import BeautifulSoup
import urllib.parse

url = "{site_url}"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
# Extraction des articles...
```
"""

def query_groq(prompt: str, model: str = MODEL_NAME) -> str:
    """
    Envoie un prompt au modèle Groq via LangChain et retourne la réponse textuelle.
    """
    try:
        llm = ChatGroq(model=model, temperature=0.0)
        response = llm.invoke(prompt)
        # Toujours retourner un str, même si le contenu est une liste ou structuré
        return response.text() if hasattr(response, 'text') else str(response)
    except Exception as e:
        return f"[ERREUR] Problème avec l'API Groq : {e}"

def main():
    print("🚀 Test de scraping avec Groq (LangChain) + Scrape.do")
    print("=" * 60)

    # Vérifier la configuration
    if not SCRAPEDO_API_KEY:
        print("⚠️  Token Scrape.do manquant dans .env")
        print("   Le scraping utilisera requests standard")
    else:
        print("✅ Token Scrape.do configuré")
        # Tester la connexion
        print("🔄 Test de connexion Scrape.do...")
        if test_scrapedo_connection():
            print("✅ Connexion Scrape.do réussie")
        else:
            print("❌ Échec de connexion Scrape.do")

    # Demander l'URL du site
    site_url = input("\n🌐 Entrez l'URL du site à scraper : ").strip()
    if not site_url:
        site_url = "https://www.finextra.com/news"
        print(f"URL par défaut utilisée : {site_url}")

    # Choisir la méthode de scraping
    print("\n🔧 Choisissez la méthode de scraping :")
    print("1. Scrape.do (recommandé - professionnel)")
    print("2. Requests standard (rapide)")
    print("3. Détection automatique")
    
    choice = input("Votre choix (1-3) : ").strip()
    
    # Récupérer le contenu selon la méthode choisie
    if choice == "1" and SCRAPEDO_API_KEY:
        print("🔄 Utilisation de Scrape.do...")
        html = get_site_content_professional(site_url)
    elif choice == "2":
        print("🔄 Utilisation de requests standard...")
        try:
            html = requests.get(site_url, timeout=10).text
        except Exception as e:
            print(f"❌ Erreur requests: {e}")
            html = ""
    else:
        print("🔄 Détection automatique...")
        if SCRAPEDO_API_KEY:
            html = get_site_content_professional(site_url)
        else:
            try:
                html = requests.get(site_url, timeout=10).text
            except Exception as e:
                print(f"❌ Erreur requests: {e}")
                html = ""

    # Détecter si le site est dynamique
    is_dynamic = is_dynamic_site(html)
    print(f"\n📊 Site détecté comme {'dynamique' if is_dynamic else 'statique'}")

    # Générer et envoyer le prompt
    prompt = generate_scraping_prompt(site_url, is_dynamic)
    print(f"\n🔹 Prompt envoyé au modèle :\n{prompt}")

    response = query_groq(prompt)
    print(f"\n🔸 Réponse du modèle :\n{response}")

    # Option pour exécuter le code généré
    if "[ERREUR]" not in response:
        execute = input("\n🤔 Voulez-vous exécuter le code généré ? (o/n) : ").lower().strip()
        if execute in ['o', 'oui', 'y', 'yes']:
            print("\n⚠️  ATTENTION : Exécution de code généré par IA")
            print("Le code sera exécuté dans un environnement sécurisé...")
            print("(Fonctionnalité d'exécution à implémenter)")

if __name__ == "__main__":
    main()
