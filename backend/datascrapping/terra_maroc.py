import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import re
import os
import json

BASE_URL = "https://terra-maroc.com"
TARGET_URL = "https://terra-maroc.com/artisanat/histoire-savoir-faire"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text.encode('utf-8', 'ignore').decode('utf-8')

def extract_historical_content(soup):
    data = []

    main_content = soup.find('main') or soup.find('div', class_=lambda x: x and ('content' in x.lower() or 'main' in x.lower())) or soup

    main_title = clean_text(main_content.find('h1').get_text()) if main_content.find('h1') else "Histoire de l'artisanat marocain"

    intro_paragraphs = [clean_text(p.get_text()) for p in main_content.find_all('p', recursive=False)[:3]]
    intro_text = '\n'.join([p for p in intro_paragraphs if p and len(p) > 30])

    history_sections = []
    for h2 in main_content.find_all(['h2', 'h3']):
        section_title = clean_text(h2.get_text())
        section_content = []
        next_node = h2.find_next_sibling()

        while next_node and next_node.name not in ['h2', 'h3', 'div', 'footer', 'main']:
            if next_node.name == 'p':
                section_content.append(clean_text(next_node.get_text()))
            elif next_node.name == 'ul':
                section_content.extend([f"- {clean_text(li.get_text())}" for li in next_node.find_all('li')])
            next_node = next_node.find_next_sibling()

        if section_content:
            history_sections.append({
                'sous_titre': section_title,
                'contenu': '\n'.join(section_content)
            })

    data.append({
        'titre_principal': main_title,
        'introduction': intro_text,
        'sections_historiques': history_sections,
        'source': TARGET_URL
    })

    return data

def main():
    print(f"Scraping de la page: {TARGET_URL}")

    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Erreur lors de la récupération de la page: {e}")
        return

    historical_data = extract_historical_content(soup)

    # Affichage aperçu dans la console
    print("\n--- Aperçu des sections extraites ---")
    for section in historical_data[0]['sections_historiques']:
        print(f"Sous-titre : {section['sous_titre']}")
        print(f"Contenu (extrait 200 caractères) :\n{section['contenu'][:200]}...\n")

    # Export JSON complet (structure riche)
    json_file = "histoire_artisanat_marocain.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(historical_data, f, ensure_ascii=False, indent=4)
    print(f"Données JSON sauvegardées dans {json_file}")

    # Export CSV simplifié (avec une ligne par section)
    flat_data = []
    for item in historical_data:
        for section in item['sections_historiques']:
            flat_data.append({
                'titre_principal': item['titre_principal'],
                'introduction': item['introduction'],
                'sous_titre': section['sous_titre'],
                'contenu': section['contenu'],
                'source': item['source']
            })

    df = pd.DataFrame(flat_data)
    df = df.dropna(subset=['contenu'])
    df = df[df['contenu'].str.len() > 50]

    csv_file = "histoire_artisanat_marocain.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"Données CSV sauvegardées dans {csv_file}")
    print(f"Nombre de sections historiques extraites : {len(df)}")

if __name__ == "__main__":
    main()
