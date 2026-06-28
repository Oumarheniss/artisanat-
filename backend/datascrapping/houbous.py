import requests
from bs4 import BeautifulSoup
import urllib3

# Désactiver les warnings liés à la désactivation SSL (à utiliser uniquement pour tests)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scraper_section_arabe(url, debut_section):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, verify=False)  # <-- verify=False désactive SSL
    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête pour {url}: {e}")
        return None

    response.encoding = 'utf-8'

    if response.status_code != 200:
        print(f"Erreur lors de la requête : {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    content_div = soup.find('div', class_='itemFullText')

    if not content_div:
        print("Le contenu principal n'a pas été trouvé.")
        return None

    texte = content_div.get_text(separator='\n', strip=True)
    lignes = texte.split('\n')

    try:
        debut_index = next(i for i, ligne in enumerate(lignes) if debut_section in ligne)
    except StopIteration:
        print(f"La section '{debut_section}' n'a pas été trouvée.")
        return None

    section_extraite = '\n'.join(lignes[debut_index:])
    return section_extraite

def sauvegarder_texte(texte, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(texte)
    print(f"Texte sauvegardé dans '{filename}'.")

if __name__ == "__main__":
    url = "https://www.habous.gov.ma/daouat-alhaq/item/6855"
    debut_section = "كيف بدأ التصنيع في المغرب"

    texte_filtré = scraper_section_arabe(url, debut_section)
    if texte_filtré:
        print("=== Section extraite ===\n")
        print(texte_filtré)
        sauvegarder_texte(texte_filtré, "artisanat_maroc.txt")
    else:
        print("Aucun résultat à sauvegarder.")
