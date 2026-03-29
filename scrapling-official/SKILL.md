---
name: scrapling-official
description: "Module de scraping avancé utilisant Scrapling pour extraire le contenu de pages web. Plus rapide et plus robuste que BeautifulSoup/trafilatura, avec support natif du JavaScript et sélecteurs CSS intelligents."
category: scraping
---

# Scrapling Official Skill pour Hermes Agent

Un outil de scraping puissant et moderne basé sur la bibliothèque `scrapling`, conçu pour fonctionner avec votre Hermes Agent. Ce skill permet d'extraire du contenu structuré depuis des pages web avec une meilleure performance et une plus grande résilience face aux changements de structure HTML.

## Pourquoi Scrapling ?

Scrapling est une alternative moderne à BeautifulSoup et trafilatura avec les avantages suivants :

- **Plus rapide** : Jusqu'à 3x plus rapide que BeautifulSoup
- **Adaptatif** : Les sélecteurs CSS s'adaptent automatiquement aux changements mineurs du DOM
- **JavaScript** : Support natif pour le rendu JavaScript (via Playwright intégré)
- **Intelligent** : Détection automatique du contenu principal d'une page
- **Flexible** : API simple et intuitive pour l'extraction de données

## Quand utiliser ce Skill

- Vous devez extraire du contenu depuis des pages web dynamiques (JavaScript)
- Les sites cibles ont une structure HTML complexe ou changeante
- Vous avez besoin d'une extraction rapide et fiable pour de nombreuses pages
- Vous voulez extraire des données structurées (articles, produits, profils, etc.)

## Prérequis

- Python 3.8 ou supérieur
- Installation de la dépendance `scrapling` (voir section Installation)
- Pour le support JavaScript : `playwright` (installé automatiquement avec scrapling)

## Installation

```bash
# Dans le dossier du skill
cd progfranceSkills/scrapling-official

# Installer les dépendances
pip install -r requirements.txt

# Si vous utilisez uv (recommandé)
uv pip install -r requirements.txt
```

## Flux de travail étape par étape

### Étape 1 — Configuration des URLs cibles

Éditez le fichier `config.json` pour ajouter les URLs que vous souhaitez scraper :

```json
{
  "urls": [
    "https://example.com/article-1",
    "https://example.com/article-2"
  ],
  "options": {
    "extract_full_content": true,
    "remove_scripts": true,
    "remove_styles": true,
    "timeout": 30
  }
}
```

### Étape 2 — Exécution du scraping

Lancez le script avec Python :

```bash
# Extraction basique
python scrapling_scraper.py

# Avec options personnalisées
python scrapling_scraper.py --config custom_config.json --output results.json

# Mode debug (affiche les détails de l'extraction)
python scrapling_scraper.py --debug
```

### Étape 3 — Traitement des résultats

Le script génère un fichier JSON structuré avec :

- `url` : L'URL source
- `title` : Le titre de la page
- `content` : Le contenu textuel extrait
- `metadata` : Les métadonnées (auteur, date, etc.)
- `selectors_used` : Les sélecteurs CSS utilisés pour l'extraction

## Instructions pour l'Agent Hermes

### Format de sortie attendu

Lorsque vous utilisez ce skill, l'Agent Hermes recevra un JSON structuré comme suit :

```json
{
  "scraped_pages": [
    {
      "url": "https://example.com/article",
      "title": "Titre de l'article",
      "content": "Contenu textuel complet extrait...",
      "metadata": {
        "author": "Auteur",
        "published_date": "2024-01-15",
        "tags": ["tag1", "tag2"]
      },
      "extraction_stats": {
        "content_length": 1250,
        "selectors_matched": 5,
        "extraction_time_ms": 234
      }
    }
  ]
}
```

### Commandes pour l'Agent

1. **Scraping simple d'une URL :**
   ```
   python scrapling_scraper.py --url "https://example.com"
   ```

2. **Scraping depuis un fichier de configuration :**
   ```
   python scrapling_scraper.py --config config.json
   ```

3. **Extraction avec sélecteurs personnalisés :**
   ```
   python scrapling_scraper.py --url "https://example.com" --selectors '{"title": "h1.article-title", "content": "div.article-body"}'
   ```

4. **Mode JavaScript (pour pages dynamiques) :**
   ```
   python scrapling_scraper.py --url "https://example.com" --js
   ```

## Options disponibles

| Option | Description | Valeur par défaut |
|--------|-------------|-------------------|
| `--url` | URL unique à scraper | - |
| `--config` | Fichier de configuration JSON | `config.json` |
| `--output` | Fichier de sortie | `results.json` |
| `--js` | Activer le rendu JavaScript | `False` |
| `--debug` | Mode debug (verbose) | `False` |
| `--timeout` | Timeout en secondes | `30` |
| `--selectors` | Sélecteurs CSS personnalisés (JSON) | Auto-détection |

## Exemples d'utilisation

### Exemple 1 : Scraper un article de blog

```bash
python scrapling_scraper.py --url "https://monblog.com/article-123" --output article.json
```

### Exemple 2 : Extraire des produits d'une page e-commerce

```bash
python scrapling_scraper.py --url "https://boutique.com/produits" \
  --selectors '{"products": "div.product-card", "name": "h3.product-name", "price": "span.price"}' \
  --output produits.json
```

### Exemple 3 : Scraper plusieurs URLs en parallèle

```bash
# config.json
{
  "urls": [
    "https://site1.com/page1",
    "https://site2.com/page2",
    "https://site3.com/page3"
  ]
}

# Exécution
python scrapling_scraper.py --config config.json --output multi_results.json
```

## Intégration avec Hermes Agent

Pour intégrer ce skill dans votre flux de travail Hermes :

1. **Déclenchement** : L'Agent Hermes peut appeler le script via `subprocess` ou en import direct
2. **Communication** : Les résultats sont retournés en JSON standard
3. **Traitement** : L'Agent peut analyser le contenu extrait pour générer des réponses, résumés, ou analyses

### Exemple d'intégration Python

```python
import subprocess
import json

# Lancer le scraper
result = subprocess.run(
    ["python", "scrapling_scraper.py", "--url", "https://example.com", "--output", "-"],
    capture_output=True,
    text=True
)

# Parser les résultats
data = json.loads(result.stdout)
print(f"Titre: {data['scraped_pages'][0]['title']}")
print(f"Contenu: {data['scraped_pages'][0]['content'][:500]}...")
```

## Dépannage

- **Erreur d'installation de Playwright** : Exécutez `playwright install` après l'installation de scrapling
- **Timeout sur une page** : Augmentez le timeout avec `--timeout 60`
- **Contenu vide extrait** : Essayez le mode JavaScript avec `--js`
- **Sélecteurs non détectés** : Utilisez `--debug` pour voir les sélecteurs essayés

## Personnalisation

Pour adapter le scraper à vos besoins spécifiques :

1. Éditez `scrapling_scraper.py` pour modifier les sélecteurs par défaut
2. Créez des profils de scraping dans `profiles/` pour différents types de sites
3. Ajoutez des transformateurs de données dans `transformers/` pour formater la sortie

## Comparaison avec d'autres outils

| Outil | Vitesse | JS Support | Adaptatif | Complexité |
|-------|---------|------------|-----------|------------|
| Scrapling | ⚡⚡⚡ | Oui | Oui | Faible |
| BeautifulSoup | ⚡ | Non | Non | Faible |
| Trafilatura | ⚡⚡ | Non | Non | Faible |
| Playwright direct | ⚡⚡ | Oui | Non | Élevée |

## Ressources

- [Documentation Scrapling](https://github.com/D4Vinci/Scrapling)
- [Exemples OpenClaw](https://github.com/LeoYeAI/openclaw-master-skills/tree/main/skills/scrapling-official)
