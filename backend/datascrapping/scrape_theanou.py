import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import time
import json
from PIL import Image
import io
import pytesseract
import pandas as pd

# Configuration
BASE_URL = "https://www.theanou.com"
OUTPUT_DIR = "anou_complete_data"
os.makedirs(os.path.join(OUTPUT_DIR, "images"), exist_ok=True)

# Initialisation Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=chrome_options)

def scrape_page(url):
    print(f"\n🌐 Scraping {url}")
    data = {"url": url, "texts": [], "images": []}
    
    # Méthode 1: Selenium (pour contenu dynamique)
    driver.get(url)
    time.sleep(3)  # Attente chargement JS
    
    # Extraction texte Selenium
    for element in driver.find_elements(By.XPATH, "//*[text()[normalize-space()]]"):
        text = element.text.strip()
        if len(text) > 10:  # Filtre les petits textes
            data["texts"].append({
                "type": element.tag_name,
                "text": text,
                "method": "selenium"
            })
    
    # Extraction images Selenium
    for img in driver.find_elements(By.TAG_NAME, "img"):
        try:
            src = img.get_attribute("src")
            if src and not src.startswith("data:"):
                data["images"].append({
                    "url": src,
                    "alt": img.get_attribute("alt") or "",
                    "local_path": download_image(src)
                })
        except:
            continue
    
    # Méthode 2: BeautifulSoup (pour HTML statique)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extraction texte BS4
    for tag in ['p', 'h1', 'h2', 'h3', 'div']:
        for element in soup.find_all(tag):
            text = element.get_text(' ', strip=True)
            if text and len(text) > 10:
                data["texts"].append({
                    "type": tag,
                    "text": text,
                    "method": "bs4"
                })
    
    # Extraction images BS4 (complémentaire)
    for img in soup.find_all('img'):
        try:
            src = img.get('src')
            if src and src not in [i['url'] for i in data["images"]]:
                data["images"].append({
                    "url": src,
                    "alt": img.get('alt', ""),
                    "local_path": download_image(src)
                })
        except:
            continue
    
    return data

def download_image(img_url):
    """Télécharge et enregistre une image"""
    if not img_url.startswith('http'):
        img_url = urljoin(BASE_URL, img_url)
    
    try:
        response = requests.get(img_url, stream=True, timeout=10)
        if response.status_code == 200:
            # Génère un nom de fichier unique
            img_name = f"img_{int(time.time())}_{os.path.basename(img_url)[:50]}"
            img_path = os.path.join(OUTPUT_DIR, "images", img_name)
            
            # Sauvegarde l'image
            with open(img_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            # Essaye d'extraire le texte avec OCR
            try:
                img = Image.open(io.BytesIO(response.content))
                ocr_text = pytesseract.image_to_string(img)
                if ocr_text.strip():
                    return {"path": img_path, "ocr_text": ocr_text.strip()}
            except:
                pass
            
            return {"path": img_path, "ocr_text": None}
    except:
        return None

def save_data(data, filename):
    """Sauvegarde les données au format JSON et CSV"""
    # JSON complet
    with open(os.path.join(OUTPUT_DIR, f"{filename}.json"), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # CSV pour les textes
    if data["texts"]:
        pd.DataFrame(data["texts"]).to_csv(
            os.path.join(OUTPUT_DIR, f"{filename}_texts.csv"), 
            index=False,
            encoding='utf-8-sig'
        )
    
    # CSV pour les images
    if data["images"]:
        pd.DataFrame([
            {**img, **{"ocr_text": img["local_path"]["ocr_text"] if img["local_path"] else None}}
            for img in data["images"]
        ]).to_csv(
            os.path.join(OUTPUT_DIR, f"{filename}_images.csv"), 
            index=False
        )

def main():
    urls = [
        BASE_URL,
        f"{BASE_URL}/about",
        f"{BASE_URL}/blog",
        f"{BASE_URL}/shop"
    ]
    
    all_data = {}
    
    for url in urls:
        page_data = scrape_page(url)
        all_data[url] = page_data
        save_data(page_data, url.split('//')[1].replace('/', '_'))
        time.sleep(2)  # Pause entre les pages
    
    driver.quit()
    
    # Sauvegarde consolidée
    with open(os.path.join(OUTPUT_DIR, "all_data.json"), 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Extraction terminée! Données sauvegardées dans: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    main()