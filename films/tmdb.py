import random
import time

import requests
from django.conf import settings

BASE_URL = "https://api.themoviedb.org/3"
TIMEOUT = 10 # Seconds until timeout
MAX_RETRIES = 5

class TMDBError(Exception):
    """TMDB kept failing after all retries."""

class TMDBClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {settings.TMDB_TOKEN}",
            "accept": "application/json",
        })

    def _get(self, path, params=None):
        url = f"{BASE_URL}{path}"
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, params=params, timeout=TIMEOUT)
            except (requests.Timeout, requests.ConnectionError):
                self._sleep(attempt)
                continue

            if response.status_code == 404:
                return None
            if response.status_code == 429 or response.status_code >= 500:
                self._sleep(attempt, response.headers.get("Retry-After"))
                continue

            response.raise_for_status()
            return response.json()
        raise TMDBError(f"Gave up on {path} after {MAX_RETRIES} attempts")

    @staticmethod
    def _sleep(attempt, retry_after=None):
        delay = 2 ** attempt + random.random()
        try:
            delay = max(delay, float(retry_after))
        except (TypeError, ValueError):
            pass
        time.sleep(delay)

    def get_movie(self, tmdb_id):
        return self._get(
            f"/movie/{tmdb_id}",
            params={"append_to_response": "credits", "language": "en-US"},
        )

    def get_genres(self):
        return self._get("/genre/movie/list", params={"language": "en-US"})

    def get_popular(self, page):
        return self._get("/movie/popular", params={"language": "en-US", "page": page})