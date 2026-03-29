#!/usr/bin/env python3
"""
Exemple d'utilisation du Reddit Miner (YARS)

Ce script démontre comment utiliser la classe YARS pour scraper Reddit.
Il suit l'exemple de code fourni dans la documentation Scrapling.

Usage:
    python reddit_example.py
"""

from reddit_miner import YARS, display_results, download_image


def main():
    """Exemple complet d'utilisation du Reddit Miner."""
    
    # Initialiser le miner
    miner = YARS()
    
    # 1. Search for posts related to "OpenAI"
    print("\n--- Recherche de posts sur 'OpenAI' ---")
    search_results = miner.search_reddit("OpenAI", limit=3)
    display_results(search_results, "SEARCH RESULTS")
    
    # 2. Scrape post details using its permalink
    print("\n--- Récupération des détails d'un post ---")
    permalink = "https://www.reddit.com/r/getdisciplined/comments/1frb5ib/what_single_health_test_or_practice_has/".split('reddit.com')[1]
    post_details = miner.scrape_post_details(permalink)
    if post_details:
        display_results(post_details, "POST DATA")
    else:
        print("Échec de la récupération des détails du post.")
    
    # 3. Fetch recent activity of user "iamsecb"
    print("\n--- Récupération des données utilisateur ---")
    user_data = miner.scrape_user_data("iamsecb", limit=2)
    display_results(user_data, "USER DATA")
    
    # 4. Fetch top posts from the subreddit "generative" from the past week
    print("\n--- Récupération des posts du subreddit 'generative' ---")
    subreddit_posts = miner.fetch_subreddit_posts("generative", limit=11, category="top", time_filter="week")
    display_results(subreddit_posts, "generative SUBREDDIT Top Posts (Week)")
    
    # 5. Download images from the fetched posts
    print("\n--- Téléchargement des images ---")
    for z in range(3):
        try:
            image_url = subreddit_posts[z]["image_url"]
        except (IndexError, KeyError):
            image_url = subreddit_posts[z]["thumbnail_url"]
        
        if image_url:
            print(f"Téléchargement de l'image {z+1}: {image_url}")
            download_image(image_url)
        else:
            print(f"Aucune image disponible pour le post {z+1}")


if __name__ == '__main__':
    main()
