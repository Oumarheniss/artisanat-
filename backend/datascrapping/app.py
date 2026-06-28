from flask import Flask, jsonify, send_from_directory
import os
import json
from datetime import datetime
from flask_cors import CORS  # Pour gérer les requêtes cross-origin

app = Flask(__name__)
CORS(app)  # Autorise les requêtes depuis n'importe quelle origine (à restreindre en production)

# Configuration
DATA_DIR = "unified_data"
JSON_FILE = "unified_artisanat.json"
FILE_PATH = os.path.join(DATA_DIR, JSON_FILE)

@app.route('/api/artisanat', methods=['GET'])
def get_artisanat_data():
    """Endpoint principal pour récupérer toutes les données"""
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "count": len(data)
        })
    
    except FileNotFoundError:
        return jsonify({
            "status": "error",
            "message": "Data file not found",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/artisanat/<category>', methods=['GET'])
def get_artisanat_by_category(category):
    """Filtre les données par catégorie"""
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        
        filtered_data = [item for item in all_data if item.get('category') == category]
        
        return jsonify({
            "status": "success",
            "category": category,
            "count": len(filtered_data),
            "data": filtered_data
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/artisanat/sources', methods=['GET'])
def get_data_sources():
    """Liste les sources disponibles"""
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        
        sources = list(set(item['source'] for item in all_data))
        
        return jsonify({
            "status": "success",
            "sources": sources,
            "count": len(sources)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/artisanat/categories', methods=['GET'])
def get_categories():
    """Retourne la liste unique des catégories"""
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        categories = sorted(list(set(item.get('category', '').strip() for item in data if item.get('category'))))

        return jsonify({
            "status": "success",
            "categories": categories,
            "count": len(categories)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Vérifie que le fichier de données existe
    if not os.path.exists(FILE_PATH):
        print(f"ERREUR: Le fichier {FILE_PATH} n'existe pas")
        print("Veuillez d'abord exécuter unify_artisanat_data.py")
    else:
        print(f"API démarrée avec les données de {FILE_PATH}")
        app.run(host='0.0.0.0', port=5000, debug=True)

