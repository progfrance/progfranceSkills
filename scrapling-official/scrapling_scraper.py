#!/usr/bin/env python3
"""
Scrapling Official Skill pour Hermes Agent
Un scraper moderne et performant utilisant la bibliothèque Scrapling.

Ce script permet d'extraire du contenu structuré depuis des pages web
avec support du JavaScript et sélecteurs CSS adaptatifs.

Usage:
    python scrapling_scraper.py --url "https://example.com"
    python scrapling_scraper.py --config config.json
    python scrapling_scraper.py --url "https://example.com" --js --output results.json
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Import de Scrapling
try:
    from scrapling import Fetcher, Adaptor
except ImportError:
    print("Erreur: Scrapling n'est pas installé. Exécutez: pip install scrapling", file=sys.stderr)
    sys.exit(1)

# Pour le support JavaScript
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class ScraplingScraper:
    """
    Classe principale pour le scraping avec Scrapling.
    Fournit une interface simple pour extraire du contenu de pages web.
    """

    # Sélecteurs par défaut pour l'extraction de contenu d'article
    DEFAULT_SELECTORS = {
        'title': [
            'h1.article-title',
            'h1.title',
            'h1',
            'meta[property="og:title"]',
            'title'
        ],
        'content': [
            'article',
            'main',
            'div.article-content',
            'div.content',
            'div.post-content',
            'article.post',
            'meta[property="og:description"]'
        ],
        'author': [
            'meta[name="author"]',
            'span.author',
            'div.author',
            'p.author'
        ],
        'date': [
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            'time',
            'span.date',
            'div.date'
        ],
        'tags': [
            'meta[name="keywords"]',
            'div.tags',
            'span.tags',
            'a.tag'
        ]
    }

    def __init__(self, timeout: int = 30, use_js: bool = False, debug: bool = False):
        """
        Initialiser le scraper.

        Args:
            timeout: Timeout en secondes pour les requêtes
            use_js: Activer le rendu JavaScript via Playwright
            debug: Activer le mode debug
        """
        self.timeout = timeout
        self.use_js = use_js
        self.debug = debug
        self.fetcher = Fetcher(
            auto_save=True,
            storage_path='.scrapling_cache',
            timeout=timeout * 1000  # Convertir en millisecondes
        )

    def log(self, message: str, level: str = "info"):
        """Afficher un message de log si le mode debug est activé."""
        if self.debug:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level.upper()}] {message}", file=sys.stderr)

    def fetch_with_js(self, url: str) -> Optional[str]:
        """
        Récupérer une page avec rendu JavaScript via Playwright.

        Args:
            url: L'URL à récupérer

        Returns:
            Le HTML de la page ou None en cas d'erreur
        """
        if not PLAYWRIGHT_AVAILABLE:
            print("Erreur: Playwright n'est pas installé. Exécutez: pip install playwright", file=sys.stderr)
            return None

        self.log(f"Récupération avec JS: {url}", "debug")

        try:
            with sync_playwright() as p:
                # Lancer le navigateur (headless)
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Naviguer vers la page
                page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)

                # Attendre un peu pour le chargement dynamique
                page.wait_for_timeout(2000)

                # Récupérer le HTML rendu
                html = page.content()

                browser.close()
                return html

        except Exception as e:
            self.log(f"Erreur Playwright: {e}", "error")
            return None

    def extract_text_from_selector(self, adaptor: Adaptor, selectors: List[str]) -> Optional[str]:
        """
        Extraire le texte en essayant plusieurs sélecteurs.

        Args:
            adaptor: L'adaptor Scrapling
            selectors: Liste de sélecteurs CSS à essayer

        Returns:
            Le texte extrait ou None
        """
        for selector in selectors:
            try:
                # Essayer d'abord avec l'adaptor adaptatif de Scrapling
                element = adaptor.lxml.css_select(selector)
                if element:
                    # Extraire le texte
                    if selector.startswith('meta['):
                        # Pour les meta tags, extraire le contenu de l'attribut
                        attr = selector.split('[')[1].split(']')[0].split('=')[0].strip('"\'')
                        text = element[0].get(attr, '')
                    elif selector == 'title':
                        text = element[0].text
                    else:
                        text = element[0].text_content().strip()

                    if text and len(text) > 10:  # Ignorer les extraits trop courts
                        return text
            except Exception:
                continue

        return None

    def scrape_url(self, url: str, custom_selectors: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
        """
        Scraper une URL et extraire le contenu.

        Args:
            url: L'URL à scraper
            custom_selectors: Sélecteurs CSS personnalisés

        Returns:
            Dictionnaire avec les données extraites
        """
        start_time = time.time()
        self.log(f"Démarrage du scraping: {url}", "info")

        result = {
            'url': url,
            'title': None,
            'content': None,
            'metadata': {},
            'selectors_used': {},
            'extraction_stats': {}
        }

        # Récupérer le HTML
        if self.use_js:
            html = self.fetch_with_js(url)
        else:
            try:
                response = self.fetcher.get(url, headless=False)
                html = response.text if response else None
            except Exception as e:
                self.log(f"Erreur de récupération: {e}", "error")
                html = None

        if not html:
            result['error'] = "Impossible de récupérer la page"
            return result

        # Créer un adaptor Scrapling
        adaptor = Adaptor(html, url=url)

        # Utiliser les sélecteurs personnalisés ou les défauts
        selectors = custom_selectors or self.DEFAULT_SELECTORS

        # Extraire le titre
        result['title'] = self.extract_text_from_selector(adaptor, selectors.get('title', self.DEFAULT_SELECTORS['title']))
        if result['title']:
            result['selectors_used']['title'] = "Titre extrait"

        # Extraire le contenu principal
        content_text = self.extract_text_from_selector(adaptor, selectors.get('content', self.DEFAULT_SELECTORS['content']))
        if content_text:
            # Nettoyer le contenu
            content_text = self.clean_content(content_text)
            result['content'] = content_text
            result['selectors_used']['content'] = f"{len(content_text)} caractères"

        # Extraire les métadonnées
        author = self.extract_text_from_selector(adaptor, selectors.get('author', self.DEFAULT_SELECTORS['author']))
        if author:
            result['metadata']['author'] = author

        date = self.extract_text_from_selector(adaptor, selectors.get('date', self.DEFAULT_SELECTORS['date']))
        if date:
            result['metadata']['published_date'] = date

        tags = self.extract_text_from_selector(adaptor, selectors.get('tags', self.DEFAULT_SELECTORS['tags']))
        if tags:
            result['metadata']['tags'] = [t.strip() for t in tags.split(',') if t.strip()]

        # Calculer les statistiques
        extraction_time = (time.time() - start_time) * 1000  # En millisecondes
        result['extraction_stats'] = {
            'content_length': len(result['content']) if result['content'] else 0,
            'extraction_time_ms': round(extraction_time, 2),
            'has_js_support': self.use_js
        }

        self.log(f"Extraction terminée en {extraction_time:.2f}ms", "info")

        return result

    def clean_content(self, content: str) -> str:
        """
        Nettoyer le contenu extrait.

        Args:
            content: Le contenu brut

        Returns:
            Le contenu nettoyé
        """
        import re

        # Supprimer les espaces multiples
        content = re.sub(r'\s+', ' ', content)

        # Supprimer les lignes vides excessives
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        # Troncer si trop long (pour éviter de surcharger le contexte de l'IA)
        max_chars = 10000
        if len(content) > max_chars:
            content = content[:max_chars] + "..."

        return content.strip()

    def scrape_multiple_urls(self, urls: List[str], custom_selectors: Optional[Dict[str, List[str]]] = None) -> List[Dict[str, Any]]:
        """
        Scraper plusieurs URLs.

        Args:
            urls: Liste d'URLs à scraper
            custom_selectors: Sélecteurs CSS personnalisés

        Returns:
            Liste des résultats pour chaque URL
        """
        results = []
        for i, url in enumerate(urls, 1):
            self.log(f"Traitement {i}/{len(urls)}: {url}", "info")
            result = self.scrape_url(url, custom_selectors)
            results.append(result)

        return results


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Charger la configuration depuis un fichier JSON.

    Args:
        config_path: Chemin vers le fichier de configuration

    Returns:
        Dictionnaire de configuration
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """Point d'entrée principal du script."""
    parser = argparse.ArgumentParser(
        description='Scrapling Official Skill pour Hermes Agent - Extracteur de contenu web',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python scrapling_scraper.py --url "https://example.com"
  python scrapling_scraper.py --config config.json
  python scrapling_scraper.py --url "https://example.com" --js --output results.json
  python scrapling_scraper.py --url "https://example.com" --selectors '{"title": "h1", "content": "article"}'
        """
    )

    parser.add_argument('--url', type=str, help='URL unique à scraper')
    parser.add_argument('--config', type=str, default='config.json', help='Chemin du fichier de configuration JSON')
    parser.add_argument('--output', type=str, default='results.json', help='Fichier de sortie (ou "-" pour stdout)')
    parser.add_argument('--js', action='store_true', help='Activer le rendu JavaScript via Playwright')
    parser.add_argument('--debug', action='store_true', help='Activer le mode debug')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout en secondes (défaut: 30)')
    parser.add_argument('--selectors', type=str, help='Sélecteurs CSS personnalisés au format JSON')

    args = parser.parse_args()

    # Déterminer les URLs à scraper
    urls = []
    custom_selectors = None

    if args.selectors:
        try:
            custom_selectors = json.loads(args.selectors)
        except json.JSONDecodeError as e:
            print(f"Erreur: Sélecteurs JSON invalides: {e}", file=sys.stderr)
            sys.exit(1)

    if args.url:
        urls = [args.url]
    elif os.path.exists(args.config):
        try:
            config = load_config(args.config)
            urls = config.get('urls', [])
            if not custom_selectors:
                custom_selectors = config.get('selectors', None)
        except Exception as e:
            print(f"Erreur de chargement du config: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Erreur: Spécifiez une URL avec --url ou un fichier de config avec --config", file=sys.stderr)
        sys.exit(1)

    if not urls:
        print("Erreur: Aucune URL à scraper", file=sys.stderr)
        sys.exit(1)

    # Initialiser le scraper
    scraper = ScraplingScraper(
        timeout=args.timeout,
        use_js=args.js,
        debug=args.debug
    )

    # Effectuer le scraping
    if len(urls) == 1:
        results = scraper.scrape_url(urls[0], custom_selectors)
    else:
        results = {'scraped_pages': scraper.scrape_multiple_urls(urls, custom_selectors)}

    # Formater la sortie
    if isinstance(results, dict) and 'scraped_pages' not in results:
        output_data = {'scraped_pages': [results]}
    else:
        output_data = results

    # Ajouter les métadonnées de l'extraction
    output_data['extraction_info'] = {
        'timestamp': datetime.now().isoformat(),
        'total_pages': len(output_data.get('scraped_pages', [])),
        'js_enabled': args.js
    }

    # Écrire la sortie
    output_json = json.dumps(output_data, indent=2, ensure_ascii=False)

    if args.output == '-':
        # Sortie stdout
        print(output_json)
    else:
        # Écrire dans un fichier
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"Résultats écrits dans: {args.output}", file=sys.stderr)

    # Afficher un résumé pour l'Agent
    scraped_pages = output_data.get('scraped_pages', [])
    print(f"\n# RÉSULTATS DU SCRAPPING", file=sys.stderr)
    print(f"Pages traitées: {len(scraped_pages)}", file=sys.stderr)
    for page in scraped_pages:
        print(f"  - {page.get('url', 'N/A')}: {page.get('title', 'Sans titre')[:50]}...", file=sys.stderr)


if __name__ == '__main__':
    main()
