from typing import List
from fastapi import Depends, HTTPException
from sqlalchemy import create_engine, and_, desc, func
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from schema.movie_schema import (
    MovieDetail,
    MovieShortDetail,
    MovieTrailer,
    MovieFilter,
    Genre as GenreSchema,
    ProductionCompany as ProductionCompanySchema,
    ProductionCountry as ProductionCountrySchema,
    SpokenLanguage as SpokenLanguageSchema,
    Collection as CollectionSchema,
    Rating as RatingSchema,
    Comment as CommentSchema
)
from db.config import PostgresConnection
from models import (Movie, MovieGenre, Genre, Trailer,
    ProductionCompany, MovieProductionCompany, ProductionCountry,
    MovieProductionCountry, SpokenLanguage, MovieSpokenLanguage, 
    Collection, Rating, ReleaseCalendar)


# Define SQLAlchemy Base
Base = declarative_base()
class MovieService:
    def __init__(self):
        self.engine = create_engine(
            PostgresConnection.get_connection_string(),
            pool_size=5,  
            max_overflow=10, 
            pool_timeout=30  
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

    async def get_movie_detail(self, movie_id: int, db: Session) -> MovieDetail:
        """Get detailed information about a specific movie"""
        # Get base movie info
        movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        # Get genres
        genres = db.query(Genre).join(MovieGenre).filter(MovieGenre.movie_id == movie_id).all()
        genres = [GenreSchema(genre_id=g.genre_id, name=g.name) for g in genres]

        # Get production companies
        production_companies = db.query(ProductionCompany)\
            .join(MovieProductionCompany)\
            .filter(MovieProductionCompany.movie_id == movie_id).all()

        # Get production countries
        production_countries = db.query(ProductionCountry)\
            .join(MovieProductionCountry)\
            .filter(MovieProductionCountry.movie_id == movie_id).all()

        # Get spoken languages
        spoken_languages = db.query(SpokenLanguage)\
            .join(MovieSpokenLanguage)\
            .filter(MovieSpokenLanguage.movie_id == movie_id).all()

        # Get collections
        collections = db.query(Collection)\
            .filter(Collection.movie_id == movie_id).all()

        # Get comments using CommentService
        from App.backend.service.user_service import CommentService
        comments = await CommentService.get_movie_comments(movie_id, db)

        # Get ratings and calculate average
        ratings = db.query(Rating)\
            .filter(Rating.movie_id == movie_id).all()
        
        average_rating = db.query(func.avg(Rating.score))\
            .filter(Rating.movie_id == movie_id)\
            .scalar() or 0.0

        # Get release date (using first available release date)
        release_date = db.query(ReleaseCalendar)\
            .filter(ReleaseCalendar.movie_id == movie_id)\
            .order_by(ReleaseCalendar.release_date)\
            .first()

        if not release_date:
            raise HTTPException(status_code=404, detail="Release date not found")

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
            created_at=movie.created_at,
            updated_at=movie.updated_at,
            genres=genres,
            release_date=release_date.release_date,
            production_companies=[
                ProductionCompanySchema.model_validate(pc, from_attributes=True)
                for pc in production_companies
            ],
            production_countries=[
                ProductionCountrySchema.model_validate(pc, from_attributes=True)
                for pc in production_countries
            ],
            spoken_languages=[
                SpokenLanguageSchema.model_validate(sl, from_attributes=True)
                for sl in spoken_languages
            ],
            collections=[
                CollectionSchema.model_validate(c, from_attributes=True)
                for c in collections
            ],
            comments=[
                CommentSchema.model_validate(c, from_attributes=True)
                for c in comments
            ],
            ratings=[
                RatingSchema.model_validate(r, from_attributes=True)
                for r in ratings
            ],
            average_rating=round(average_rating, 1)
        )

    async def get_movie_short_detail(self, movie_id: int, db: Session = Depends(get_db)) -> MovieShortDetail:
        """Get short details of a movie for home page display"""
        movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        genres = db.query(Genre).join(MovieGenre).filter(MovieGenre.movie_id == movie_id).all()
        genres=[GenreSchema(genre_id=g.genre_id, name=g.name) for g in genres]

        
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
                genres=[Genre(genre_id=g.genre_id, name=g.name) for g in db.query(Genre)
                        .join(MovieGenre)
                        .filter(MovieGenre.movie_id == movie.movie_id).all()]
            )
            for movie in movies
        ]

    async def get_trending_movies(self, db: Session) -> List[MovieShortDetail]:
        """Get trending movies based on popularity"""
        movies = db.query(Movie).order_by(desc(Movie.popularity)).limit(20).all()
        return [
            MovieShortDetail(
                movie_id=movie.movie_id,
                title=movie.title,
                poster_path=movie.poster_path,
                popularity=movie.popularity,
                genres=[GenreSchema(genre_id=g.genre_id, name=g.name) for g in db.query(Genre)
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
                genres=[GenreSchema(genre_id=g.genre_id, name=g.name) for g in db.query(Genre)
                        .join(MovieGenre)
                        .filter(MovieGenre.movie_id == movie.movie_id).all()]

            )
            for movie in recommended_movies
        ]