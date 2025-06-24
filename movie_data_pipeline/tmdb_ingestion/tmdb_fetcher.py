import requests
import os
import sys
import time
# Thêm thư mục gốc vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.tmdb_config import TMDB_API_KEY, TMDB_BASE_URL



def get_popular_movie_ids(pages=5):
    """
    Lấy danh sách movie_id từ API popular. Mỗi trang có ~20 phim.
    """
    ids = set()
    for page in range(1, pages + 1):
        url = f"{TMDB_BASE_URL}/movie/popular"
        params = {
            "api_key": TMDB_API_KEY,
            "page": page
        }
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            page_ids = [movie["id"] for movie in data.get("results", [])]
            ids.update(page_ids)
        else:
            print(f"⚠️ Error on page {page}: {resp.status_code}")
        time.sleep(0.25)  # tránh rate-limit
    return list(ids)

def discover_movies_by_year(year, page):
    url = f"{TMDB_BASE_URL}/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "sort_by": "popularity.desc",
        "primary_release_year": year,
        "page": page
    }
    resp = safe_request(url, params)
    if resp:
        data = resp.json()
        return {
            "ids": [movie["id"] for movie in data["results"]],
            "total_pages": data.get("total_pages", 0)
        }
    return {"ids": [], "total_pages": 0}


    #years = range(1990, 2020)
    #movie_ids = []
    #for year in years:
    #    for page in range(1, 6):  # mỗi năm lấy 5 trang ~ 100 phim
    #        ids = discover_movies_by_year(year, page)
    #        movie_ids.extend(ids)
    #        time.sleep(0.2)

def safe_request(url, params):
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

def fetch_movie_details(movie_id):
    """
    Lấy chi tiết một bộ phim qua movie_id, bao gồm cả videos (trailers).
    """
    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "append_to_response": "videos"
    }
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"❌ Failed to fetch movie {movie_id}: {resp.status_code}")
        return None

