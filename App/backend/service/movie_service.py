from typing import List, Optional
from datetime import datetime
from schema.movie import MovieDetail, MovieShortDetail, MovieTrailer, Genre
from fastapi import HTTPException
from sqlalchemy import (
    create_engine, select, and_, desc, func, 
    Column, Integer, String, Text, Float, Boolean, 
    DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import sessionmaker, Session, relationship
from Data_Pipeline.config.postgres_config import PostgresConnection
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Movie(Base):
    __tablename__ = 'movies'
    movie_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    original_title = Column(String, nullable=False)
    overview = Column(Text)
    tagline = Column(Text)
    runtime = Column(Integer)
    homepage = Column(String)
    poster_path = Column(String)
    popularity = Column(Float)
    adult = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class MovieGenre(Base):
    __tablename__ = 'movie_genres'
    movie_id = Column(Integer, ForeignKey('movies.movie_id'), primary_key=True)
    genre_id = Column(Integer, ForeignKey('genres.genre_id'), primary_key=True)

class GenreModel(Base):
    __tablename__ = 'genres'
    genre_id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

class Trailer(Base):
    __tablename__ = 'trailers'
    id = Column(String, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.movie_id'))
    name = Column(String, nullable=False)
    site = Column(Enum('YouTube', 'Vimeo', name='site_enum'), nullable=False)
    key = Column(String, nullable=False)
    type = Column(Enum('Trailer', 'Teaser', 'Clip', 'Featurette', 
                      'Behind the Scenes', 'Bloopers', 'Opening Scene', 
                      'Ending Scene', 'Deleted Scene', name='trailer_type_enum'), nullable=False)
    official = Column(Boolean)
    published_at = Column(DateTime)
    size = Column(Integer)

class MovieService:
    def __init__(self):
        self.engine = create_engine(PostgresConnection.get_connection_string())
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
        
    async def get_movie_detail(self, movie_id: int) -> MovieDetail:
        db = next(self.get_db())
        try:
            movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
            if not movie:
                raise HTTPException(status_code=404, detail="Movie not found")

            genres = db.query(GenreModel).join(MovieGenre).filter(
                MovieGenre.movie_id == movie_id
            ).all()
            
            return MovieDetail(
                movie_id=movie.movie_id,
                title=movie.title,
                original_title=movie.original_title,
                overview=movie.overview,
                tagline=movie.tagline,
                runtime=movie.runtime,
                homepage=movie.homepage,
                poster_path=movie.poster_path,
                popularity=movie.popularity,
                adult=movie.adult,
                genres=[Genre(genre_id=g.genre_id, name=g.name) for g in genres],
                created_at=movie.created_at,
                updated_at=movie.updated_at
            )
        finally:
            db.close()

    async def get_movie_short_detail(self, movie_id: int) -> MovieShortDetail:
        db = next(self.get_db())
        try:
            movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
            if not movie:
                raise HTTPException(status_code=404, detail="Movie not found")

            return MovieShortDetail(
                movie_id=movie.movie_id,
                title=movie.title,
                poster_path=movie.poster_path,
                popularity=movie.popularity
            )
        finally:
            db.close()

    async def filter_movies(self, genre_ids: Optional[List[int]] = None,
                          year: Optional[int] = None,
                          sort_by: str = "popularity.desc",
                          page: int = 1,
                          limit: int = 20) -> List[MovieShortDetail]:
        db = next(self.get_db())
        try:
            query = db.query(Movie)

            if genre_ids:
                query = query.join(MovieGenre).filter(MovieGenre.genre_id.in_(genre_ids))
            
            if sort_by == "popularity.desc":
                query = query.order_by(desc(Movie.popularity))
            elif sort_by == "popularity.asc":
                query = query.order_by(Movie.popularity)
            
            offset = (page - 1) * limit
            movies = query.offset(offset).limit(limit).all()

            return [
                MovieShortDetail(
                    movie_id=movie.movie_id,
                    title=movie.title,
                    poster_path=movie.poster_path,
                    popularity=movie.popularity
                )
                for movie in movies
            ]
        finally:
            db.close()

    async def get_trending_movies(self) -> List[MovieShortDetail]:
        """
        Get trending movies based on popularity (temporary implementation)
        Will be replaced with ML model recommendations later
        """
        db = next(self.get_db())
        try:
            movies = db.query(Movie).order_by(desc(Movie.popularity)).limit(20).all()
            return [
                MovieShortDetail(
                    movie_id=movie.movie_id,
                    title=movie.title,
                    poster_path=movie.poster_path,
                    popularity=movie.popularity
                )
                for movie in movies
            ]
        finally:
            db.close()

    async def get_movie_trailers(self, movie_id: int) -> List[MovieTrailer]:
        db = next(self.get_db())
        try:
            trailers = db.query(Trailer).filter(
                and_(
                    Trailer.movie_id == movie_id,
                    Trailer.type == 'Trailer'
                )
            ).all()

            if not trailers:
                return []

            return [MovieTrailer(
                id=t.id,
                movie_id=t.movie_id,
                name=t.name,
                site=t.site,
                key=t.key,
                type=t.type,
                official=t.official,
                published_at=t.published_at,
                size=t.size
            ) for t in trailers]
        finally:
            db.close()

    async def get_movie_recommendations(self, movie_id: int) -> List[MovieShortDetail]:
        """
        Get movie recommendations based on genre similarity (temporary implementation)
        Will be replaced with ML model recommendations later
        """
        db = next(self.get_db())
        try:
            movie_genres = db.query(MovieGenre.genre_id).filter(MovieGenre.movie_id == movie_id).subquery()
            
            recommended_movies = db.query(Movie).join(MovieGenre).filter(
                and_(
                    MovieGenre.genre_id.in_(movie_genres),
                    Movie.movie_id != movie_id
                )
            ).order_by(
                desc(Movie.popularity)
            ).limit(20).all()

            return [MovieShortDetail(
                movie_id=movie.movie_id,
                title=movie.title,
                poster_path=movie.poster_path,
                popularity=movie.popularity
            ) for movie in recommended_movies]
        finally:
            db.close()
