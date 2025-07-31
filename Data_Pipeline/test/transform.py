"""
Tối ưu hóa chuyển đổi JSON movie data vào PostgreSQL
Sử dụng asyncpg cho hiệu suất cao và pydantic cho validation
"""

import asyncio
import asyncpg
import json
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
import logging

# =====================
# PYDANTIC MODELS
# =====================

class Genre(BaseModel):
    id: int
    name: str

class ProductionCompany(BaseModel):
    id: int
    name: str
    logo_path: Optional[str] = None
    origin_country: Optional[str] = None

class ProductionCountry(BaseModel):
    iso_3166_1: str
    name: str

class SpokenLanguage(BaseModel):
    iso_639_1: str
    name: str
    english_name: Optional[str] = None

class Video(BaseModel):
    id: str
    name: str
    key: str
    site: str
    size: Optional[int] = None
    type: str
    official: Optional[bool] = None
    published_at: Optional[str] = None

    @validator('published_at')
    def parse_published_at(cls, v):
        if v:
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            return dt.replace(tzinfo=None)  # Chuyển về offset-naive
        return None

class Movie(BaseModel):
    id: int
    title: str
    original_title: str
    overview: Optional[str] = None
    tagline: Optional[str] = None
    runtime: Optional[int] = None
    homepage: Optional[str] = None
    poster_path: Optional[str] = None
    popularity: Optional[float] = None
    adult: Optional[bool] = False
    genres: List[Genre] = []
    production_companies: List[ProductionCompany] = []
    production_countries: List[ProductionCountry] = []
    spoken_languages: List[SpokenLanguage] = []
    videos: Optional[Dict[str, List[Video]]] = None

# =====================
# DATABASE CONVERTER
# =====================

class MovieDBConverter:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None

    async def connect(self):
        """Tạo connection pool cho hiệu suất cao"""
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=5,
            max_size=20,
            command_timeout=60
        )

    async def close(self):
        """Đóng connection pool"""
        if self.pool:
            await self.pool.close()

    async def insert_movie_batch(self, movies_data: List[Dict[str, Any]]) -> None:
        """
        Insert batch movies với transaction để đảm bảo tính toàn vẹn
        """
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Parse và validate data
                movies = [Movie(**movie_data) for movie_data in movies_data]

                # Chuẩn bị data cho batch insert
                await self._batch_insert_reference_data(conn, movies)
                await self._batch_insert_movies(conn, movies)
                await self._batch_insert_relations(conn, movies)

    async def _batch_insert_reference_data(self, conn, movies: List[Movie]):
        """Insert reference data (genres, companies, countries, languages)"""

        # Collect unique reference data
        genres = set()
        companies = {}
        countries = {}
        languages = {}

        for movie in movies:
            for genre in movie.genres:
                genres.add((genre.id, genre.name))

            for company in movie.production_companies:
                companies[company.id] = (company.name, company.origin_country, company.logo_path)

            for country in movie.production_countries:
                countries[country.iso_3166_1] = country.name

            for lang in movie.spoken_languages:
                languages[lang.iso_639_1] = lang.name

        # Batch insert với ON CONFLICT DO NOTHING
        if genres:
            await conn.executemany(
                "INSERT INTO genres (genre_id, name) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                list(genres)
            )

        if companies:
            company_data = [(k, v[0], v[1], v[2]) for k, v in companies.items()]
            await conn.executemany(
                """INSERT INTO production_companies (company_id, name, origin_country, logo_path)
                   VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING""",
                company_data
            )

        if countries:
            country_data = [(k, v) for k, v in countries.items()]
            await conn.executemany(
                "INSERT INTO production_countries (iso_3166_1, name) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                country_data
            )

        if languages:
            lang_data = [(k, v) for k, v in languages.items()]
            await conn.executemany(
                "INSERT INTO spoken_languages (iso_639_1, name) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                lang_data
            )

    async def _batch_insert_movies(self, conn, movies: List[Movie]):
        """Batch insert movies"""
        movie_data = [
            (
                movie.id, movie.title, movie.original_title, movie.overview,
                movie.tagline, movie.runtime, movie.homepage, movie.poster_path,
                movie.popularity, movie.adult
            )
            for movie in movies
        ]

        await conn.executemany(
            """INSERT INTO movies
               (movie_id, title, original_title, overview, tagline, runtime,
                homepage, poster_path, popularity, adult)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
               ON CONFLICT (movie_id) DO UPDATE SET
               title = EXCLUDED.title,
               original_title = EXCLUDED.original_title,
               overview = EXCLUDED.overview,
               tagline = EXCLUDED.tagline,
               runtime = EXCLUDED.runtime,
               homepage = EXCLUDED.homepage,
               poster_path = EXCLUDED.poster_path,
               popularity = EXCLUDED.popularity,
               adult = EXCLUDED.adult,
               updated_at = CURRENT_TIMESTAMP""",
            movie_data
        )

    async def _batch_insert_relations(self, conn, movies: List[Movie]):
        """Insert relation tables"""

        # Movie-Genre relations
        genre_relations = []
        company_relations = []
        country_relations = []
        language_relations = []
        trailer_data = []

        for movie in movies:
            # Genres
            for genre in movie.genres:
                genre_relations.append((movie.id, genre.id))

            # Companies
            for company in movie.production_companies:
                company_relations.append((movie.id, company.id))

            # Countries
            for country in movie.production_countries:
                country_relations.append((movie.id, country.iso_3166_1))

            # Languages
            for lang in movie.spoken_languages:
                language_relations.append((movie.id, lang.iso_639_1))

            # Trailers
            if movie.videos and 'results' in movie.videos:
                for video in movie.videos['results']:
                    trailer_data.append((
                        video.id, movie.id, video.name, video.site, video.key,
                        video.type, video.official, video.published_at, video.size
                    ))

        # Batch insert relations
        if genre_relations:
            await conn.executemany(
                "INSERT INTO movie_genres (movie_id, genre_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                genre_relations
            )

        if company_relations:
            await conn.executemany(
                "INSERT INTO movie_production_companies (movie_id, company_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                company_relations
            )

        if country_relations:
            await conn.executemany(
                "INSERT INTO movie_production_countries (movie_id, iso_3166_1) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                country_relations
            )

        if language_relations:
            await conn.executemany(
                "INSERT INTO movie_spoken_languages (movie_id, iso_639_1) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                language_relations
            )

        if trailer_data:
            await conn.executemany(
                """INSERT INTO trailers (id, movie_id, name, site, key, type, official, published_at, size)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) ON CONFLICT DO NOTHING""",
                trailer_data
            )

# =====================
# UTILITY FUNCTIONS
# =====================

def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    """Load và parse JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Nếu là single object, wrap thành list
        return data if isinstance(data, list) else [data]

def process_json_batch(json_data: List[Dict[str, Any]], batch_size: int = 1000):
    """Chia data thành các batch nhỏ để xử lý"""
    for i in range(0, len(json_data), batch_size):
        yield json_data[i:i + batch_size]

# =====================
# MAIN EXECUTION
# =====================

async def main():
    """Main function để test"""
    # Cấu hình database
    DB_URL = "postgresql://postgres:141124@localhost:5432/movie_db"

    # Khởi tạo converter
    converter = MovieDBConverter(DB_URL)
    await converter.connect()

    try:
        # Load JSON data
        movies_data = load_json_file(r'D:\WorkSpace\Do-an-2\Data_Pipeline\test\tmdb_data.raw_movies.json')

        # Process theo batch
        for batch in process_json_batch(movies_data, batch_size=1000):
            await converter.insert_movie_batch(batch)
            print(f"Processed batch of {len(batch)} movies")

        print("✅ Hoàn thành import dữ liệu!")

    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        await converter.close()

# Chạy script
if __name__ == "__main__":
    asyncio.run(main())

# =====================
# REQUIREMENTS.txt
# =====================
"""
asyncpg>=0.28.0
pydantic>=2.0.0
"""
