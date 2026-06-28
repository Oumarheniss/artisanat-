import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from urllib.parse import urljoin, urlparse
from datetime import datetime
import time
import random
from scholarly import scholarly
import logging
from logging.handlers import RotatingFileHandler
from tqdm import tqdm
import ssl
import urllib3

# Désactiver les avertissements SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# Configuration
CONFIG = {
    "CNRST_URL": "https://www.cnrst.ma/",
    "OUTPUT_DIR": "cnrst_artisanat_recherche",
    "HEADERS": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Referer": "https://www.google.com/"
    },
    "SEARCH_TERMS": [
        "artisanat marocain",
        "métiers traditionnels Maroc",
        "patrimoine artisanal marocain",
        "savoir-faire artisanaux Maroc"
    ],
    "MAX_RESULTS": 50,
    "REQUEST_DELAY": (1, 3),
    "TIMEOUT": 30,
    "VERIFY_SSL": False  # Désactive la vérification SSL
}

def setup_logging(output_dir):
    """Configure le logging après création des dossiers."""
    log_dir = os.path.join(output_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "scraping.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                log_path,
                maxBytes=5*1024*1024,
                backupCount=3
            ),
            logging.StreamHandler()
        ]
    )

class CNRSTScraper:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.verify = config['VERIFY_SSL']
        self.session.headers.update(config['HEADERS'])
        self.setup_directories()
        setup_logging(config['OUTPUT_DIR'])
        logging.info("Initialisation du scraper CNRST")

    def setup_directories(self):
        """Crée l'arborescence des dossiers."""
        subdirs = ["publications", "theses", "rapports", "metadata", "logs"]
        for d in subdirs:
            path = os.path.join(self.config['OUTPUT_DIR'], d)
            os.makedirs(path, exist_ok=True)

    def safe_get(self, url, **kwargs):
        """Effectue une requête HTTP avec gestion des erreurs."""
        kwargs.setdefault('timeout', self.config['TIMEOUT'])
        max_retries = kwargs.pop('max_retries', 3)
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, **kwargs)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                delay = 2 ** attempt + random.random()
                logging.warning(f"Tentative {attempt+1} échouée pour {url} - Attente {delay:.1f}s - Erreur: {str(e)}")
                time.sleep(delay)
        
        logging.error(f"Échec après {max_retries} tentatives pour {url}")
        return None

    def search_cnrst(self, search_term):
        """Effectue une recherche sur le site CNRST."""
        search_url = urljoin(self.config['CNRST_URL'], "recherche")
        params = {'s': search_term}
        
        response = self.safe_get(search_url, params=params)
        if not response:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Sélecteurs adaptatifs
        items = soup.select('.search-result') or soup.select('.result-item') or soup.select('article.post')
        
        for item in items:
            try:
                title = item.select_one('h2 a') or item.select_one('h3 a') or item.find('a')
                if not title:
                    continue
                    
                result = {
                    'titre': self.clean_text(title),
                    'lien': urljoin(self.config['CNRST_URL'], title['href']),
                    'type': 'thesis' if 'thèse' in title.text.lower() else 'publication',
                    'source': 'CNRST',
                    'mots_cles': search_term
                }
                results.append(result)
            except Exception as e:
                logging.error(f"Erreur traitement item: {e}")
                
        return results

    def extract_publication_details(self, url):
        """Extrait les détails d'une publication."""
        response = self.safe_get(url)
        if not response:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        details = {
            'resume': '',
            'contenu': '',
            'auteurs': [],
            'date': '',
            'pdf_link': None
        }
        
        # Extraction du résumé
        abstract = soup.select_one('.abstract') or soup.select_one('.resume')
        if abstract:
            details['resume'] = self.clean_text(abstract)
        
        # Extraction du contenu principal
        content = soup.find('article') or soup.select_one('.content') or soup.select_one('.entry-content')
        if content:
            details['contenu'] = self.clean_text(content)
        
        # Extraction des auteurs
        authors = soup.select('.author') or soup.select('[rel="author"]')
        details['auteurs'] = [self.clean_text(a) for a in authors]
        
        # Extraction de la date
        date = soup.select_one('.date') or soup.select_one('time')
        if date:
            details['date'] = self.clean_text(date)
        
        # Recherche du lien PDF
        for a in soup.find_all('a', href=True):
            if a['href'].lower().endswith('.pdf'):
                details['pdf_link'] = urljoin(url, a['href'])
                break
        
        return details

    def clean_text(self, element):
        """Nettoie le texte extrait."""
        if element is None:
            return ""
        if isinstance(element, (str, bytes)):
            text = str(element)
        else:
            text = element.get_text(' ', strip=True)
        return ' '.join(text.split()).strip()

    def download_file(self, url, dest_folder, filename=None):
        """Télécharge un fichier."""
        if not url:
            return None
            
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            if not filename:
                filename = os.path.basename(urlparse(url).path) or "document.pdf"
                filename = filename.split('?')[0]
                
            filepath = os.path.join(self.config['OUTPUT_DIR'], dest_folder, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
                    
            return filepath
        except Exception as e:
            logging.error(f"Erreur téléchargement {url}: {e}")
            return None

    def search_scholarly(self, query, max_results=5):
        """Recherche sur Google Scholar."""
        try:
            search_query = scholarly.search_pubs(query)
            results = []
            for _ in range(max_results):
                pub = next(search_query, None)
                if not pub:
                    break
                results.append({
                    'titre': pub['bib'].get('title', ''),
                    'auteurs': pub['bib'].get('author', ''),
                    'annee': pub['bib'].get('year', ''),
                    'lien': pub.get('pub_url', ''),
                    'abstract': pub['bib'].get('abstract', ''),
                    'source': 'Google Scholar'
                })
            return results
        except Exception as e:
            logging.error(f"Erreur Google Scholar: {e}")
            return []

    def save_results(self, data, filename_prefix):
        """Sauvegarde les résultats."""
        if not data:
            logging.info(f"Aucune donnée à sauvegarder pour {filename_prefix}")
            return
            
        json_path = os.path.join(self.config['OUTPUT_DIR'], "metadata", f"{filename_prefix}.json")
        csv_path = os.path.join(self.config['OUTPUT_DIR'], f"{filename_prefix}.csv")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        pd.DataFrame(data).to_csv(csv_path, index=False, encoding='utf-8-sig')
        logging.info(f"Données sauvegardées : {json_path} et {csv_path}")

    def run(self):
        """Exécute le processus complet."""
        logging.info("Début de la collecte des données")
        all_results = []
        
        # Recherche CNRST
        for term in self.config['SEARCH_TERMS']:
            logging.info(f"Recherche CNRST: {term}")
            results = self.search_cnrst(term)
            
            for result in tqdm(results, desc=f"Traitement {term[:15]}..."):
                details = self.extract_publication_details(result['lien'])
                if details:
                    result.update(details)
                    
                    if details.get('pdf_link'):
                        pdf_name = f"{term[:10]}_{len(all_results)}.pdf"
                        result['pdf_local'] = self.download_file(
                            details['pdf_link'],
                            'publications',
                            pdf_name
                        )
                
                all_results.append(result)
                time.sleep(random.uniform(*self.config['REQUEST_DELAY']))
        
        # Recherche Google Scholar
        scholar_results = []
        for term in self.config['SEARCH_TERMS']:
            logging.info(f"Recherche Scholar: {term}")
            query = f"{term} site:cnrst.ma OR site:ac.ma"
            results = self.search_scholarly(query)
            scholar_results.extend(results)
            time.sleep(5)
        
        # Sauvegarde
        self.save_results(all_results, "cnrst_publications")
        self.save_results(scholar_results, "google_scholar_results")
        
        # Rapport final
        report = {
            "date": datetime.now().isoformat(),
            "total_cnrst": len(all_results),
            "total_scholar": len(scholar_results),
            "termes": self.config['SEARCH_TERMS'],
            "statistiques": {
                "avec_pdf": sum(1 for r in all_results if r.get('pdf_local')),
                "theses": sum(1 for r in all_results if r.get('type') == 'thesis')
            }
        }
        
        report_path = os.path.join(self.config['OUTPUT_DIR'], "rapports", "rapport.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Collecte terminée. Rapport: {report_path}")

if __name__ == "__main__":
    scraper = CNRSTScraper(CONFIG)
    scraper.run()
