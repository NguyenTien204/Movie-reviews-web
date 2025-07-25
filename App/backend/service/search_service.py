# service/movie_search_service.py
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List
from models import Movie, Genre, MovieGenre, Rating
from schema.movie_schema import (
    MovieShortDetail, Genre as GenreSchema,
)
class Movie_Search_service:
    @staticmethod
    async def search_by_name(keyword: str, db: Session) -> List[MovieShortDetail]:
        keyword_like = f"%{keyword.lower()}%"

        movies = (
            db.query(Movie)
            .filter(
                or_(
                    func.lower(Movie.title).like(keyword_like),
                    func.lower(Movie.original_title).like(keyword_like)
                )
            )
            .order_by(Movie.popularity.desc())
            .limit(20)
            .all()
        )

        movie_ids = [m.movie_id for m in movies]
        movie_genres = (
            db.query(MovieGenre.movie_id, Genre)
            .join(Genre, Genre.genre_id == MovieGenre.genre_id)
            .filter(MovieGenre.movie_id.in_(movie_ids))
            .all()
        )
        from collections import defaultdict
        genre_map = defaultdict(list)
        for movie_id, genre in movie_genres:
            genre_map[movie_id].append(GenreSchema(genre_id=genre.genre_id, name=genre.name))

        return [
            MovieShortDetail(
                movie_id=m.movie_id,
                title=m.title,
                poster_path=m.poster_path,
                popularity=m.popularity,
                genres=genre_map[m.movie_id],
                average_rating=round(
                    db.query(func.avg(Rating.score)).filter(Rating.movie_id == m.movie_id).scalar() or 0.0, 1
                )
            )
            for m in movies
        ]
