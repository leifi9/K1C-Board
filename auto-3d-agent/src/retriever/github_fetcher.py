import requests

class GitHubFetcher:
    def __init__(self, api_token=None):
        self.api_token = api_token
        self.base_url = "https://api.github.com"

    def fetch_repositories(self, query, sort="stars", order="desc"):
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"token {self.api_token}"
        url = f"{self.base_url}/search/repositories?q={query}&sort={sort}&order={order}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            # Return empty list on error to avoid crashes
            return []

    def parse_repository(self, repo):
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
