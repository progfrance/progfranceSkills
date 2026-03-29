#!/usr/bin/env python3
"""
RSS Aggregator & Smart Scraper avec Scrapling

Ce script extrait des actualités depuis des flux RSS et utilise Scrapling
pour extraire le contenu des pages web de manière plus performante et robuste
que trafilatura.

Usage:
    python fetch_news.py --days 1 --opml references/feeds.opml
"""

import argparse
import datetime
import feedparser
import xml.etree.ElementTree as ET
import concurrent.futures
import time
import sys
import os
import re
import logging
from html import unescape
from typing import Dict, List, Optional, Any

# Import de Scrapling pour l'extraction de contenu
try:
    from scrapling import Fetcher, Adaptor
    SCRAPLING_AVAILABLE = True
except ImportError:
    print("Erreur: Scrapling n'est pas installé. Exécutez: pip install scrapling", file=sys.stderr)
    SCRAPLING_AVAILABLE = False
    Fetcher = None
    Adaptor = None

# Rendre scrapling silencieux pour ne pas polluer la sortie de l'Agent
logging.getLogger('scrapling').setLevel(logging.WARNING)


def clean_text(text: str, max_chars: int = 8000) -> str:
    """Nettoie le HTML et limite la taille pour ne pas exploser la fenêtre de contexte de l'IA."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = unescape(text)
    text = ' '.join(text.split())
    if len(text) > max_chars:
        return text[:max_chars] + "..."
    return text


def parse_opml(opml_path: str) -> List[str]:
    """Extrait les URLs depuis le fichier OPML."""
    urls = []
    try:
        tree = ET.parse(opml_path)
        root = tree.getroot()
        for outline in root.findall(".//outline"):
            url = outline.get('xmlUrl')
            if url:
                url = url.strip().strip('`').strip('"').strip("'")
                urls.append(url)
    except Exception as e:
        print(f"Erreur lecture OPML: {e}", file=sys.stderr)
    return urls


def get_entry_date(entry: Any) -> Optional[datetime.datetime]:
    """Tente de récupérer la date de publication."""
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return datetime.datetime.fromtimestamp(time.mktime(entry.published_parsed))
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        return datetime.datetime.fromtimestamp(time.mktime(entry.updated_parsed))
    return None


class ScraplingExtractor:
    """
    Extracteur de contenu utilisant Scrapling.
    Plus rapide et plus robuste que trafilatura.
    """
    
    # Sélecteurs CSS pour extraire le contenu principal
    CONTENT_SELECTORS = [
        'article',
        'main',
        'div.article-content',
        'div.content',
        'div.post-content',
        'div.entry-content',
        'article.post',
        'div.article',
        'div.story-content',
        'div.page-content',
        'section.content',
        'div.body-text',
        'div.article-body'
    ]
    
    TITLE_SELECTORS = [
        'h1.article-title',
        'h1.title',
        'h1',
        'meta[property="og:title"]',
        'title'
    ]
    
    def __init__(self, timeout: int = 30):
        """Initialiser l'extracteur Scrapling."""
        self.timeout = timeout
        self.fetcher = Fetcher(
            auto_save=True,
            storage_path='.scrapling_cache',
            timeout=timeout * 1000
        ) if Fetcher else None
    
    def extract_content(self, url: str) -> Optional[str]:
        """
        Extraire le contenu principal d'une page web.
        
        Args:
            url: URL de la page à extraire
            
        Returns:
            Le contenu textuel extrait ou None en cas d'erreur
        """
        if not SCRAPLING_AVAILABLE or not self.fetcher:
            return None
        
        try:
            # Récupérer la page avec Scrapling
            response = self.fetcher.get(url, headless=False, timeout=self.timeout * 1000)
            
            if not response or not response.text:
                return None
            
            # Créer un adaptor Scrapling
            adaptor = Adaptor(response.text, url=url)
            
            # Essayer d'extraire le contenu avec les sélecteurs
            content = None
            for selector in self.CONTENT_SELECTORS:
                try:
                    elements = adaptor.lxml.css_select(selector)
                    if elements:
                        content = elements[0].text_content().strip()
                        if content and len(content) > 100:
                            break
                except Exception:
                    continue
            
            # Si aucun contenu trouvé, essayer avec l'extraction automatique de Scrapling
            if not content:
                try:
                    # Scrapling peut détecter automatiquement le contenu principal
                    content = adaptor.get_text()
                except Exception:
                    pass
            
            if content:
                # Nettoyer le contenu
                content = self._clean_content(content)
                return content
            
        except Exception as e:
            print(f" [Scrapling Error] sur {url}: {e}", file=sys.stderr)
        
        return None
    
    def _clean_content(self, content: str) -> str:
        """Nettoyer le contenu extrait."""
        import re
        
        # Supprimer les espaces multiples
        content = re.sub(r'\s+', ' ', content)
        
        # Supprimer les lignes vides excessives
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        return content.strip()


def process_feed(url: str, cutoff_date: datetime.datetime, max_entries: int = 10) -> List[Dict[str, Any]]:
    """Traite un flux RSS individuel avec Scrapling pour le deep scraping."""
    updates = []
    
    # Optimisation Reddit issue de ton ancien script
    if "reddit.com" in url and "/comments/" not in url and not url.endswith(".rss"):
        url = url.rstrip("/") + ".rss"
    
    print(f"Recherche sur : {url}", file=sys.stderr)
    
    # Initialiser l'extracteur Scrapling
    extractor = ScraplingExtractor(timeout=30)
    
    try:
        feed = feedparser.parse(url)
        if getattr(feed, 'bozo', False) and not feed.entries:
            return []
        
        feed_title = feed.feed.get('title', url)
        
        for entry in feed.entries[:max_entries]:
            entry_date = get_entry_date(entry)
            if not entry_date or entry_date < cutoff_date:
                continue
            
            title = entry.get('title', 'Sans titre')
            link = entry.get('link', url)
            
            # Chercher le contenu initial dans le RSS
            content = entry.get('summary', entry.get('description', ''))
            if not content and 'content' in entry:
                content = entry.content[0].value
            
            content = clean_text(content)
            
            # --- DEEP SCRAPING AVEC SCRAPLING ---
            # Si le contenu est trop court (<200 chars) et que ce n'est pas Reddit, on va lire la page web
            if len(content) < 200 and link and "reddit.com" not in link:
                extracted = extractor.extract_content(link)
                if extracted:
                    content = clean_text(extracted)
            
            updates.append({
                'feed_title': feed_title,
                'title': title,
                'content': content,
                'updated': entry_date,
                'link': link
            })
    except Exception as e:
        # Erreur silencieuse envoyée dans stderr pour le debug
        print(f"Erreur traitement de {url}: {e}", file=sys.stderr)
    
    return updates


def main():
    parser = argparse.ArgumentParser(description='RSS Aggregator & Smart Scraper avec Scrapling')
    parser.add_argument('--days', type=int, default=1, help='Nombre de jours à remonter')
    parser.add_argument('--opml', type=str, default='references/feeds.opml', help='Chemin du fichier OPML')
    parser.add_argument('--max-entries', type=int, default=10, help='Max articles scannés par flux')
    args = parser.parse_args()
    
    # Gestion propre des chemins
    script_dir = os.path.dirname(os.path.abspath(__file__))
    opml_path = args.opml
    if not os.path.isabs(opml_path):
        if not os.path.exists(opml_path):
            skill_root = os.path.dirname(script_dir)
            opml_path = os.path.join(skill_root, args.opml)
    
    if not os.path.exists(opml_path):
        print(f"Erreur : OPML introuvable ({opml_path})", file=sys.stderr)
        sys.exit(1)
    
    urls = parse_opml(opml_path)
    if not urls:
        print("Aucune URL trouvée dans l'OPML.", file=sys.stderr)
        sys.exit(0)
    
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=args.days)
    all_updates = []
    
    # Traitement parallèle sécurisé avec un timeout
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(process_feed, url, cutoff_date, args.max_entries): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            try:
                # Si un site bloque, on timeout au bout de 20 secondes
                data = future.result(timeout=20)
                all_updates.extend(data)
            except concurrent.futures.TimeoutError:
                print("Timeout sur une URL", file=sys.stderr)
            except Exception as exc:
                print(f"Exception générée : {exc}", file=sys.stderr)
    
    all_updates.sort(key=lambda x: x['updated'], reverse=True)
    
    if not all_updates:
        print("Aucune nouvelle information trouvée dans le laps de temps imparti.")
        return
    
    # FORMATAGE POUR L'AGENT IA
    # On renvoie le brut structuré, c'est l'IA qui fera le résumé final !
    print("# CONTEXTE D'ACTUALITÉS EXTRAIT\n")
    print("INSTRUCTION SYSTÈME : Voici les articles complets. Lis-les attentivement puis génère ta réponse à l'utilisateur en suivant les instructions de formatage définies dans ton SKILL.md.\n")
    
    for i, item in enumerate(all_updates, 1):
        print(f"## ARTICLE {i}")
        print(f"**Source** : {item['feed_title']}")
        print(f"**Titre** : {item['title']}")
        print(f"**Date** : {item['updated'].strftime('%Y-%m-%d %H:%M')}")
        print(f"**Lien** : {item['link']}")
        print(f"**Contenu Extrait** :\n{item['content']}\n")
        print("-" * 50 + "\n")


if __name__ == '__main__':
    main()
