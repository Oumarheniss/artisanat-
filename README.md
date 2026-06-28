# Artisanat Data Scraping

## Description

Ce projet permet de collecter, nettoyer et structurer des données liées à l'artisanat marocain à partir de différentes sources web.

Les données récupérées sont ensuite préparées pour être utilisées dans des applications de visualisation, d'analyse ou d'intelligence artificielle.

---

## Structure du projet

```
backend/
│
├── datascrapping/
│   ├── scripts/
│   ├── output/
│   └── ...
│
├── requirements.txt
└── ...
```

---

## Installation

Cloner le projet :

```bash
git clone https://github.com/<username>/<repository>.git
cd <repository>
```

Créer un environnement virtuel :

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

## Utilisation

Lancer le script principal :

```bash
python main.py
```

Les données générées seront enregistrées dans le dossier prévu à cet effet.

---

## Technologies utilisées

* Python
* Requests
* BeautifulSoup
* Pandas
* JSON
* CSV

---

## Remarque

Les fichiers contenant des clés API, des jetons d'accès ou des données sensibles ne sont pas versionnés dans le dépôt Git.

Il est recommandé d'utiliser un fichier `.env` pour stocker les variables d'environnement.

---

## Auteur

**Oumaima Rheniss**

Projet réalisé dans le cadre d'un projet de collecte et de traitement de données.
