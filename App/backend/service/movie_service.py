from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from service.user_service import CommentService
from models import (
    Movie, Genre, MovieGenre, Trailer, ProductionCompany, MovieProductionCompany,
    ProductionCountry, MovieProductionCountry, SpokenLanguage, MovieSpokenLanguage,
    Collection, Rating, ReleaseCalendar
)
from schema.movie_schema import (
    MovieDetail, MovieShortDetail, MovieTrailer, Genre as GenreSchema,
    ProductionCompany as ProductionCompanySchema, ProductionCountry as ProductionCountrySchema,
    SpokenLanguage as SpokenLanguageSchema, Collection as CollectionSchema,
    Comment as CommentSchema, Rating as RatingSchema
)

class MovieDisplayService:
    
    @staticmethod
    async def get_movie_detail(movie_id: int, db: Session) -> MovieDetail:
        movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        genres = db.query(Genre).join(MovieGenre).filter(MovieGenre.movie_id == movie_id).all()
        genres = [GenreSchema(genre_id=g.genre_id, name=g.name) for g in genres]

        production_companies = db.query(ProductionCompany).join(MovieProductionCompany)\
            .filter(MovieProductionCompany.movie_id == movie_id).all()
        production_countries = db.query(ProductionCountry).join(MovieProductionCountry)\
            .filter(MovieProductionCountry.movie_id == movie_id).all()
        spoken_languages = db.query(SpokenLanguage).join(MovieSpokenLanguage)\
            .filter(MovieSpokenLanguage.movie_id == movie_id).all()
        collections = db.query(Collection).filter(Collection.movie_id == movie_id).all()

        
        comments = await CommentService.get_movie_comments(movie_id, db)

        ratings = db.query(Rating).filter(Rating.movie_id == movie_id).all()
        average_rating = db.query(func.avg(Rating.score)).filter(Rating.movie_id == movie_id).scalar() or 0.0

        release_date = db.query(ReleaseCalendar)\
            .filter(ReleaseCalendar.movie_id == movie_id)\
            .order_by(ReleaseCalendar.release_date).first()
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
            comments=[CommentSchema.model_validate(c, from_attributes=True) for c in comments],
            ratings=[RatingSchema.model_validate(r, from_attributes=True) for r in ratings],
            average_rating=round(average_rating, 1)
        )

    @staticmethod
    async def get_movie_short_detail(movie_id: int, db: Session) -> MovieShortDetail:
        movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        genres = db.query(Genre).join(MovieGenre).filter(MovieGenre.movie_id == movie_id).all()
        average_rating = db.query(func.avg(Rating.score)).filter(Rating.movie_id == movie_id).scalar() or 0.0
        return MovieShortDetail(
            movie_id=movie.movie_id,
            title=movie.title,
            poster_path=movie.poster_path,
            popularity=movie.popularity,
            genres=[GenreSchema(genre_id=g.genre_id, name=g.name) for g in genres],
            average_rating=round(average_rating, 1)
        )

    @staticmethod
    async def get_movie_trailers(movie_id: int, db: Session):
        trailers = db.query(Trailer).filter(
            and_(Trailer.movie_id == movie_id, Trailer.type == 'Trailer')
        ).all()
        return [
            MovieTrailer.model_validate(t, from_attributes=True) for t in trailers
        ]
