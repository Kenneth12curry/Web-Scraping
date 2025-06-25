from flask import Flask, render_template_string, request
import requests as req
import json
import tempfile
import subprocess
import sys
import re
from bs4 import BeautifulSoup
import textwrap

def get_html_snippet(url: str, max_length: int = 3000) -> str:
    try:
        resp = req.get(url, timeout=10)
        html = resp.text
        # Utilise BeautifulSoup pour extraire le premier <article> et son contexte
        soup = BeautifulSoup(html, 'html.parser')
        article = soup.find('article')
        if article:
            # On prend le parent direct (souvent <main> ou <div>) pour donner du contexte
            parent = article.parent
            snippet = str(parent) if parent else str(article)
            # Limite la taille de l'extrait
            return snippet[:max_length]
        # Sinon, fallback sur le début du HTML
        return html[:max_length]
    except Exception as e:
        return f"Erreur lors du téléchargement du HTML : {e}"

def is_dynamic_html(html: str) -> bool:
    # Détection simple : beaucoup de <script>, présence de 'window.__', 'React', etc.
    script_count = html.count('<script')
    dynamic_keywords = ['window.__', 'React', 'angular', 'vue', 'data-layer', 'app-root']
    if script_count > 10:
        return True
    for kw in dynamic_keywords:
        if kw in html:
            return True
    return False

def generate_scraping_prompt_with_html(site_name: str, html_snippet: str, use_selenium: bool = False) -> str:
    if use_selenium:
        return f"""
Tu es un expert en scraping web. Voici un extrait du HTML de la page d'accueil du site {site_name} :
{html_snippet}

Génère un script Python utilisant Selenium (avec Chrome headless) et BeautifulSoup pour extraire les titres et contenus de tous les articles récents du site, même si le contenu est généré par JavaScript. Le script doit :
- Charger la page avec Selenium pour exécuter le JavaScript
- Extraire les titres et contenus des articles sur chaque page
- Pour chaque article, essaye de trouver le titre dans <h1> ou <h2> avec la classe entry-title. Vérifie que chaque élément intermédiaire (header, h1, h2, entry-title, entry-content, etc.) existe avant d'accéder à ses attributs ou à .text. Si un élément n'existe pas, passe à l'article suivant sans lever d'exception.
- Suivre la pagination (page suivante) jusqu'à la dernière page
- Vérifier que chaque élément existe avant d'accéder à ses attributs, et ignorer les articles incomplets
- Afficher les résultats dans la console
N'inclus pas d'explications, seulement le code Python.
"""
    else:
        return f"""
Tu es un expert en scraping web. Voici un extrait du HTML de la page d'accueil du site {site_name} :
{html_snippet}

Génère un script Python utilisant requests et BeautifulSoup pour extraire les titres et contenus de tous les articles récents du site. Le script doit :
- S'adapter à la structure HTML fournie
- Suivre la pagination (page suivante) jusqu'à la dernière page
- Vérifier que chaque élément existe avant d'accéder à ses attributs, et ignorer les articles incomplets
- Afficher les résultats dans la console
N'inclus pas d'explications, seulement le code Python.
"""

def query_llama_local(prompt: str, model: str = "llama3") -> str:
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = req.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    result = response.json()
    return result.get('response', str(result))

def execute_generated_code(code: str) -> str:
    # Exécute le code Python généré dans un fichier temporaire et capture la sortie
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        result = subprocess.run([sys.executable, tmp_path], capture_output=True, text=True, timeout=30)
        output = result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        output = f"Erreur lors de l'exécution du code généré : {e}"
    return output

def clean_generated_code(code: str) -> str:
    # Cherche le bloc de code Python entre ```python ... ``` ou ``` ... ```
    match = re.search(r"```python(.*?)```", code, re.DOTALL)
    if not match:
        match = re.search(r"```(.*?)```", code, re.DOTALL)
    if match:
        code_block = match.group(1).strip()
        return textwrap.dedent(code_block)
    # Sinon, supprime les lignes non valides (ex: phrases d'intro)
    lines = code.strip().splitlines()
    cleaned = []
    for line in lines:
        if line.strip().startswith('import') or line.strip().startswith('from') or '=' in line or line.strip().startswith('for') or line.strip().startswith('def') or line.strip().startswith('print') or line.strip().startswith('soup'):
            cleaned.append(line)
    return textwrap.dedent('\n'.join(cleaned))

app = Flask(__name__)

HTML = '''
<!doctype html>
<title>Scraper Fintech avec Llama 3.1</title>
<h2>Générer un script de scraping pour un site fintech</h2>
<form method="post">
  URL du site fintech : <input name="site_url" type="text" size="50" required>
  <input type="submit" value="Générer et exécuter">
</form>
{% if prompt %}
  <h3>Prompt envoyé :</h3>
  <pre>{{ prompt }}</pre>
{% endif %}
{% if response %}
  <h3>Code généré :</h3>
  <pre>{{ response }}</pre>
{% endif %}
{% if result %}
  <h3>Résultats extraits :</h3>
  <pre>{{ result }}</pre>
{% endif %}
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    prompt = response = result = None
    if request.method == 'POST':
        site_url = request.form['site_url']
        html_snippet = get_html_snippet(site_url)
        use_selenium = is_dynamic_html(html_snippet)
        prompt = generate_scraping_prompt_with_html(site_url, html_snippet, use_selenium)
        try:
            response = query_llama_local(prompt)
            cleaned_code = clean_generated_code(response)
            result = execute_generated_code(cleaned_code)
        except Exception as e:
            result = f"Erreur lors de la requête ou de l'exécution : {e}"
    return render_template_string(HTML, prompt=prompt, response=response, result=result)

if __name__ == '__main__':
    app.run(debug=True) 