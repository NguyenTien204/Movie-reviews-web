# save_to_mongo.py

from pymongo import MongoClient
import time
from tmdb_fetcher import TMDBClient


class MongoSaver:
    def __init__(self, db_name="tmdb_data", collection_name="raw_movies", uri="mongodb://localhost:27017/"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def save_movies(self, data_list):
        if data_list:
            self.collection.insert_many(data_list)
            print(f"✅ Saved {len(data_list)} movies to MongoDB '{self.db.name}.{self.collection.name}'")

    def get_existing_movie_ids(self):
        return set(doc["id"] for doc in self.collection.find({}, {"id": 1}))


if __name__ == "__main__":
        # ========================== #
    #     Lấy phim phổ biến   #
    #movie_ids = get_popular_movie_ids(pages=5)  # → khoảng 100 id phim
    # Khởi tạo client API và MongoDB
    tmdb = TMDBClient()
    mongo = MongoSaver()

    # ========================== #
    #     Lấy phim theo năm     #
    years = range(1990, 2020)
    movie_ids = []

    for year in years:
        print(f"\n📅 Collecting movies for year: {year}")
        total_pages = 1
        for page in range(1, 51):
            result = tmdb.discover_movies_by_year(year, page)
            ids = result["ids"]

            if page == 1:
                total_pages = result["total_pages"]
                print(f"🔢 Total pages for {year}: {total_pages}")

            if not ids:
                break

            movie_ids.extend(ids)
            print(f"✅ Year {year} | Page {page} | {len(ids)} movies")

            if page >= total_pages:
                break
            time.sleep(0.2)

    # ========================== #
    #     Xử lý ID phim         #
    movie_ids = list(set(movie_ids))
    print(f"\n🎯 Total collected movie IDs: {len(movie_ids)}")

    existing_ids = mongo.get_existing_movie_ids()
    new_ids = [mid for mid in movie_ids if mid not in existing_ids]
    print(f"🧹 New IDs to fetch: {len(new_ids)}")

    # ========================== #
    #     Lấy chi tiết phim     #
    all_movies = []
    for idx, mid in enumerate(new_ids):
        movie = tmdb.fetch_movie_details(mid)
        if movie:
            all_movies.append(movie)
            print(f"[{idx + 1}/{len(new_ids)}] ✅ {movie['title']}")
        else:
            print(f"[{idx + 1}/{len(new_ids)}] ❌ Failed to fetch ID {mid}")
        time.sleep(0.25)

    # ========================== #
    #     Lưu vào MongoDB       #
    mongo.save_movies(all_movies)
    print(f"\n📦 Done: {len(all_movies)} movies saved to MongoDB.")
