"""
GitHub repository fetcher for gathering 3D model related data.

This module provides functionality to search and fetch GitHub repositories
that may contain relevant 3D model data or specifications.
"""

import requests


class GitHubFetcher:
    """
    Fetch repositories from GitHub to gather additional information for 3D model generation.
    """
    
    def __init__(self, api_token=None):
        """
        Initialize the GitHub fetcher.
        
        Args:
            api_token: Optional GitHub API token for authenticated requests
        """
        self.api_token = api_token
        self.base_url = "https://api.github.com"

    def fetch_repositories(self, query, sort="stars", order="desc"):
        """
        Search and fetch repositories from GitHub.
        
        Args:
            query: Search query string
            sort: Sort field (e.g., 'stars', 'forks', 'updated')
            order: Sort order ('asc' or 'desc')
            
        Returns:
            list: List of repository data dictionaries
        """
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"token {self.api_token}"
        url = f"{self.base_url}/search/repositories?q={query}&sort={sort}&order={order}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json().get("items", [])
            else:
                # Return empty list on error to avoid crashes
                return []
        except Exception:
            # Return empty list on any error to avoid crashes
            return []

    def parse_repository(self, repo):
        """
        Parse repository data and extract relevant information.
        
        Args:
            repo: Repository data dictionary from GitHub API
            
        Returns:
            dict: Parsed repository information
        """
        return {
            "name": repo.get("name"),
            "url": repo.get("html_url"),
            "description": repo.get("description"),
            "language": repo.get("language"),
            "stars": repo.get("stargazers_count"),
            "forks": repo.get("forks_count"),
            "created_at": repo.get("created_at"),
            "updated_at": repo.get("updated_at"),
        }
