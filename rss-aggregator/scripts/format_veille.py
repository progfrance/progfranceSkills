#!/usr/bin/env python3
import argparse
import datetime
import feedparser
import xml.etree.ElementTree as ET
import concurrent.futures
import time
import sys
import os
import re
from html import unescape

def clean_summary(summary, max_chars=800):
    if not summary:
        return "No summary available."
    text = re.sub(r'<[^>]+>', '', summary)
    text = unescape(text)
    text = ' '.join(text.split())
    if len(text) > max_chars:
        return text[:max_chars-3] + "..."
    return text

def parse_opml(opml_path):
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
        print(f"Error parsing OPML: {e}", file=sys.stderr)
    return urls

def get_entry_date(entry):
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return datetime.datetime.fromtimestamp(time.mktime(entry.published_parsed))
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        return datetime.datetime.fromtimestamp(time.mktime(entry.updated_parsed))
    return None

def process_feed(url, cutoff_date, max_entries=20):
    updates = []
    try:
        feed = feedparser.parse(url)
        if feed.bozo and not feed.entries:
            return []
        feed_title = feed.feed.get('title', url)
        # Limite le nombre d'entrées traitées
        for entry in feed.entries[:max_entries]:
            entry_date = get_entry_date(entry)
            if not entry_date:
                continue
            if entry_date >= cutoff_date:
                summary = entry.get('summary', entry.get('description', ''))
                updates.append({
                    'feed_title': feed_title,
                    'title': entry.get('title', 'No Title'),
                    'author': entry.get('author', feed.feed.get('author', 'Unknown')),
                    'summary': clean_summary(summary),
                    'updated': entry_date,
                    'link': entry.get('link', '')
                })
    except Exception as e:
        pass
    return updates

def determine_theme(title, summary):
    text = (title + " " + summary).lower()
    if any(word in text for word in ['ia', 'intelligence artificielle', 'modèle', 'llm', 'gpt', 'claude', 'gemini', 'openai', 'anthropic', 'deep learning', 'machine learning', 'réseau de neurones']):
        return "IA"
    elif any(word in text for word in ['sécurité', 'cyber', 'vulnérabilité', 'hack', 'malware', 'phishing', 'ransomware', 'défense', 'attaque', 'confidentialité', 'chiffrement']):
        return "Cybersécurité"
    elif any(word in text for word in ['matériel', 'hardware', 'gpu', 'cpu', 'puce', 'semi-conducteur', 'nvidia', 'amd', 'intel', 'quantique', 'robotique']):
        return "Hardware"
    else:
        return "Autres"

def main():
    parser = argparse.ArgumentParser(description='RSS Aggregator for Veille Odyssee')
    parser.add_argument('--days', type=int, default=1, help='Number of days to look back')
    parser.add_argument('--opml', type=str, default='references/feeds.opml', help='Path to OPML file')
    # Ajout du nouvel argument
    parser.add_argument('--max-entries', type=int, default=20, help='Maximum number of entries to process per feed')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    opml_path = args.opml
    if not os.path.isabs(opml_path):
        if not os.path.exists(opml_path):
            skill_root = os.path.dirname(script_dir)
            opml_path = os.path.join(skill_root, args.opml)

    if not os.path.exists(opml_path):
        print(f"OPML file not found: {opml_path}", file=sys.stderr)
        sys.exit(1)

    urls = parse_opml(opml_path)
    if not urls:
        print("No URLs found in OPML.", file=sys.stderr)
        sys.exit(0)

    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=args.days)

    all_updates = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # On passe args.max_entries à process_feed
        future_to_url = {executor.submit(process_feed, url, cutoff_date, args.max_entries): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            data = future.result()
            all_updates.extend(data)

    all_updates.sort(key=lambda x: x['updated'], reverse=True)

    if not all_updates:
        print("No updates found.")
        return

    # Group by theme
    grouped = {}
    for item in all_updates:
        theme = determine_theme(item['title'], item['summary'])
        if theme not in grouped:
            grouped[theme] = []
        grouped[theme].append(item)

    # Output in required format
    print(f"Veille technologique du {datetime.datetime.now().strftime('%d/%m/%Y')}\n")
    for theme, items in grouped.items():
        print(f"## {theme}")
        for item in items:
            # Create a 2-sentence summary from the cleaned summary
            summary = item['summary']
            # Take first two sentences, or split by '. ' and take first two parts
            sentences = summary.split('. ')
            if len(sentences) >= 2:
                two_sentences = '. '.join(sentences[:2]) + '.'
            else:
                two_sentences = summary if summary.endswith('.') else summary + '.'
            # Ensure it's not too long; truncate if needed
            if len(two_sentences) > 300:
                two_sentences = two_sentences[:297] + '...'
            print(f"* [{item['title']}] : {two_sentences}")
            print(f"Source : {item['link']}\n")

if __name__ == '__main__':
    main()