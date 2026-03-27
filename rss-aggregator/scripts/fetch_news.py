#!/usr/bin/env python3
import argparse
import datetime
import feedparser
import trafilatura
import xml.etree.ElementTree as ET
import concurrent.futures
import time
import sys
import os
import re
import logging
from html import unescape

# Rendre trafilatura silencieux pour ne pas polluer la sortie de l'Agent
logging.getLogger('trafilatura').setLevel(logging.WARNING)

def clean_text(text, max_chars=8000):
    """Nettoie le HTML et limite la taille pour ne pas exploser la fenêtre de contexte de l'IA."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = unescape(text)
    text = ' '.join(text.split())
    if len(text) > max_chars:
        return text[:max_chars] + "..."
    return text

def parse_opml(opml_path):
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

def get_entry_date(entry):
    """Tente de récupérer la date de publication."""
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return datetime.datetime.fromtimestamp(time.mktime(entry.published_parsed))
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        return datetime.datetime.fromtimestamp(time.mktime(entry.updated_parsed))
    return None

def process_feed(url, cutoff_date, max_entries=10):
    """Traite un flux RSS individuel avec Deep Scraping si nécessaire."""
    updates = []
    
    # Optimisation Reddit issue de ton ancien script
    if "reddit.com" in url and "/comments/" not in url and not url.endswith(".rss"):
        url = url.rstrip("/") + ".rss"
        
    print(f"Recherche sur : {url}", file=sys.stderr)
    
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
            
            # --- DEEP SCRAPING ---
            # Si le contenu est trop court (<200 chars) et que ce n'est pas Reddit, on va lire la page web
            if len(content) < 200 and link and "reddit.com" not in link:
                try:
                    downloaded = trafilatura.fetch_url(link)
                    if downloaded:
                        extracted = trafilatura.extract(downloaded)
                        if extracted:
                            content = clean_text(extracted)
                except Exception as e:
                    print(f"  [Trafilatura Error] sur {link}: {e}", file=sys.stderr)

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
    parser = argparse.ArgumentParser(description='RSS Aggregator & Smart Scraper')
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
