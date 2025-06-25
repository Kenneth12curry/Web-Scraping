import requests
import json

# Nom du modèle Llama 3.1 sur HuggingFace (à adapter si besoin)
MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"

def generate_scraping_prompt(site_name: str) -> str:
    return f"""
Tu es un expert en scraping web. Génère un script Python utilisant requests et BeautifulSoup pour extraire les informations clés du site fintech suivant : {site_name}.
Le script doit :
- Se connecter à la page d'accueil
- Extraire les titres des articles récents
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
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    result = response.json()
    return result.get('response', str(result))

def main():
    site = "https://www.exemple-fintech.com"  # Remplace par le site de ton choix
    prompt = generate_scraping_prompt(site)
    print("Prompt envoyé :\n", prompt)
    response = query_llama_local(prompt)
    print("\nRéponse du modèle :\n", response)

if __name__ == "__main__":
    main() 