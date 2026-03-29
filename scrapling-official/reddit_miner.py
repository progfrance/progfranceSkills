#!/usr/bin/env python3
"""
Reddit Miner - YARS (Yet Another Reddit Scraper)
Un scraper spécialisé pour Reddit utilisant Scrapling.

Ce module fournit des méthodes pour:
- Rechercher des posts sur Reddit
- Récupérer les détails d'un post
- Obtenir les données d'un utilisateur
- Récupérer les posts d'un subreddit
- Télécharger des images depuis Reddit

Usage:
    from reddit_miner import YARS
    
    miner = YARS()
    results = miner.search_reddit("OpenAI", limit=3)
"""

import os
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import de Scrapling pour le parsing HTML
try:
    from scrapling import Fetcher, Adaptor
except ImportError:
    print("Erreur: Scrapling n'est pas installé. Exécutez: pip install scrapling")
    Fetcher = None
    Adaptor = None

# Pour le téléchargement d'images
try:
    import PIL.Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class YARS:
    """
    Yet Another Reddit Scraper (YARS)
    
    Classe principale pour le scraping de Reddit.
    Fournit une interface simple pour extraire des données depuis Reddit.
    """
    
    # Base URL de l'API Reddit
    REDDIT_BASE_URL = "https://www.reddit.com"
    REDDIT_API_URL = "https://www.reddit.com"
    
    # Catégories de posts disponibles
    POST_CATEGORIES = ["hot", "new", "top", "rising", "controversial"]
    
    # Intervals de temps pour les filtres
    TIME_FILTERS = ["hour", "day", "week", "month", "year", "all"]
    
    def __init__(self, timeout: int = 30, debug: bool = False):
        """
        Initialiser le Reddit Miner.
        
        Args:
            timeout: Timeout en secondes pour les requêtes
            debug: Activer le mode debug
        """
        self.timeout = timeout
        self.debug = debug
        self.fetcher = Fetcher(
            auto_save=True,
            storage_path='.scrapling_cache',
            timeout=timeout * 1000
        ) if Fetcher else None
        
        # Headers pour les requêtes HTTP
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        self.log("Reddit Miner initialisé", "info")
    
    def log(self, message: str, level: str = "info"):
        """Afficher un message de log si le mode debug est activé."""
        if self.debug:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level.upper()}] {message}")
    
    def search_reddit(self, query: str, limit: int = 10, subreddit: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Rechercher des posts sur Reddit.
        
        Args:
            query: Terme de recherche
            limit: Nombre maximum de résultats
            subreddit: Subreddit spécifique (optionnel)
            
        Returns:
            Liste des posts trouvés
        """
        self.log(f"Recherche: '{query}' (limit={limit})", "info")
        
        results = []
        
        # Construire l'URL de recherche
        if subreddit:
            search_url = f"{self.REDDIT_API_URL}/r/{subreddit}/search.json"
            params = {
                'q': query,
                'limit': limit,
                'sort': 'relevance',
                'restrict_sr': 1
            }
        else:
            search_url = f"{self.REDDIT_API_URL}/search.json"
            params = {
                'q': query,
                'limit': limit,
                'sort': 'relevance',
                'restrict_sr': 0
            }
        
        try:
            response = requests.get(search_url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Extraire les posts depuis la réponse JSON
            if 'data' in data and 'children' in data['data']:
                for child in data['data']['children']:
                    post_data = child.get('data', {})
                    post_info = self._parse_post_data(post_data)
                    results.append(post_info)
            
            self.log(f"Recherche terminée: {len(results)} résultats trouvés", "info")
            
        except requests.RequestException as e:
            self.log(f"Erreur lors de la recherche: {e}", "error")
        except Exception as e:
            self.log(f"Erreur inattendue: {e}", "error")
        
        return results
    
    def scrape_post_details(self, permalink: str) -> Optional[Dict[str, Any]]:
        """
        Récupérer les détails d'un post Reddit.
        
        Args:
            permalink: Permalink du post (ex: /r/subreddit/comments/abc123/title/)
            
        Returns:
            Dictionnaire avec les détails du post
        """
        self.log(f"Récupération des détails du post: {permalink}", "info")
        
        # S'assurer que le permalink commence par /
        if not permalink.startswith('/'):
            permalink = '/' + permalink
        
        # Ajouter .json pour obtenir les données structurées
        json_url = f"{self.REDDIT_API_URL}{permalink}.json"
        
        try:
            response = requests.get(json_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Reddit retourne une liste avec 2 éléments: le post et les commentaires
            if isinstance(data, list) and len(data) > 0:
                post_data = data[0].get('data', {}).get('children', [{}])[0].get('data', {})
                
                # Si le post n'est pas dans cette structure, essayer directement
                if not post_data and len(data) > 0:
                    post_data = data[0].get('data', {})
                
                post_info = self._parse_post_data(post_data)
                
                # Ajouter les commentaires si disponibles
                if isinstance(data, list) and len(data) > 1:
                    comments = data[1].get('data', {}).get('children', [])
                    post_info['comments'] = [self._parse_comment(c.get('data', {})) for c in comments if c.get('data')]
                
                self.log(f"Détails du post récupérés: {post_info.get('title', 'N/A')}", "info")
                return post_info
            
        except requests.RequestException as e:
            self.log(f"Erreur lors de la récupération: {e}", "error")
        except Exception as e:
            self.log(f"Erreur inattendue: {e}", "error")
        
        return None
    
    def scrape_user_data(self, username: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Récupérer les données d'un utilisateur Reddit.
        
        Args:
            username: Nom d'utilisateur
            limit: Nombre de posts récents à récupérer
            
        Returns:
            Dictionnaire avec les données de l'utilisateur
        """
        self.log(f"Récupération des données utilisateur: {username}", "info")
        
        # URL pour les posts de l'utilisateur
        user_posts_url = f"{self.REDDIT_API_URL}/user/{username}.json"
        
        try:
            response = requests.get(user_posts_url, params={'limit': limit}, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            user_info = {
                'username': username,
                'posts': [],
                'karma': None,
                'created_utc': None
            }
            
            # Extraire les posts
            if 'data' in data and 'children' in data['data']:
                for child in data['data']['children']:
                    post_data = child.get('data', {})
                    post_info = self._parse_post_data(post_data)
                    user_info['posts'].append(post_info)
                    
                    # Extraire les infos utilisateur du premier post
                    if not user_info['karma'] and 'author_fullname' in post_data:
                        user_info['karma'] = post_data.get('link_karma', 0) + post_data.get('comment_karma', 0)
            
            # Essayer de récupérer plus de détails via la page profil
            profile_url = f"{self.REDDIT_API_URL}/user/{username}/about.json"
            profile_response = requests.get(profile_url, headers=self.headers, timeout=self.timeout)
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                profile_info = profile_data.get('data', {})
                user_info['karma'] = profile_info.get('link_karma', 0) + profile_info.get('comment_karma', 0)
                user_info['created_utc'] = profile_info.get('created_utc')
                user_info['is_gold'] = profile_info.get('is_gold', False)
                user_info['is_mod'] = profile_info.get('is_mod', False)
            
            self.log(f"Données utilisateur récupérées: {user_info.get('username', 'N/A')}", "info")
            return user_info
            
        except requests.RequestException as e:
            self.log(f"Erreur lors de la récupération: {e}", "error")
        except Exception as e:
            self.log(f"Erreur inattendue: {e}", "error")
        
        return None
    
    def fetch_subreddit_posts(self, subreddit: str, limit: int = 10, category: str = "hot", 
                              time_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupérer les posts d'un subreddit.
        
        Args:
            subreddit: Nom du subreddit
            limit: Nombre de posts à récupérer
            category: Catégorie (hot, new, top, rising, controversial)
            time_filter: Filtre temporel (hour, day, week, month, year, all) - seulement pour 'top'
            
        Returns:
            Liste des posts du subreddit
        """
        self.log(f"Récupération des posts de r/{subreddit} (category={category}, limit={limit})", "info")
        
        # Valider la catégorie
        if category not in self.POST_CATEGORIES:
            self.log(f"Catégorie invalide: {category}, utilisation de 'hot' par défaut", "warning")
            category = "hot"
        
        # Construire l'URL
        url = f"{self.REDDIT_API_URL}/r/{subreddit}/{category}.json"
        
        params = {'limit': limit}
        
        # Ajouter le filtre temporel si applicable
        if time_filter and category == "top" and time_filter in self.TIME_FILTERS:
            params['t'] = time_filter
        
        results = []
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Extraire les posts
            if 'data' in data and 'children' in data['data']:
                for child in data['data']['children']:
                    post_data = child.get('data', {})
                    post_info = self._parse_post_data(post_data)
                    results.append(post_info)
            
            self.log(f"Posts récupérés: {len(results)} posts pour r/{subreddit}", "info")
            
        except requests.RequestException as e:
            self.log(f"Erreur lors de la récupération: {e}", "error")
        except Exception as e:
            self.log(f"Erreur inattendue: {e}", "error")
        
        return results
    
    def _parse_post_data(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parser les données d'un post Reddit.
        
        Args:
            post_data: Données brutes du post
            
        Returns:
            Dictionnaire formaté avec les informations du post
        """
        # Déterminer l'URL de l'image
        image_url = None
        thumbnail_url = post_data.get('thumbnail', '')
        
        # Vérifier si le post est un lien vers une image
        if post_data.get('is_video'):
            # Pour les vidéos, essayer d'obtenir la prévisualisation
            preview = post_data.get('secure_media', {}).get('reddit_video', {})
            if preview:
                image_url = preview.get('fallback_url')
        elif post_data.get('url'):
            url = post_data.get('url', '')
            if url.startswith('http'):
                # Vérifier si c'est une image
                if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    image_url = url
                elif 'imgur' in url.lower():
                    image_url = url
                elif 'i.reddit.com' in url.lower():
                    image_url = url
        
        # Si pas d'image, utiliser le thumbnail
        if not image_url and thumbnail_url and thumbnail_url != 'self':
            image_url = thumbnail_url
        
        return {
            'id': post_data.get('id'),
            'title': post_data.get('title', ''),
            'author': post_data.get('author', ''),
            'subreddit': post_data.get('subreddit', ''),
            'url': post_data.get('url', ''),
            'permalink': post_data.get('permalink', ''),
            'score': post_data.get('score', 0),
            'upvote_ratio': post_data.get('upvote_ratio', 0),
            'num_comments': post_data.get('num_comments', 0),
            'created_utc': post_data.get('created_utc'),
            'selftext': post_data.get('selftext', ''),
            'is_video': post_data.get('is_video', False),
            'is_self': post_data.get('is_self', False),
            'image_url': image_url,
            'thumbnail_url': thumbnail_url,
            'flair': post_data.get('link_flair_text', ''),
            'awards': post_data.get('all_awardings', [])
        }
    
    def _parse_comment(self, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parser les données d'un commentaire Reddit.
        
        Args:
            comment_data: Données brutes du commentaire
            
        Returns:
            Dictionnaire formaté avec les informations du commentaire
        """
        return {
            'id': comment_data.get('id'),
            'author': comment_data.get('author', ''),
            'body': comment_data.get('body', ''),
            'score': comment_data.get('score', 0),
            'created_utc': comment_data.get('created_utc'),
            'replies': []  # Les réponses imbriquées ne sont pas traitées ici
        }


def download_image(image_url: str, output_dir: str = "downloads") -> Optional[str]:
    """
    Télécharger une image depuis une URL.
    
    Args:
        image_url: URL de l'image à télécharger
        output_dir: Répertoire de sortie
        
    Returns:
        Chemin du fichier téléchargé ou None en cas d'erreur
    """
    try:
        # Créer le répertoire de sortie s'il n'existe pas
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Générer un nom de fichier unique
        timestamp = int(time.time() * 1000)
        filename = f"reddit_image_{timestamp}.jpg"
        file_path = output_path / filename
        
        # Télécharger l'image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(image_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Écrire le fichier
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Image téléchargée: {file_path}")
        return str(file_path)
        
    except requests.RequestException as e:
        print(f"Erreur lors du téléchargement: {e}")
    except Exception as e:
        print(f"Erreur inattendue: {e}")
    
    return None


def display_results(data: Any, title: str = "RESULTS"):
    """
    Afficher les résultats de manière formatée.
    
    Args:
        data: Données à afficher (dict, list, ou autre)
        title: Titre de la section
    """
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")
    
    if data is None:
        print("Aucune donnée à afficher")
    elif isinstance(data, list):
        print(f"Nombre d'éléments: {len(data)}\n")
        for i, item in enumerate(data, 1):
            print(f"\n--- Élément {i} ---")
            if isinstance(item, dict):
                for key, value in item.items():
                    if key in ['awards', 'comments']:
                        continue  # Ignorer les champs trop détaillés
                    if key == 'selftext' and len(str(value)) > 200:
                        print(f"  {key}: {str(value)[:200]}...")
                    else:
                        print(f"  {key}: {value}")
            else:
                print(f"  {item}")
    elif isinstance(data, dict):
        for key, value in data.items():
            if key in ['awards', 'comments']:
                continue  # Ignorer les champs trop détaillés
            if key == 'selftext' and len(str(value)) > 200:
                print(f"  {key}: {str(value)[:200]}...")
            else:
                print(f"  {key}: {value}")
    else:
        print(data)
    
    print(f"{'='*60}\n")


# Alias pour compatibilité avec l'exemple
def main():
    """Exemple d'utilisation du Reddit Miner."""
    print("Reddit Miner - YARS Example")
    print("="*60)
    
    # Initialiser le miner
    miner = YARS(debug=True)
    
    # Exemple de recherche
    print("\n1. Recherche de posts sur 'OpenAI'...")
    search_results = miner.search_reddit("OpenAI", limit=3)
    display_results(search_results, "SEARCH RESULTS")
    
    # Exemple de récupération de détails d'un post
    if search_results:
        print("\n2. Récupération des détails d'un post...")
        permalink = search_results[0].get('permalink', '')
        if permalink:
            post_details = miner.scrape_post_details(permalink)
            display_results(post_details, "POST DETAILS")
    
    # Exemple de récupération des données utilisateur
    print("\n3. Récupération des données utilisateur...")
    user_data = miner.scrape_user_data("iamsecb", limit=2)
    display_results(user_data, "USER DATA")
    
    # Exemple de récupération des posts d'un subreddit
    print("\n4. Récupération des posts d'un subreddit...")
    subreddit_posts = miner.fetch_subreddit_posts("generative", limit=5, category="top", time_filter="week")
    display_results(subreddit_posts, "SUBREDDIT POSTS")
    
    # Exemple de téléchargement d'image
    if subreddit_posts:
        print("\n5. Téléchargement d'images...")
        for i, post in enumerate(subreddit_posts[:3]):
            image_url = post.get('image_url') or post.get('thumbnail_url')
            if image_url:
                print(f"Téléchargement de l'image {i+1}: {image_url}")
                download_image(image_url)


if __name__ == '__main__':
    main()
