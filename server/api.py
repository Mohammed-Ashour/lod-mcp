"""LOD API client with rate limiting and caching"""
from typing import Any, Dict
import time
import requests

try:
    from server.cache import cache
except ImportError:
    from cache import cache


# Rate limiting
_last_request_time = 0
_min_request_interval = 0.1


def _rate_limited_request(url: str, headers: Dict[str, str]) -> requests.Response:
    """Make rate-limited request to LOD API"""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < _min_request_interval:
        time.sleep(_min_request_interval - elapsed)
    _last_request_time = time.time()
    return requests.get(url, headers=headers, timeout=10)


def cached_api_call(endpoint: str, params: str, url: str) -> Any:
    """Make cached API call with rate limiting"""
    cached = cache.get(endpoint, params)
    if cached is not None:
        return cached
    
    response = _rate_limited_request(url, {"accept": "application/json"})
    
    if response.status_code == 200:
        data = response.json()
        cache.set(endpoint, params, data)
        return data
    return None


def search_api(query: str) -> Any:
    """Search for words"""
    params = f"query={query}&lang=lb"
    url = f"https://lod.lu/api/en/search?{params}"
    return cached_api_call("search", params, url)


def suggest_api(prefix: str) -> Any:
    """Get autocomplete suggestions"""
    params = f"query={prefix}"
    url = f"https://lod.lu/api/en/suggest?{params}"
    return cached_api_call("suggest", params, url)


def entry_api(lod_id: str) -> Any:
    """Get full entry details"""
    url = f"https://lod.lu/api/lb/entry/{lod_id}"
    return cached_api_call("entry", lod_id, url)
