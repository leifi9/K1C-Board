import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from urllib.parse import quote_plus


class WebSearch:
    def __init__(self, user_agent: str = None):
        self.user_agent = user_agent or 'Mozilla/5.0 (compatible; Auto3DAgent/1.0)'
        self.headers = {
            'User-Agent': self.user_agent
        }

    def search_web(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search the web for relevant 3D modeling resources.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with URLs and snippets
        """
        try:
            # Use DuckDuckGo HTML search (doesn't require API key)
            encoded_query = quote_plus(query + " 3D model")
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            # Parse HTML results
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Find result containers
            result_divs = soup.find_all('div', class_='result')
            
            for div in result_divs[:max_results]:
                try:
                    # Extract title
                    title_elem = div.find('a', class_='result__a')
                    title = title_elem.text.strip() if title_elem else ''
                    
                    # Extract URL
                    url_elem = div.find('a', class_='result__a')
                    result_url = url_elem.get('href', '') if url_elem else ''
                    
                    # Extract snippet
                    snippet_elem = div.find('a', class_='result__snippet')
                    snippet = snippet_elem.text.strip() if snippet_elem else ''
                    
                    if title and result_url:
                        results.append({
                            'title': title,
                            'url': result_url,
                            'snippet': snippet,
                            'source': 'web_search'
                        })
                except Exception:
                    continue
            
            return results
            
        except Exception as e:
            # Return empty list on error to avoid crashes
            return []

    def fetch_results(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fetch and process content from search result URLs.
        
        Args:
            search_results: List of search results with URLs
            
        Returns:
            List of processed results with extracted content
        """
        processed_results = []
        
        for result in search_results:
            try:
                url = result.get('url', '')
                if not url:
                    continue
                
                # Fetch the page content
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    continue
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(['script', 'style']):
                    script.decompose()
                
                # Extract text content
                text = soup.get_text()
                
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Limit text length
                max_length = 1000
                if len(text) > max_length:
                    text = text[:max_length] + '...'
                
                processed_results.append({
                    'title': result.get('title', ''),
                    'url': url,
                    'snippet': result.get('snippet', ''),
                    'content': text,
                    'source': result.get('source', 'web_search')
                })
                
            except Exception:
                # Skip failed fetches
                continue
        
        return processed_results
    
    def search_specific_sites(self, query: str, sites: List[str]) -> List[Dict[str, Any]]:
        """
        Search specific sites for 3D modeling resources.
        
        Args:
            query: Search query
            sites: List of site domains to search (e.g., ['thingiverse.com', 'grabcad.com'])
            
        Returns:
            List of search results from specified sites
        """
        all_results = []
        
        for site in sites:
            site_query = f"site:{site} {query}"
            results = self.search_web(site_query, max_results=5)
            all_results.extend(results)
        
        return all_results
