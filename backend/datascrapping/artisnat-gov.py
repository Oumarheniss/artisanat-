import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv

BASE_URL = 'https://www.visitmorocco.com/fr/decouvrir-le-maroc/artisanat-traditionnel-revisite'
OUTPUT_FILE = 'artisanat_marocain.csv'

CATEGORIES = {
    'tapis': ['tapis', 'kilim', 'azilal', 'boucherouite', 'hanbel'],
    'caftan': ['caftan', 'djellaba', 'gandoura', 'haïk', 'habit traditionnel'],
    'bijoux': ['bijoux', 'bracelet', 'collier', 'argent', 'berbère', 'bague'],
    'poterie': ['poterie', 'céramique', 'terre cuite'],
    'zellige': ['zellige', 'mosaïque', 'carreaux', 'carrelage'],
    'cuir': ['cuir', 'babouche', 'sac', 'ceinture', 'tannerie', 'maroquinerie'],
    'bois': ['bois', 'sculpture', 'marqueterie', 'thuya'],
    'métal': ['laiton', 'fer forgé', 'lanterne', 'métal', 'dinanderie']
}

def clean_text(text):
    return ' '.join(text.strip().split())

def determine_category(text):
    text = text.lower()
    scores = {}
    for cat, keywords in CATEGORIES.items():
        scores[cat] = sum(text.count(kw) for kw in keywords)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else 'autre'

def extract_artisanat_data(soup, url_source):
    data = []
    for h3 in soup.find_all('h3'):
        section = h3.find_parent(['section', 'div', 'article']) or soup
        title_text = clean_text(h3.get_text())
        content = clean_text(' '.join(p.get_text() for p in section.find_all('p')))
        if len(content) < 100:
            continue

        category = determine_category(title_text + ' ' + content)
        if category == 'autre':
            continue

        images = [urljoin(BASE_URL, img['src']) for img in section.find_all('img')[:3] if img.get('src')]
        links = [urljoin(BASE_URL, a['href']) for a in section.find_all('a', href=True)[:3]]

        data.append({
            'catégorie': category,
            'titre': title_text,
            'description': content[:1000],
            'images': ' | '.join(images),
            'liens': ' | '.join(links),
            'source': url_source
        })
    return data

def write_to_csv(data, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['catégorie', 'titre', 'description', 'images', 'liens', 'source'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def main():
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        print("Erreur lors du chargement de la page.")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    data = extract_artisanat_data(soup, BASE_URL)
    write_to_csv(data, OUTPUT_FILE)
    print(f"✅ Données extraites et enregistrées dans {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
