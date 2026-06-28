import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import time

# Configuration de base
BASE_URL = "https://www.voyage-maroc.com"
START_URL = "https://www.voyage-maroc.com/infos-pratiques/Arts-culture"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Fonction pour récupérer le contenu d'une page
def get_page(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Erreur lors de la récupération de {url}: {e}")
        return None

# Fonction pour extraire les données principales
def extract_main_data(soup):
    data = []
    
    # Section principale
    main_content = soup.find('div', class_='main-content') or soup
    
    # Extraction des articles et sections
    articles = main_content.find_all(['article', 'div'], class_=lambda x: x and ('article' in x or 'content' in x))
    
    for article in articles:
        title = article.find(['h1', 'h2', 'h3'])
        title_text = title.get_text(strip=True) if title else "Sans titre"
        
        content = article.get_text(' ', strip=True)
        
        # Vérifier si le contenu concerne nos sujets d'intérêt
        keywords = ['artisanat', 'artisanal', 'artisan', 'vêtement', 'habit', 'textile', 
                   'tissage', 'poterie', 'bois', 'cuir', 'métal', 'bijou', 'histoire']
        
        if any(keyword.lower() in content.lower() for keyword in keywords):
            links = [urljoin(BASE_URL, a['href']) for a in article.find_all('a', href=True)]
            
            data.append({
                'type': 'article',
                'titre': title_text,
                'contenu': content,
                'liens': links
            })
    
    return data

# Fonction pour extraire l'historique de l'artisanat
def extract_history_data(soup):
    history_data = []
    
    # Recherche spécifique de sections sur l'histoire
    history_sections = soup.find_all(['section', 'div'], class_=lambda x: x and ('history' in x.lower() or 'historique' in x.lower()))
    
    for section in history_sections:
        title = section.find(['h2', 'h3', 'h4']) or section.find_previous(['h1', 'h2', 'h3'])
        title_text = title.get_text(strip=True) if title else "Histoire de l'artisanat"
        
        content = section.get_text(' ', strip=True)
        
        if 'artisanat' in content.lower():
            history_data.append({
                'type': 'histoire',
                'titre': title_text,
                'contenu': content
            })
    
    return history_data

# Fonction pour explorer les liens connexes
def explore_related_links(links, max_pages=3):
    related_data = []
    visited = set()
    
    for link in links[:max_pages]:
        if link in visited:
            continue
            
        visited.add(link)
        print(f"Exploration de la page liée: {link}")
        
        soup = get_page(link)
        if not soup:
            continue
            
        # Extraction des données des pages liées
        data = extract_main_data(soup)
        history = extract_history_data(soup)
        
        related_data.extend(data)
        related_data.extend(history)
        
        time.sleep(2)  # Respect du serveur
    
    return related_data

# Fonction principale
def main():
    # Récupération de la page initiale
    print(f"Scraping de la page principale: {START_URL}")
    soup = get_page(START_URL)
    
    if not soup:
        return
    
    # Extraction des données principales
    main_data = extract_main_data(soup)
    history_data = extract_history_data(soup)
    
    # Collecte des liens à explorer
    all_links = set()
    for item in main_data:
        for link in item['liens']:
            if BASE_URL in link:
                all_links.add(link)
    
    # Exploration des liens connexes
    related_data = explore_related_links(list(all_links))
    
    # Combinaison de toutes les données
    all_data = main_data + history_data + related_data
    
    # Création du DataFrame
    df = pd.DataFrame(all_data)
    
    # Nettoyage des données
    df = df.drop_duplicates(subset=['contenu'])
    df['contenu'] = df['contenu'].str.replace('\s+', ' ', regex=True)
    
    # Sauvegarde
    df.to_csv('artisanat_marocain.csv', index=False, encoding='utf-8-sig')
    print("Scraping terminé. Données sauvegardées dans artisanat_marocain.csv")

if __name__ == "__main__":
    main()