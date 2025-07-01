"""
Service de scraping
"""
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import logging
import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse
import time
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from playwright.sync_api import sync_playwright
from langchain_groq import ChatGroq
from config import Config
from database.mysql_connector import mysql_connector
from database.redis_connector import redis_connector
import random
from typing import Optional

logger = logging.getLogger(__name__)

class ScrapingService:
    """Service de gestion du scraping"""
    
    USER_AGENTS = [
        # Liste de User-Agents courants pour la rotation
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    ]
    
    def __init__(self, min_delay: float = 0.5, proxies: Optional[dict] = None):
        self.db = mysql_connector
        self.cache = redis_connector
        self.config = Config
        self.last_request_time = 0
        self.min_delay = min_delay  # délai minimum entre deux requêtes (en secondes)
        self.proxies = proxies  # ex: {"http": "http://proxy:port", "https": "http://proxy:port"}
    
    def _rate_limit(self):
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_request_time = time.time()

    def _get_random_user_agent(self):
        return random.choice(self.USER_AGENTS)

    def _http_get_with_retry(self, url, headers=None, retries=3, backoff=1.5, timeout=10):
        """GET HTTP avec retry et backoff"""
        attempt = 0
        last_exc = None
        while attempt < retries:
            try:
                self._rate_limit()
                h = headers or {}
                if 'User-Agent' not in h:
                    h['User-Agent'] = self._get_random_user_agent()
                resp = requests.get(url, headers=h, timeout=timeout, proxies=self.proxies)
                resp.raise_for_status()
                return resp
            except Exception as e:
                last_exc = e
                logger.warning(f"HTTP GET failed (tentative {attempt+1}/{retries}): {e}")
                time.sleep(backoff * (attempt + 1))
                attempt += 1
        raise last_exc

    def get_html(self, url, method_order=None, max_wait=10) -> str:
        """Centralise la récupération du HTML avec fallback, rotation UA, proxy, retry, etc."""
        method_order = method_order or ['requests', 'scrapedo', 'selenium', 'playwright']
        last_exc = None
        for method in method_order:
            try:
                if method == 'scrapedo':
                    html = self.get_site_content_professional(url)
                    logger.info(f"HTML récupéré via Scrape.do")
                    return html
                elif method == 'requests':
                    resp = self._http_get_with_retry(url)
                    logger.info(f"HTML récupéré via requests")
                    return resp.text
                elif method == 'selenium':
                    html = self.get_site_content_selenium(url, max_wait=max_wait)
                    logger.info(f"HTML récupéré via Selenium")
                    return html
                elif method == 'playwright':
                    html = self.get_site_content_playwright(url, max_wait=max_wait)
                    logger.info(f"HTML récupéré via Playwright")
                    return html
            except Exception as e:
                logger.warning(f"Méthode {method} échouée: {e}")
                last_exc = e
        logger.error(f"Toutes les méthodes de récupération HTML ont échoué pour {url}")
        if last_exc is not None and isinstance(last_exc, BaseException):
            raise last_exc
        raise Exception("Impossible de récupérer le HTML")

    def scrape_with_scrapedo(self, url: str, params: dict = {}) -> dict:
        """Scraper avec Scrape.do"""
        try:
            if not self.config.HAS_SCRAPEDO:
                raise Exception("Scrape.do API key non configurée")
            
            api_url = "https://api.scrape.do/"
            params.update({
                'token': self.config.SCRAPEDO_API_KEY,
                'url': url
                # Ajouter d'autres paramètres scrape.do ici si besoin (super, geoCode, etc.)
            })
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            return {
                'success': True,
                'html': response.text,
                'status_code': response.status_code
            }
        except Exception as e:
            logger.error(f"Erreur Scrape.do: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_site_content_professional(self, url: str) -> str:
        """Récupérer le contenu d'un site avec Scrape.do"""
        try:
            result = self.scrape_with_scrapedo(url)
            if result['success']:
                return result['html']
            else:
                raise Exception(f"Scrape.do échoué: {result.get('error', 'Erreur inconnue')}")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du contenu: {e}")
            raise
    
    def get_site_content_selenium(self, url: str, max_wait: int = 10) -> str:
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent={self._get_random_user_agent()}")
            # Proxy support (si self.proxies)
            if self.proxies and 'http' in self.proxies:
                chrome_options.add_argument(f"--proxy-server={self.proxies['http']}")
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(max_wait)
            driver.get(url)
            time.sleep(2)
            html = driver.page_source
            driver.quit()
            return html
        except Exception as e:
            logger.error(f"Erreur Selenium: {e}")
            if 'driver' in locals():
                driver.quit()
            raise
    
    def get_site_content_playwright(self, url: str, max_wait: int = 10) -> str:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=self._get_random_user_agent())
                # Proxy support (si self.proxies)
                if self.proxies and 'http' in self.proxies:
                    context = browser.new_context(user_agent=self._get_random_user_agent(), proxy={"server": self.proxies['http']})
                page = context.new_page()
                page.set_default_timeout(max_wait * 1000)
                page.goto(url, wait_until='networkidle')
                html = page.content()
                browser.close()
                return html
        except Exception as e:
            logger.error(f"Erreur Playwright: {e}")
            raise
    
    def find_next_page_url(self, soup, base_url):
        """Trouver l'URL de la page suivante"""
        try:
            # Chercher les liens de pagination
            next_selectors = [
                'a[rel="next"]',
                'a.next',
                'a[aria-label*="next"]',
                'a[title*="next"]',
                '.pagination a:last-child',
                '.pager a:last-child'
            ]
            
            for selector in next_selectors:
                next_link = soup.select_one(selector)
                if next_link and next_link.get('href'):
                    return urljoin(base_url, next_link['href'])
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de la page suivante: {e}")
            return None
    
    def extract_full_article_content(self, element, title):
        """Extrait le contenu complet d'un article avec une approche hiérarchique"""
        content_parts = []
        
        # 1. Paragraphes principaux (priorité haute)
        paragraphs = element.find_all('p')
        for p in paragraphs:
            txt = p.get_text(strip=True)
            if txt and len(txt) > 15 and txt != title:
                # Éviter les doublons
                if not any(txt in existing for existing in content_parts):
                    content_parts.append(txt)
        
        # 2. Contenu des divs avec classe spécifique
        content_divs = element.find_all('div', class_=lambda x: x and any(keyword in x.lower() for keyword in [
            'content', 'text', 'body', 'article', 'post', 'entry', 'description', 'excerpt', 'summary'
        ]))
        for div in content_divs:
            txt = div.get_text(strip=True)
            if txt and len(txt) > 30 and txt != title:
                if not any(txt in existing for existing in content_parts):
                    content_parts.append(txt)
        
        # 3. Sous-titres et intertitres
        subtitles = element.find_all(['h2', 'h3', 'h4', 'h5', 'h6'])
        for subtitle in subtitles:
            txt = subtitle.get_text(strip=True)
            if txt and len(txt) > 10 and txt != title:
                if not any(txt in existing for existing in content_parts):
                    content_parts.append(txt)
        
        # 4. Listes (ul, ol)
        lists = element.find_all(['ul', 'ol'])
        for list_elem in lists:
            if isinstance(list_elem, Tag):
                items = list_elem.find_all('li')
                for item in items:
                    txt = item.get_text(strip=True)
                    if txt and len(txt) > 10:
                        if not any(txt in existing for existing in content_parts):
                            content_parts.append(txt)
        
        # 5. Spans avec contenu textuel
        spans = element.find_all('span')
        for span in spans:
            txt = span.get_text(strip=True)
            if txt and len(txt) > 20 and txt != title:
                if not any(txt in existing for existing in content_parts):
                    content_parts.append(txt)
        
        # 6. Contenu des sections
        sections = element.find_all('section')
        for section in sections:
            txt = section.get_text(strip=True)
            if txt and len(txt) > 50 and txt != title:
                if not any(txt in existing for existing in content_parts):
                    content_parts.append(txt)
        
        # 7. Contenu des articles imbriqués
        nested_articles = element.find_all('article')
        for nested_article in nested_articles:
            if nested_article != element:  # Éviter la récursion
                txt = nested_article.get_text(strip=True)
                if txt and len(txt) > 30 and txt != title:
                    if not any(txt in existing for existing in content_parts):
                        content_parts.append(txt)
        
        # Assembler le contenu
        content = '\n\n'.join(content_parts)
        
        # Nettoyer le contenu
        content = re.sub(r'\n{3,}', '\n\n', content)  # Supprimer les sauts de ligne multiples
        content = re.sub(r'\s+', ' ', content)  # Normaliser les espaces
        content = content.strip()
        
        return content
    
    def extract_article_from_url(self, article_url, base_url):
        """Extraire le contenu complet d'un article depuis son URL"""
        try:
            # Essayer d'abord avec requests
            try:
                response = requests.get(article_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                html = response.text
            except Exception:
                # Fallback vers Selenium
                html = self.get_site_content_selenium(article_url)
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extraire le titre
            title_selectors = ['h1', 'h2', '.title', '.article-title', '.post-title']
            title = ""
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            # Extraire le contenu principal
            content_selectors = [
                'article', '.article-content', '.post-content', '.entry-content',
                '.content', '.main-content', '.article-body', '.post-body'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = self.extract_full_article_content(content_elem, title)
                    if content and len(content) > 100:
                        break
            
            # Extraire la date
            date_selectors = ['time', '.date', '.published', '.post-date', '.article-date']
            date_str = ""
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date_str = date_elem.get_text(strip=True)
                    break
            
            return {
                'title': title,
                'content': content,
                'date': date_str,
                'url': article_url
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction depuis URL: {e}")
            return None
    
    def extract_articles_complete(self, site_url, method='scrapedo', max_articles=20):
        """Logique complète d'extraction d'articles avec fallback et IA"""
        try:
            if not site_url.startswith(('http://', 'https://')):
                site_url = 'https://' + site_url
            
            try:
                domain = urlparse(site_url).netloc
            except Exception:
                domain = 'unknown'
            
            articles = []
            url_to_scrape = site_url
            method_used = ''
            feedback = ''
            html_pages = []
            
            try:
                max_articles = int(max_articles)
                if max_articles < 1:
                    max_articles = 1
                if max_articles > 100:
                    max_articles = 100
            except Exception:
                max_articles = 20
            
            start_time = time.time()
            
            # Boucle de pagination (max 5 pages)
            for page_num in range(5):
                html = ""
                try:
                    # Utilisation de la méthode centralisée
                    html = self.get_html(url_to_scrape, method_order=[method, 'requests', 'selenium', 'playwright'])
                    method_used = method
                except Exception as e:
                    logger.warning(f"Toutes les méthodes de récupération HTML ont échoué: {e}")
                    feedback = f"Impossible de récupérer le contenu du site: {e}"
                    html = ""
                if not html:
                    break
                html_pages.append(html)
                
                try:
                    soup = BeautifulSoup(html, 'html.parser')
                    # Sélecteurs CSS pour trouver les articles
                    selectors = [
                        # Sélecteurs génériques
                        'article', 'div.news-item', 'div.post', 'div.blog-post',
                        'li.news-item', 'div.article', 'div.story',
                        # Sélecteurs supplémentaires pour sites tech/actualités
                        'div.news', 'div.actualite', 'div.news-article',
                        'li.article', 'div.entry', 'div.content-article',
                        'section.article', 'div.news-content', 'div.article-content',
                        'div.news-block', 'div.article-block', 'div.post-content',
                        'div.news-summary', 'div.article-summary', 'div.news-excerpt',
                        # Sélecteurs spécifiques pour sites français
                        'div.article-item', 'div.news-card', 'div.article-card',
                        'li.news', 'div.actualite-item', 'div.article-preview',
                        'div.article-teaser', 'div.news-teaser', 'div.article-snippet',
                        # Sélecteurs pour sites d'actualités
                        'div.article-list-item', 'div.news-list-item', 'div.article-entry',
                        'article.article', 'div.article-wrapper', 'div.news-wrapper',
                        # Sélecteurs pour sites de blogs
                        'div.blog-entry', 'div.post-item', 'div.blog-item',
                        'li.blog-post', 'div.blog-article', 'div.post-article'
                    ]
                    
                    logger.info(f"Page {page_num + 1}: Recherche d'articles avec {len(selectors)} sélecteurs")
                    
                    # Set pour éviter les doublons
                    seen_titles = set()
                    
                    for selector in selectors:
                        elements = soup.select(selector)
                        logger.info(f"Sélecteur '{selector}': {len(elements)} éléments trouvés")
                        
                        for element in elements[:max_articles]:  # Limiter par page
                            try:
                                title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
                                link_elem = element.find('a')
                                
                                if title_elem:  # Seulement vérifier le titre, pas le lien
                                    title = title_elem.get_text(strip=True)
                                    
                                    # Filtrer les titres trop courts ou non pertinents
                                    if len(title) < 10 or title.lower() in ['accueil', 'menu', 'navigation', 'footer', 'boutique', 'services']:
                                        continue
                                    
                                    # Éviter les doublons
                                    title_normalized = title.lower().strip()
                                    if title_normalized in seen_titles:
                                        logger.info(f"Titre dupliqué ignoré: {title[:50]}...")
                                        continue
                                    seen_titles.add(title_normalized)
                                    
                                    logger.info(f"Titre trouvé: {title[:50]}...")
                                    url = ""
                                    if link_elem and isinstance(link_elem, Tag):
                                        href_value = link_elem.get('href')
                                        if href_value:
                                            url = str(href_value)
                                            try:
                                                url = urljoin(url_to_scrape, url)
                                            except Exception:
                                                url = ""
                                    
                                    if not url:  # Si pas de lien trouvé, utiliser l'URL courante
                                        url = url_to_scrape
                                    
                                    if title:  # Ajouter l'article si on a au moins un titre
                                        # Extraction du contenu avec approche hiérarchique
                                        content = self.extract_full_article_content(element, title)
                                        
                                        # Si le contenu est insuffisant, essayer d'extraire depuis l'URL de l'article
                                        if not content or len(content) < 100:
                                            if url and url != url_to_scrape:
                                                logger.info(f"Contenu insuffisant, tentative d'extraction depuis l'URL: {url}")
                                                full_article = self.extract_article_from_url(url, url_to_scrape)
                                                if full_article and full_article.get('content'):
                                                    content = full_article['content']
                                                    # Mettre à jour le titre si meilleur
                                                    if full_article.get('title') and len(full_article['title']) > len(title):
                                                        title = full_article['title']
                                        
                                        # Vérifier que le contenu est suffisant
                                        if content and len(content) > 30:  # Réduit pour être moins strict
                                            # Ajouter une date si disponible
                                            date_str = ""
                                            date_elem = element.find(['time', 'span.date', 'div.date', 'span.timestamp', 'span.time', 'div.time'])
                                            if date_elem:
                                                date_str = date_elem.get_text(strip=True)
                                                # Nettoyer la date
                                                date_str = re.sub(r'[^\w\s\-/]', '', date_str)
                                            
                                            article_data = {
                                                'title': title,
                                                'url': url,
                                                'content': content
                                            }
                                            
                                            if date_str:
                                                article_data['date'] = date_str
                                            
                                            articles.append(article_data)
                                            logger.info(f"Article ajouté: {title[:50]}... (contenu: {len(content)} chars)")
                                        else:
                                            logger.info(f"Article ignoré (contenu insuffisant): {title[:50]}...")
                            
                            except Exception as e:
                                logger.warning(f"Erreur lors de l'extraction d'un article: {e}")
                                continue
                        
                        if len(articles) >= max_articles:
                            break
                    
                    if len(articles) >= max_articles:
                        break
                    
                    next_url = self.find_next_page_url(soup, url_to_scrape)
                    if not next_url or next_url == url_to_scrape:
                        break
                    url_to_scrape = next_url
                    
                except Exception as e:
                    logger.error(f"Erreur lors du parsing HTML: {e}")
                    break
            
            # Fallback IA si aucun article trouvé
            if not articles and html_pages:
                logger.info("Aucun article trouvé, fallback extraction IA...")
                logger.info(f"HTML de la première page (premiers 500 caractères): {html_pages[0][:500]}")
                
                try:
                    llm = ChatGroq(model="llama3-8b-8192", temperature=0.0)
                    prompt = f"""
Voici le HTML d'une page d'actualité :
---
{html_pages[0][:10000]}
---
Ta mission : extraire tous les articles (titre, url, date, contenu principal) et retourne une liste JSON. Ne génère aucun code, ne donne que les données extraites.
"""
                    ia_response = llm.invoke(prompt)
                    try:
                        ia_articles = json.loads(ia_response.text() if hasattr(ia_response, 'text') else str(ia_response))
                        if isinstance(ia_articles, list):
                            articles = ia_articles
                            method_used += "+ia-fallback"
                            feedback += "Extraction IA fallback utilisée. "
                    except Exception as parse_err:
                        logger.warning(f"Erreur parsing JSON IA fallback: {parse_err}")
                        logger.warning(f"Réponse brute IA fallback: {ia_response}")
                        
                        # Tentative d'extraction JSON depuis le texte
                        try:
                            response_text = ia_response.text() if hasattr(ia_response, 'text') else str(ia_response)
                            # Chercher du JSON entre backticks ou dans le texte
                            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response_text, re.DOTALL)
                            if json_match:
                                json_str = json_match.group(1)
                                ia_articles = json.loads(json_str)
                                if isinstance(ia_articles, list):
                                    articles = ia_articles
                                    method_used += "+ia-fallback"
                                    feedback += "Extraction IA fallback utilisée (JSON extrait). "
                            else:
                                # Chercher directement un tableau JSON dans le texte
                                json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
                                if json_match:
                                    json_str = json_match.group(0)
                                    ia_articles = json.loads(json_str)
                                    if isinstance(ia_articles, list):
                                        articles = ia_articles
                                        method_used += "+ia-fallback"
                                        feedback += "Extraction IA fallback utilisée (JSON trouvé). "
                        except Exception as extract_err:
                            logger.warning(f"Échec extraction JSON depuis texte: {extract_err}")
                            feedback += f"IA fallback n'a pas pu extraire les articles."
                            
                except Exception as ia_err:
                    logger.error(f"Erreur lors du fallback IA: {ia_err}")
                    feedback += f"Erreur IA fallback: {ia_err}"
            
            # Résumé IA pour chaque article (si pas déjà présent)
            if self.config.HAS_GROQ and articles:
                try:
                    llm = ChatGroq(model="llama3-8b-8192", temperature=0.0)
                    max_resume_articles = min(10, len(articles))  # Limite adaptative
                    
                    logger.info(f"Génération des résumés IA pour {max_resume_articles} articles...")
                    
                    for idx, article in enumerate(articles[:max_resume_articles]):
                        if 'resume' not in article or not article.get('resume'):
                            try:
                                # Préparer le contenu pour l'IA
                                content_for_ia = article.get('content', '')
                                if not content_for_ia or len(content_for_ia.strip()) < 50:
                                    article['resume'] = "Résumé non disponible (contenu insuffisant)."
                                    continue
                                
                                # Limiter la taille du contenu pour éviter les timeouts
                                content_for_ia = content_for_ia[:800]
                                
                                prompt = (
                                    "Résume ce texte d'actualité en 2-3 phrases claires et synthétiques. "
                                    "Ne mets pas de phrase d'introduction comme 'Voici un résumé' ou 'Résumé :'. "
                                    "Va directement au contenu du résumé :\n\n"
                                    f"{content_for_ia}"
                                )
                                
                                ia_response = llm.invoke(prompt)
                                resume = ia_response.text() if hasattr(ia_response, 'text') else str(ia_response)
                                
                                # Nettoyer le résumé
                                resume = resume.strip()
                                # Supprimer les phrases d'introduction courantes
                                resume = re.sub(r"^(voici un résumé[^:]*:|résumé\s*:)\s*", "", resume, flags=re.IGNORECASE)
                                resume = re.sub(r"^(ce texte parle de|il s'agit de|l'article traite de)\s*", "", resume, flags=re.IGNORECASE)
                                
                                # Vérifier que le résumé n'est pas vide après nettoyage
                                if resume and len(resume.strip()) > 10:
                                    article['resume'] = resume[:350] + '...' if len(resume) > 350 else resume
                                else:
                                    article['resume'] = "Résumé non disponible (réponse IA invalide)."
                                    
                            except Exception as e:
                                logger.warning(f"Erreur résumé IA pour article {idx}: {e}")
                                article['resume'] = "Résumé non disponible (erreur technique)."
                            
                            # Pause plus courte entre les appels IA
                            time.sleep(0.5)
                    
                    # Pour les articles restants, ajouter un message explicatif
                    for idx in range(max_resume_articles, len(articles)):
                        articles[idx]['resume'] = "Résumé non disponible (limite de traitement atteinte)."
                        
                except Exception as e:
                    logger.error(f"Erreur globale lors de la génération des résumés IA: {e}")
                    # Ajouter un résumé par défaut pour tous les articles
                    for article in articles:
                        if 'resume' not in article or not article.get('resume'):
                            article['resume'] = "Résumé non disponible (service IA indisponible)."
            else:
                # Si Groq n'est pas disponible, ajouter un message explicatif
                for article in articles:
                    if 'resume' not in article or not article.get('resume'):
                        article['resume'] = "Résumé non disponible (service IA non configuré)."
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'articles': articles,
                'total_articles': len(articles),
                'method_used': method_used,
                'domain': domain,
                'feedback': feedback,
                'processing_time': f"{processing_time:.2f}s",
                'articles_with_summaries': sum(1 for a in articles if a.get('resume') and 'non disponible' not in a.get('resume', ''))
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction complète: {e}")
            return {
                'success': False,
                'error': str(e),
                'articles': [],
                'total_articles': 0
            }
    
    def log_scraping_history(self, user_id, url, method, articles_count, status):
        """Enregistrer l'historique de scraping"""
        try:
            query = """
                INSERT INTO scraping_history (user_id, url, method, articles_count, status, timestamp)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            self.db.execute_query(query, (user_id, url, method, articles_count, status))
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'historique: {e}")
    
    def get_user_usage_stats(self, username):
        """Récupérer les statistiques d'utilisation d'un utilisateur"""
        try:
            # Récupérer l'ID de l'utilisateur
            user_query = "SELECT id FROM users WHERE username = %s"
            user_result = self.db.execute_query(user_query, (username,))
            if not user_result:
                return {}
            
            user_id = user_result[0]['id']
            
            # Statistiques générales
            stats_query = """
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_requests,
                    SUM(articles_count) as total_articles,
                    MIN(created_at) as first_request,
                    MAX(created_at) as last_request
                FROM scraping_history 
                WHERE user_id = %s
            """
            stats_result = self.db.execute_query(stats_query, (user_id,))
            general_stats = stats_result[0] if stats_result else {}
            
            # Domaines les plus utilisés
            domains_query = """
                SELECT 
                    SUBSTRING_INDEX(SUBSTRING_INDEX(url, '/', 3), '://', -1) as domain,
                    COUNT(*) as count
                FROM scraping_history 
                WHERE user_id = %s
                GROUP BY domain
                ORDER BY count DESC
                LIMIT 10
            """
            domains_result = self.db.execute_query(domains_query, (user_id,))
            
            # Méthodes utilisées
            methods_query = """
                SELECT 
                    method,
                    COUNT(*) as count
                FROM scraping_history 
                WHERE user_id = %s
                GROUP BY method
                ORDER BY count DESC
            """
            methods_result = self.db.execute_query(methods_query, (user_id,))
            
            # Historique récent (dernières 10 requêtes)
            recent_query = """
                SELECT 
                    url,
                    method,
                    articles_count,
                    status,
                    created_at
                FROM scraping_history 
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 10
            """
            recent_result = self.db.execute_query(recent_query, (user_id,))
            
            return {
                'general_stats': general_stats,
                'top_domains': domains_result,
                'methods_used': methods_result,
                'recent_requests': recent_result
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {}

# Instance globale
scraping_service = ScrapingService() 