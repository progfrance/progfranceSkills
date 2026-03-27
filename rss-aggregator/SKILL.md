---
name: rss-aggregator
description: Effectue une veille technologique approfondie en récupérant les articles complets de flux RSS. Utilise ce skill quand l'utilisateur demande une "veille", "les dernières news", ou "un résumé de l'actualité".
---

# RSS Aggregator & Smart Scraper

Ce skill récupère les dernières actualités à partir d'une liste de flux RSS (`references/feeds.opml`). Il utilise un système de "Deep Scraping" pour télécharger le contenu textuel complet des articles web, offrant un contexte riche pour la création de synthèses.

## Usage

Utilise le script `scripts/fetch_news.py` pour récupérer les articles bruts. Ensuite, tu devras analyser la sortie de ce script et rédiger toi-même la newsletter finale pour l'utilisateur en respectant STRICTEMENT les instructions de formatage ci-dessous.

### Command

```bash
uv run --with feedparser --with trafilatura scripts/fetch_news.py --days <number_of_days>
```

*Options disponibles :*
- `--days` : Nombre de jours à remonter (par défaut : 1).
- `--max-entries` : Nombre maximum d'articles scannés par flux (par défaut : 10).
- `--opml` : Spécifier un fichier OPML différent (ex: `references/feeds-reddit.opml`).

## Instructions de Formatage pour l'Agent (CRITIQUE)

Une fois que le script `fetch_news.py` t'a retourné le contexte avec les articles bruts, tu dois agir comme un **expert en veille technologique** et rédiger une newsletter de synthèse en Français pour l'utilisateur.

**TA MISSION :**
Rédiger une newsletter synthétique à partir du contexte brut extrait par le script.

**RÈGLES DE FORME :**
1. Regroupe intelligemment les news par grandes thématiques (ex: IA, Cybersécurité, Hardware, Business...). C'est à toi de déterminer les catégories pertinentes en fonction des articles.
2. Pour CHAQUE news que tu choisis de retenir, tu dois mettre le LIEN BRUT à la fin.
3. Format OBLIGATOIRE par news :
   * [Titre de la news] : Résumé pertinent en 2 ou 3 phrases généré par tes soins à partir du "Contenu Extrait".
   Source : [https://le-lien-complet-de-l-article.com](https://le-lien-complet-de-l-article.com)

**RÈGLES DE FOND :**
- Filtre l'information : Ignore les articles vides, promotionnels ou non pertinents.
- Sois concis, factuel et précis dans tes résumés.
- Ne mets PAS de Markdown sur les liens de source (pas de `[texte](url)`), mets juste l'URL brute.
- Base tes résumés UNIQUEMENT sur le contexte fourni par le script. N'invente pas d'informations.

## Configuration

La liste des flux principaux est stockée dans `references/feeds.opml`.
Des flux alternatifs (ex: Reddit) sont dans `references/feeds-reddit.opml`.
