import os
import time
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from urllib.parse import urljoin, urlparse
from datetime import datetime

# Configuration
BASE_URL = "https://mda.gov.ma/fr/"
OUTPUT_DIR = "mda_artisanat_complet"
LOG_FILE = os.path.join(OUTPUT_DIR, "scraping_log.txt")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9"
}

# Catégories principales d'artisanat
MAIN_CATEGORIES = {
    "arts_de_terre": "artisanat-du-maroc/les-arts-de-terre/",
    "arts_de_cuir": "artisanat-du-maroc/les-arts-de-cuir/",
    "arts_du_bois": "artisanat-du-maroc/les-arts-du-bois/",
    "arts_textiles": "artisanat-du-maroc/les-arts-du-textiles/",
    "arts_du_metal": "artisanat-du-maroc/les-arts-du-metal/",
    "arts_bijouterie": "artisanat-du-maroc/les-arts-de-la-bijouterie/",
    "arts_bien_etre": "artisanat-du-maroc/les-arts-du-bien-etre/",
    "arts_vannerie": "artisanat-du-maroc/les-arts-de-la-vannerie/",
    "autres_arts": "artisanat-du-maroc/les-autres-arts/"
}

# Sections supplémentaires
ADDITIONAL_SECTIONS = {
    "publications_statistiques": "documentation-et-informations/ressources/publications-et-statistiques/",
    "infrastructures": "art-de-vivre/infrastructures/",
    "programmes_preservation": "art-de-vivre/preservation-des-metiers/",
    "qualite_innovation": "art-de-vivre/qualite-et-innovation/",
    "appui_production": "art-de-vivre/appui-a-la-production/",
    "formation_metiers": "programmes-et-services-mda/formation-metiers/",
    "promotion_commercialisation": "programmes-et-services-mda/promotion-et-commercialisation/"
}

def setup_logging():
    """Initialise le fichier de log"""
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Début du scraping MDA - {datetime.now().isoformat()}\n\n")

def log_message(message):
    """Enregistre un message dans le log"""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")
    print(message)

def fetch_page(url):
    """Récupère le contenu HTML d'une page avec gestion d'erreurs améliorée"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        
        # Vérification du contenu
        if len(response.text) < 5000:
            raise ValueError("Contenu trop court - possible page vide")
            
        return response.text
    except Exception as e:
        error_msg = f"❌ Erreur sur {url}: {str(e)}"
        log_message(error_msg)
        return None

def clean_text(element):
    """Nettoie le texte extrait d'un élément HTML"""
    if not element:
        return ""
    text = element.get_text(' ', strip=True)
    return ' '.join(text.split())

def extract_main_content(soup):
    """Extrait le contenu principal d'une page"""
    content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
    return content if content else soup

def extract_detailed_data(soup, url):
    """Extrait les données détaillées d'une page de catégorie"""
    main_content = extract_main_content(soup)
    
    data = {
        "metadata": {
            "url": url,
            "date_collecte": datetime.now().isoformat()
        },
        "titre": clean_text(soup.find('h1')),
        "introduction": "",
        "sections": [],
        "images": [],
        "documents": [],
        "liens_utiles": []
    }

    # Introduction (premier paragraphe significatif)
    first_paragraph = main_content.find('p') if main_content else None
    if first_paragraph:
        data["introduction"] = clean_text(first_paragraph)

    # Sections avec titres et contenus
    for heading in main_content.find_all(['h2', 'h3']) if main_content else []:
        section = {
            "titre": clean_text(heading),
            "contenu": []
        }
        
        next_node = heading.next_sibling
        while next_node and next_node.name not in ['h2', 'h3']:
            if next_node.name == 'p':
                text = clean_text(next_node)
                if text:
                    section["contenu"].append(text)
            elif next_node.name == 'ul':
                section["contenu"].extend([clean_text(li) for li in next_node.find_all('li')])
            
            next_node = next_node.next_sibling
        
        if section["contenu"]:
            data["sections"].append(section)

    # Images avec contexte
    for img in soup.find_all('img'):
        if img.get('src'):
            img_data = {
                "url": urljoin(url, img['src']),
                "alt": img.get('alt', ''),
                "contexte": get_image_context(img)
            }
            data["images"].append(img_data)

    # Documents PDF/DOC
    for link in soup.find_all('a', href=lambda x: x and x.lower().endswith(('.pdf', '.doc', '.docx'))):
        data["documents"].append({
            "titre": clean_text(link) or os.path.basename(link['href']),
            "url": urljoin(url, link['href']),
            "type": link['href'].split('.')[-1].lower()
        })

    # Liens utiles internes
    for link in soup.find_all('a', href=lambda x: x and x.startswith('/') and 'contact' not in x.lower()):
        data["liens_utiles"].append({
            "texte": clean_text(link),
            "url": urljoin(url, link['href'])
        })

    return data

def get_image_context(img_tag):
    """Trouve le contexte d'une image dans la page"""
    parent = img_tag.find_parent(['article', 'section', 'div'])
    if parent:
        return {
            "titre_parent": clean_text(parent.find(['h2', 'h3', 'h4'])),
            "texte_proche": clean_text(parent.find('p'))
        }
    return None

def save_category_data(data, category_name):
    """Sauvegarde les données d'une catégorie de manière organisée"""
    category_dir = os.path.join(OUTPUT_DIR, category_name)
    os.makedirs(category_dir, exist_ok=True)
    
    # Fichier JSON complet
    with open(os.path.join(category_dir, f"{category_name}_complet.json"), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Export CSV segmenté
    for data_type in ['sections', 'images', 'documents', 'liens_utiles']:
        if data.get(data_type):
            df = pd.DataFrame(data[data_type])
            df.to_csv(
                os.path.join(category_dir, f"{category_name}_{data_type}.csv"),
                index=False,
                encoding='utf-8-sig'
            )

def scrape_section(url, section_name):
    """Scrape une section spécifique du site"""
    log_message(f"🔍 Début du scraping: {section_name}")
    
    html = fetch_page(url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    data = extract_detailed_data(soup, url)
    
    if data:
        save_category_data(data, section_name)
        log_message(f"✅ {section_name}: {len(data.get('sections', []))} sections trouvées")
    else:
        log_message(f"⚠️ Aucune donnée valide pour {section_name}")
    
    return data

def main():
    setup_logging()
    log_message("🚀 Lancement du scraping complet du MDA")
    
    all_data = {}
    
    # Scraping des catégories principales
    for cat_name, cat_path in MAIN_CATEGORIES.items():
        url = urljoin(BASE_URL, cat_path)
        data = scrape_section(url, cat_name)
        if data:
            all_data[cat_name] = data
        
        # Pause aléatoire entre 2 et 5 secondes
        pause = random.uniform(2, 5)
        time.sleep(pause)
    
    # Scraping des sections supplémentaires
    for sec_name, sec_path in ADDITIONAL_SECTIONS.items():
        url = urljoin(BASE_URL, sec_path)
        data = scrape_section(url, sec_name)
        if data:
            all_data[sec_name] = data
        
        pause = random.uniform(2, 5)
        time.sleep(pause)
    
    # Sauvegarde consolidée
    with open(os.path.join(OUTPUT_DIR, "mda_artisanat_consolide.json"), 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    log_message("\n✅ Scraping terminé avec succès!")
    log_message(f"📁 Données sauvegardées dans: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    main()