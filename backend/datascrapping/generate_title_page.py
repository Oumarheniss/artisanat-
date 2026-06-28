import json
import os

# Fichiers
DATA_FILE = './unified_data/unified_artisanat.json'
TEMPLATE_FILE = './template_titre.html'
OUTPUT_DIR = './generated_pages'

# Chargement des données
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Chargement du template HTML
with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
    template_html = f.read()

# Slugify pour générer des noms de fichiers sûrs
def slugify(text):
    import re
    return re.sub(r'[\s/]+', '-', text.lower()).replace('é', 'e').replace('è', 'e')

# Création du dossier s'il n'existe pas
os.makedirs(OUTPUT_DIR, exist_ok=True)

count = 0

for item in data:
    title = item.get("title") or item.get("raw_data", {}).get("titre")
    if not title or title.strip().lower() == "sans titre":
        continue

    category = item.get("category", "Autres")

    # Recherche intelligente de la description
    description = item.get("description") or \
                  item.get("content") or \
                  item.get("raw_data", {}).get("description") or \
                  item.get("raw_data", {}).get("contenu") or \
                  "Aucune description disponible."

    slug = slugify(title)
    output_path = os.path.join(OUTPUT_DIR, f"{slug}.html")

    # Génération du contenu HTML
    html_content = template_html.replace("{{TITRE}}", title)\
                                .replace("{{CATEGORIE}}", category)\
                                .replace("{{DESCRIPTION}}", description)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    count += 1

print(f"✅ {count} pages générées dans le dossier '{OUTPUT_DIR}'")
