import requests
import time
TMDB_API_KEY = '358fe0abcb8f482817d2372f11dcfb7a'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

class TMDBClient:
    def __init__(self, api_key=TMDB_API_KEY, base_url=TMDB_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url

    def _safe_request(self, endpoint, params):
        url = f"{self.base_url}/{endpoint}"
        for attempt in range(3):
            try:
                resp = requests.get(url, params=params, timeout=10)
                if resp.status_code == 200:
                    return resp
                elif resp.status_code == 429:
                    print("⚠️ Hit rate limit. Waiting 5s before retrying...")
                    time.sleep(5)
                elif 500 <= resp.status_code < 600:
                    print(f"⚠️ Server error {resp.status_code}. Retrying...")
                    time.sleep(2)
            except requests.RequestException as e:
                print(f"❌ Request error: {e}. Retrying...")
                time.sleep(2)
        return None

    def get_popular_movie_ids(self, pages=5):
        """
        Lấy danh sách movie_id từ API popular. Mỗi trang có ~20 phim.
        """
        ids = set()
        for page in range(1, pages + 1):
            params = {
                "api_key": self.api_key,
                "page": page
            }
            resp = self._safe_request("movie/popular", params)
            if resp:
                data = resp.json()
                page_ids = [movie["id"] for movie in data.get("results", [])]
                ids.update(page_ids)
            else:
                print(f"⚠️ Error on page {page}")
            time.sleep(0.25)
        return list(ids)

    def discover_movies_by_year(self, year, page):
        """
        Lấy danh sách movie_id theo năm phát hành và thứ tự phổ biến.
        """
        params = {
            "api_key": self.api_key,
            "sort_by": "popularity.desc",
            "primary_release_year": year,
            "page": page
        }
        resp = self._safe_request("discover/movie", params)
        if resp:
            data = resp.json()
            return {
                "ids": [movie["id"] for movie in data.get("results", [])],
                "total_pages": data.get("total_pages", 0)
            }
        return {"ids": [], "total_pages": 0}

    def fetch_movie_details(self, movie_id):
        """
        Lấy chi tiết một bộ phim qua movie_id, bao gồm cả videos (trailers).
        """
        params = {
            "api_key": self.api_key,
            "append_to_response": "videos"
        }
        resp = self._safe_request(f"movie/{movie_id}", params)
        if resp:
            return resp.json()
        else:
            print(f"❌ Failed to fetch movie {movie_id}")
            return None
