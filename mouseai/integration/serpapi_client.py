import requests
from typing import Dict, Any


def serpapi_about_carousel(query: str, api_key: str, engine: str = "google") -> Dict[str, Any]:
    if not api_key:
        raise ValueError("SERPAPI_API_KEY is missing")

    url = "https://serpapi.com/search.json"
    params = {
        "engine": engine,
        "q": query,
        "api_key": api_key,
        "about-carousel": "true",
    }

    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    return {
        "search_metadata": data.get("search_metadata"),
        "about_carousel": data.get("about_carousel", {}),
        "organic_results": data.get("organic_results", []),
    }
