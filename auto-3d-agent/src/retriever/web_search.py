"""Simple web search helper with optional provider backends.

This module supports two providers:

1. SerpAPI (if SERPAPI_API_KEY is provided in the environment). This offers true
   web search results via Google's public API and returns the most relevant
   snippets.
2. DuckDuckGo Instant Answer API (fallback). This requires no API key and gives
   a lightweight set of related topics/snippets for the query.

All results are normalised into dictionaries that include title, snippet, url
and provider information so that downstream processes can present them in the
UI or logs.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict
from typing import Iterable, List, Optional

import requests

SERPAPI_ENDPOINT = "https://serpapi.com/search"
DUCKDUCKGO_ENDPOINT = "https://api.duckduckgo.com/"
DEFAULT_TIMEOUT = int(os.environ.get("AUTO3D_WEB_SEARCH_TIMEOUT", "10"))
MAX_RESULTS = int(os.environ.get("AUTO3D_WEB_SEARCH_MAX_RESULTS", "10"))


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    provider: str

    def serialise(self) -> dict:
        return asdict(self)


class WebSearch:
    """Fetches search results from configurable providers."""

    def __init__(self, serpapi_key: Optional[str] = None):
        self.serpapi_key = serpapi_key or os.environ.get("SERPAPI_API_KEY")

    def search_web(self, query: str, limit: int = MAX_RESULTS) -> List[SearchResult]:
        if not query or not query.strip():
            return []

        # Prefer SerpAPI when the key is configured; otherwise fallback to DuckDuckGo.
        if self.serpapi_key:
            results = self._search_serpapi(query, limit)
            if results:
                return results

        return self._search_duckduckgo(query, limit)

    def _search_serpapi(self, query: str, limit: int) -> List[SearchResult]:
        params = {
            "engine": os.environ.get("SERPAPI_ENGINE", "google"),
            "q": query,
            "api_key": self.serpapi_key,
            "num": min(limit, 10),  # SerpAPI caps at 10 per request for Google.
        }

        try:
            response = requests.get(SERPAPI_ENDPOINT, params=params, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[web_search] SerpAPI request failed: {exc}", file=sys.stderr)
            return []

        data = response.json()
        organic_results = data.get("organic_results", [])
        results: List[SearchResult] = []

        for item in organic_results[:limit]:
            title = item.get("title") or item.get("snippet") or "Untitled result"
            snippet = item.get("snippet", "") or item.get("title", "")
            link = item.get("link") or item.get("source") or ""
            if not link:
                continue
            results.append(
                SearchResult(
                    title=title.strip(),
                    url=link,
                    snippet=snippet.strip(),
                    provider="serpapi",
                )
            )

        return results

    def _search_duckduckgo(self, query: str, limit: int) -> List[SearchResult]:
        params = {
            "q": query,
            "format": "json",
            "no_html": "1",
            "no_redirect": "1",
        }

        try:
            response = requests.get(DUCKDUCKGO_ENDPOINT, params=params, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[web_search] DuckDuckGo request failed: {exc}", file=sys.stderr)
            return []

        data = response.json()
        results: List[SearchResult] = []

        abstract_text = data.get("AbstractText")
        abstract_url = data.get("AbstractURL")
        heading = data.get("Heading")
        if abstract_text and abstract_url:
            results.append(
                SearchResult(
                    title=(heading or abstract_url).strip(),
                    url=abstract_url,
                    snippet=abstract_text.strip(),
                    provider="duckduckgo",
                )
            )

        related_topics = data.get("RelatedTopics", [])
        results.extend(self._extract_duckduckgo_topics(related_topics))

        # Deduplicate by URL and trim to limit.
        unique_results = []
        seen_urls = set()
        for res in results:
            if res.url and res.url not in seen_urls:
                unique_results.append(res)
                seen_urls.add(res.url)
            if len(unique_results) >= limit:
                break

        return unique_results

    def _extract_duckduckgo_topics(self, topics: Iterable, depth: int = 0) -> List[SearchResult]:
        results: List[SearchResult] = []
        for entry in topics:
            if not isinstance(entry, dict):
                continue
            # Nested topics contain their own "Topics" list.
            nested = entry.get("Topics")
            if nested and depth < 3:
                results.extend(self._extract_duckduckgo_topics(nested, depth + 1))
                continue

            first_url = entry.get("FirstURL")
            text = entry.get("Text")
            if not first_url or not text:
                continue
            title = entry.get("Result") or text.split(" - ", 1)[0]
            snippet = text
            results.append(
                SearchResult(
                    title=str(title).strip(),
                    url=first_url,
                    snippet=str(snippet).strip(),
                    provider="duckduckgo",
                )
            )
        return results

    def fetch_results(self, search_results: Iterable[SearchResult]) -> List[SearchResult]:
        """Identity helper retained for compatibility."""
        return list(search_results)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Perform a lightweight web search for agent workflows.")
    parser.add_argument("query", help="Search query to execute.")
    parser.add_argument(
        "--limit",
        type=int,
        default=MAX_RESULTS,
        help=f"Maximum number of results to return (default: {MAX_RESULTS}).",
    )
    parser.add_argument(
        "--format",
        choices=("json", "lines"),
        default="json",
        help="Output format: JSON array or newline-delimited strings.",
    )
    args = parser.parse_args(argv)

    searcher = WebSearch()
    results = searcher.search_web(args.query, limit=args.limit)
    serialised = [res.serialise() for res in results]

    if args.format == "json":
        json.dump({"results": serialised}, sys.stdout)
        sys.stdout.write("\n")
    else:
        for item in serialised:
            sys.stdout.write(f"{item['title']} — {item['url']}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
