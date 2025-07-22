from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from typing import List
from models import Movie, Genre, MovieGenre
from schema.movie_schema import (
    MovieShortDetail, MovieFilter, Genre as GenreSchema
)

class MovieDiscoveryService:

    @staticmethod
    async def filter_movies(filter_params: MovieFilter, db: Session) -> List[MovieShortDetail]:
        query = db.query(Movie)

        if filter_params.genre:
            query = query.join(MovieGenre).filter(MovieGenre.genre_id.in_(filter_params.genre))
        if filter_params.year:
            query = query.filter(func.extract('year', Movie.release_date) == filter_params.year)

        if filter_params.sort_by == "popularity.desc":
            query = query.order_by(desc(Movie.popularity))
        elif filter_params.sort_by == "popularity.asc":
            query = query.order_by(Movie.popularity)

        offset = (filter_params.page - 1) * filter_params.limit
        movies = query.offset(offset).limit(filter_params.limit).all()

        return [
            MovieShortDetail(
                movie_id=movie.movie_id,
                title=movie.title,
                poster_path=movie.poster_path,
                popularity=movie.popularity,
                genres=[
                    GenreSchema(genre_id=g.genre_id, name=g.name)
                    for g in db.query(Genre).join(MovieGenre).filter(MovieGenre.movie_id == movie.movie_id).all()
                ]
            )
            for movie in movies
        ]

    @staticmethod
    async def get_trending_movies(db: Session) -> List[MovieShortDetail]:
        movies = db.query(Movie).order_by(desc(Movie.popularity)).limit(20).all()
        return [
            MovieShortDetail(
                movie_id=movie.movie_id,
                title=movie.title,
                poster_path=movie.poster_path,
                popularity=movie.popularity,
                genres=[
                    GenreSchema(genre_id=g.genre_id, name=g.name)
                    for g in db.query(Genre).join(MovieGenre).filter(MovieGenre.movie_id == movie.movie_id).all()
                ]
            )
            for movie in movies
        ]

    @staticmethod
    async def get_movie_recommendations(movie_id: int, db: Session) -> List[MovieShortDetail]:
        movie_genres = db.query(MovieGenre.genre_id).filter(MovieGenre.movie_id == movie_id).subquery()
        recommended_movies = db.query(Movie).join(MovieGenre).filter(
            and_(
                MovieGenre.genre_id.in_(movie_genres),
                Movie.movie_id != movie_id
            )
        ).order_by(desc(Movie.popularity)).limit(20).all()

        return [
            MovieShortDetail(
                movie_id=m.movie_id,
                title=m.title,
                poster_path=m.poster_path,
                popularity=m.popularity,
                genres=[
                    GenreSchema(genre_id=g.genre_id, name=g.name)
                    for g in db.query(Genre).join(MovieGenre).filter(MovieGenre.movie_id == m.movie_id).all()
                ]
            )
            for m in recommended_movies
        ]
