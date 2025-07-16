from typing import List
from fastapi import Depends, HTTPException
from sqlalchemy import (
    create_engine, and_, desc, func
)
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from schema.movie import MovieDetail, MovieShortDetail, MovieTrailer, Genre, MovieFilter
from db.config import PostgresConnection
from App.backend.models.base_movie import Movie, MovieGenre, GenreModel, Trailer
# Define SQLAlchemy Base
Base = declarative_base()


class MovieService:
    def __init__(self):
        # Create engine with connection pooling
        self.engine = create_engine(
            PostgresConnection.get_connection_string(),
            pool_size=5,  # Connection pool size
            max_overflow=10,  # Allow overflow connections
            pool_timeout=30  # Timeout for getting a connection from pool
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_db(self) -> Session:
        """Dependency for getting database session"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def get_movie_detail(self, movie_id: int, db: Session = Depends(get_db)) -> MovieDetail:
        """Get detailed information about a specific movie"""
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

    async def get_movie_short_detail(self, movie_id: int, db: Session = Depends(get_db)) -> MovieShortDetail:
        """Get short details of a movie for home page display"""
        movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        genres = db.query(GenreModel).join(MovieGenre).filter(
            MovieGenre.movie_id == movie_id
        ).all()
        
        return MovieShortDetail(
            movie_id=movie.movie_id,
            title=movie.title,
            poster_path=movie.poster_path,
            popularity=movie.popularity,
            genres=[Genre(genre_id=g.genre_id, name=g.name) for g in genres]
        )

    async def filter_movies(self, filter_params: MovieFilter = Depends(), db: Session = Depends(get_db)) -> List[MovieShortDetail]:
        """Filter movies based on various criteria"""
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
                genres=[Genre(genre_id=g.genre_id, name=g.name) for g in db.query(GenreModel)
                        .join(MovieGenre)
                        .filter(MovieGenre.movie_id == movie.movie_id).all()]
            )
            for movie in movies
        ]

    async def get_trending_movies(self, db: Session = Depends(get_db)) -> List[MovieShortDetail]:
        """Get trending movies based on popularity"""
        movies = db.query(Movie).order_by(desc(Movie.popularity)).limit(20).all()
        return [
            MovieShortDetail(
                movie_id=movie.movie_id,
                title=movie.title,
                poster_path=movie.poster_path,
                popularity=movie.popularity,
                genres=[Genre(genre_id=g.genre_id, name=g.name) for g in db.query(GenreModel)
                        .join(MovieGenre)
                        .filter(MovieGenre.movie_id == movie.movie_id).all()]
            )
            for movie in movies
        ]

    async def get_movie_trailers(self, movie_id: int, db: Session = Depends(get_db)) -> List[MovieTrailer]:
        """Get available trailers for a movie"""
        trailers = db.query(Trailer).filter(
            and_(
                Trailer.movie_id == movie_id,
                Trailer.type == 'Trailer'
            )
        ).all()

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

    async def get_movie_recommendations(self, movie_id: int, db: Session = Depends(get_db)) -> List[MovieShortDetail]:
        """Get movie recommendations based on genre similarity"""
        movie_genres = db.query(MovieGenre.genre_id).filter(MovieGenre.movie_id == movie_id).subquery()
        
        recommended_movies = db.query(Movie).join(MovieGenre).filter(
            and_(
                MovieGenre.genre_id.in_(movie_genres),
                Movie.movie_id != movie_id
            )
        ).order_by(desc(Movie.popularity)).limit(20).all()

        return [
            MovieShortDetail(
                movie_id=movie.movie_id,
                title=movie.title,
                poster_path=movie.poster_path,
                popularity=movie.popularity,
                genres=[Genre(genre_id=g.genre_id, name=g.name) for g in db.query(GenreModel)
                        .join(MovieGenre)
                        .filter(MovieGenre.movie_id == movie.movie_id).all()]
            )
            for movie in recommended_movies
        ]