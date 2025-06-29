#!/usr/bin/env python3
"""
Script de test pour vérifier les améliorations du scraping et des résumés IA
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8080"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
SCRAPING_URL = f"{BASE_URL}/api/scraping/extract"

# Credentials de test
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login():
    """Connexion pour obtenir un token JWT"""
    try:
        response = requests.post(LOGIN_URL, json={
            'username': ADMIN_USERNAME,
            'password': ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('access_token')
        
        print(f"❌ Erreur de connexion: {response.status_code}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de la connexion: {e}")
        return None

def test_scraping_with_summaries(token):
    """Test du scraping avec vérification des résumés IA"""
    headers = {'Authorization': f'Bearer {token}'}
    
    # Sites de test avec différents types de contenu
    test_sites = [
        {
            'url': 'https://www.lemonde.fr',
            'name': 'Le Monde',
            'expected_articles': 1
        },
        {
            'url': 'https://www.lefigaro.fr',
            'name': 'Le Figaro',
            'expected_articles': 3
        },
        {
            'url': 'https://www.liberation.fr',
            'name': 'Libération',
            'expected_articles': 2
        }
    ]
    
    print("🕷️ Test des améliorations du scraping...")
    print("=" * 60)
    
    total_articles = 0
    total_with_summaries = 0
    total_processing_time = 0
    
    for i, site in enumerate(test_sites, 1):
        print(f"\n📄 Test {i}/3: {site['name']} ({site['url']})")
        
        try:
            start_time = time.time()
            
            response = requests.post(SCRAPING_URL, 
                json={
                    'url': site['url'], 
                    'method': 'scrapedo', 
                    'max_articles': site['expected_articles']
                },
                headers=headers
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    articles = data.get('articles', [])
                    articles_count = len(articles)
                    articles_with_summaries = data.get('articles_with_summaries', 0)
                    method_used = data.get('method_used', 'unknown')
                    feedback = data.get('feedback', '')
                    processing_time_api = data.get('processing_time', 'N/A')
                    
                    print(f"  ✅ Succès")
                    print(f"    📊 Articles extraits: {articles_count}")
                    print(f"    🤖 Articles avec résumés IA: {articles_with_summaries}")
                    print(f"    ⚙️ Méthode utilisée: {method_used}")
                    print(f"    ⏱️ Temps de traitement: {processing_time_api}")
                    print(f"    💬 Feedback: {feedback}")
                    
                    # Analyser la qualité des articles
                    if articles:
                        print(f"    📝 Analyse des articles:")
                        for idx, article in enumerate(articles[:3], 1):  # Analyser les 3 premiers
                            title = article.get('title', 'Sans titre')
                            content_length = len(article.get('content', ''))
                            resume = article.get('resume', '')
                            has_resume = 'non disponible' not in resume.lower() if resume else False
                            
                            print(f"      {idx}. {title[:50]}...")
                            print(f"         Contenu: {content_length} caractères")
                            print(f"         Résumé IA: {'✅' if has_resume else '❌'} {resume[:80]}...")
                    
                    total_articles += articles_count
                    total_with_summaries += articles_with_summaries
                    total_processing_time += processing_time
                    
                else:
                    print(f"  ❌ Échec: {data.get('message', 'Erreur inconnue')}")
            else:
                print(f"  ❌ Erreur HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
        
        # Pause entre les tests
        time.sleep(2)
    
    # Résumé global
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES AMÉLIORATIONS")
    print("=" * 60)
    
    print(f"📈 Total articles extraits: {total_articles}")
    print(f"🤖 Articles avec résumés IA: {total_with_summaries}")
    print(f"📊 Taux de résumés IA: {(total_with_summaries/total_articles*100):.1f}%" if total_articles > 0 else "N/A")
    print(f"⏱️ Temps de traitement moyen: {(total_processing_time/3):.2f}s")
    
    # Évaluation de la qualité
    print(f"\n🎯 Évaluation de la qualité:")
    if total_articles > 0:
        summary_rate = (total_with_summaries/total_articles*100)
        if summary_rate >= 80:
            print(f"  ✅ Excellente qualité des résumés IA ({summary_rate:.1f}%)")
        elif summary_rate >= 60:
            print(f"  ⚠️ Bonne qualité des résumés IA ({summary_rate:.1f}%)")
        else:
            print(f"  ❌ Qualité des résumés IA à améliorer ({summary_rate:.1f}%)")
    
    if total_processing_time < 30:
        print(f"  ✅ Performance excellente (temps total: {total_processing_time:.1f}s)")
    elif total_processing_time < 60:
        print(f"  ⚠️ Performance correcte (temps total: {total_processing_time:.1f}s)")
    else:
        print(f"  ❌ Performance à améliorer (temps total: {total_processing_time:.1f}s)")

def test_specific_improvements(token):
    """Test spécifique des améliorations"""
    headers = {'Authorization': f'Bearer {token}'}
    
    print("\n🔧 Test des améliorations spécifiques...")
    print("=" * 60)
    
    # Test avec un site qui devrait donner de bons résultats
    test_url = "https://www.lemonde.fr"
    
    try:
        print(f"📄 Test détaillé: {test_url}")
        
        response = requests.post(SCRAPING_URL, 
            json={'url': test_url, 'method': 'scrapedo', 'max_articles': 5},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                articles = data.get('articles', [])
                
                print(f"✅ Extraction réussie: {len(articles)} articles")
                
                # Analyser chaque article en détail
                for idx, article in enumerate(articles, 1):
                    print(f"\n📝 Article {idx}:")
                    print(f"   Titre: {article.get('title', 'N/A')}")
                    print(f"   URL: {article.get('url', 'N/A')}")
                    print(f"   Contenu: {len(article.get('content', ''))} caractères")
                    
                    resume = article.get('resume', '')
                    if resume and 'non disponible' not in resume.lower():
                        print(f"   Résumé IA: ✅ {resume}")
                    else:
                        print(f"   Résumé IA: ❌ {resume}")
                    
                    # Vérifier la présence d'une date
                    if article.get('date'):
                        print(f"   Date: ✅ {article.get('date')}")
                    else:
                        print(f"   Date: ❌ Non trouvée")
                
                # Vérifier les nouvelles métriques
                processing_time = data.get('processing_time', 'N/A')
                articles_with_summaries = data.get('articles_with_summaries', 0)
                
                print(f"\n📊 Nouvelles métriques:")
                print(f"   Temps de traitement: {processing_time}")
                print(f"   Articles avec résumés: {articles_with_summaries}/{len(articles)}")
                
            else:
                print(f"❌ Échec: {data.get('message', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("🚀 Test des améliorations du scraping FinData IA-M.K")
    print("=" * 60)
    
    # Connexion
    print("🔐 Connexion...")
    token = login()
    if not token:
        print("❌ Impossible de se connecter. Arrêt du test.")
        return
    
    print("✅ Connexion réussie!")
    
    # Test du scraping avec résumés
    test_scraping_with_summaries(token)
    
    # Test spécifique des améliorations
    test_specific_improvements(token)
    
    print("\n🎉 Test des améliorations terminé!")
    print("💡 Les améliorations incluent:")
    print("   - Résumés IA plus fiables")
    print("   - Meilleure extraction de contenu")
    print("   - Gestion d'erreurs améliorée")
    print("   - Métriques de performance")

if __name__ == "__main__":
    main() 