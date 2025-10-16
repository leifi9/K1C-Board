import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus


class RedditFetcher:
    def __init__(self, subreddit: str = None):
        self.subreddit = subreddit or "3Dmodeling"
        self.base_url = "https://www.reddit.com"
        self.headers = {
            'User-Agent': 'Auto3DAgent/1.0'
        }

    def fetch_posts(self, query: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch posts from the specified subreddit using Reddit's JSON API.
        
        Args:
            query: Optional search query to filter posts
            limit: Maximum number of posts to fetch
            
        Returns:
            List of post dictionaries with relevant information
        """
        try:
            if query:
                # Search within subreddit
                encoded_query = quote_plus(query)
                url = f"{self.base_url}/r/{self.subreddit}/search.json"
                params = {
                    'q': query,
                    'restrict_sr': 'on',
                    'limit': limit,
                    'sort': 'relevance'
                }
            else:
                # Get hot posts from subreddit
                url = f"{self.base_url}/r/{self.subreddit}/hot.json"
                params = {'limit': limit}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            
            if 'data' not in data or 'children' not in data['data']:
                return []
            
            posts = []
            for child in data['data']['children']:
                post_data = child.get('data', {})
                parsed_post = self.parse_post(post_data)
                if parsed_post:
                    posts.append(parsed_post)
            
            return posts
            
        except Exception as e:
            # Return empty list on error to avoid crashes
            return []

    def parse_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a single Reddit post and extract relevant information.
        
        Args:
            post: Raw post data from Reddit API
            
        Returns:
            Dictionary with parsed post information
        """
        try:
            if not post:
                return {}
            
            parsed = {
                'title': post.get('title', ''),
                'author': post.get('author', ''),
                'subreddit': post.get('subreddit', ''),
                'score': post.get('score', 0),
                'num_comments': post.get('num_comments', 0),
                'url': f"{self.base_url}{post.get('permalink', '')}",
                'created_utc': post.get('created_utc', 0),
                'selftext': post.get('selftext', ''),
                'is_self': post.get('is_self', False),
                'link_url': post.get('url', ''),
                'thumbnail': post.get('thumbnail', ''),
                'post_hint': post.get('post_hint', ''),
            }
            
            # Extract image/video URLs if available
            if 'preview' in post and 'images' in post['preview']:
                images = post['preview']['images']
                if images:
                    source = images[0].get('source', {})
                    parsed['image_url'] = source.get('url', '')
            
            # Check for media content
            if 'media' in post and post['media']:
                parsed['has_media'] = True
            else:
                parsed['has_media'] = False
            
            return parsed
            
        except Exception:
            return {}
    
    def fetch_from_multiple_subreddits(self, subreddits: List[str], 
                                       query: Optional[str] = None, 
                                       limit_per_sub: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch posts from multiple subreddits.
        
        Args:
            subreddits: List of subreddit names
            query: Optional search query
            limit_per_sub: Maximum posts per subreddit
            
        Returns:
            Combined list of posts from all subreddits
        """
        all_posts = []
        
        for subreddit in subreddits:
            original_subreddit = self.subreddit
            self.subreddit = subreddit
            
            posts = self.fetch_posts(query=query, limit=limit_per_sub)
            all_posts.extend(posts)
            
            self.subreddit = original_subreddit
        
        # Sort by score
        all_posts.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return all_posts
    
    def get_top_posts(self, time_filter: str = 'week', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top posts from subreddit for a given time period.
        
        Args:
            time_filter: Time period ('hour', 'day', 'week', 'month', 'year', 'all')
            limit: Maximum number of posts
            
        Returns:
            List of top posts
        """
        try:
            url = f"{self.base_url}/r/{self.subreddit}/top.json"
            params = {
                't': time_filter,
                'limit': limit
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            
            if 'data' not in data or 'children' not in data['data']:
                return []
            
            posts = []
            for child in data['data']['children']:
                post_data = child.get('data', {})
                parsed_post = self.parse_post(post_data)
                if parsed_post:
                    posts.append(parsed_post)
            
            return posts
            
        except Exception:
            return []
