import pandas as pd
import json
import os
import re

class ArtisanatDataUnifier:
    def __init__(self):
        # Inclure uniquement les fichiers confirmés dans ton répertoire
        self.data_sources = {
            "voyage_maroc": {
                "path": "artisanat_marocain.csv",
                "type": "csv",
                "category": "general"
            },
            "terra_maroc": {
                "path": "histoire_artisanat_marocain.json",
                "type": "json",
                "category": "histoire"
            }
            # Tu pourras réactiver les autres plus tard quand les fichiers seront prêts
        }
        self.output_dir = "unified_data"
        os.makedirs(self.output_dir, exist_ok=True)

    def clean_text(self, text):
        """Nettoie le texte pour le NLP"""
        if pd.isna(text) or str(text).strip().lower() in ["", "nan", "none"]:
            return ""
        return re.sub(r'\s+', ' ', str(text)).strip()[:5000]

    def safe_image_convert(self, image_str):
        """Convertit la colonne images en liste de manière sécurisée"""
        if pd.isna(image_str) or str(image_str).strip().lower() in ["", "nan", "none"]:
            return []
        try:
            if isinstance(image_str, (list, dict)):
                return image_str
            return str(image_str).split("|")
        except Exception:
            return []

    def load_file(self, file_path, file_type):
        """Charge un fichier selon son type"""
        try:
            if file_type == "csv":
                df = pd.read_csv(file_path)

                processed_data = []
                for _, row in df.iterrows():
                    processed_data.append({
                        "title": self.clean_text(row.get("titre") or row.get("title")),
                        "content": self.clean_text(
                            row.get("contenu") or 
                            row.get("content") or 
                            row.get("description")
                        ),
                        "images": self.safe_image_convert(row.get("images")),
                        "raw_data": {k: v for k, v in row.items() if pd.notna(v)}
                    })
                return processed_data

            elif file_type == "json":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    return [data]
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {file_path} : {str(e)}")
            return []

    def unify_data(self):
        """Fusionne toutes les sources"""
        unified_data = []
        seen = set()

        for source_name, config in self.data_sources.items():
            print(f"\n🔍 Traitement de {source_name}...")
            data = self.load_file(config["path"], config["type"])

            for item in data:
                title = self.clean_text(item.get("title", ""))
                content = self.clean_text(item.get("content", ""))
                key = (title, content)

                if key in seen:
                    continue  # éviter les doublons
                seen.add(key)

                unified_data.append({
                    "source": source_name,
                    "category": config["category"],
                    "title": title or "Sans titre",
                    "content": content,
                    "images": item.get("images", []),
                    "raw_data": item.get("raw_data", item)
                })

        return unified_data

    def save_unified_data(self, data):
        """Sauvegarde les résultats"""
        with open(f"{self.output_dir}/unified_artisanat.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        pd.DataFrame(data).to_csv(f"{self.output_dir}/unified_artisanat.csv", index=False)

        print(f"\n💾 Données sauvegardées dans {self.output_dir}/")
        print("📊 Statistiques par source :")
        print(pd.DataFrame(data)["source"].value_counts())

    def run(self):
        print("🚀 Démarrage de l'unification des données...")
        unified_data = self.unify_data()
        self.save_unified_data(unified_data)
        print(f"\n✅ {len(unified_data)} éléments unifiés avec succès !")

if __name__ == "__main__":
    unifier = ArtisanatDataUnifier()
    unifier.run()
