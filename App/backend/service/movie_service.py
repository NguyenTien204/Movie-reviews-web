from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from models import (
    Movie, Genre, MovieGenre, Trailer, ProductionCompany, MovieProductionCompany,
    ProductionCountry, MovieProductionCountry, SpokenLanguage, MovieSpokenLanguage,
    Collection, Rating, ReleaseCalendar, TrailerTypeEnum
)
from schema.movie_schema import (
    MovieDetail, MovieShortDetail, MovieTrailer, Genre as GenreSchema,
    ProductionCompany as ProductionCompanySchema, ProductionCountry as ProductionCountrySchema,
    SpokenLanguage as SpokenLanguageSchema, Collection as CollectionSchema,
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
            homepage=movie.homepage,
            poster_path=movie.poster_path,
            popularity=movie.popularity,
            adult=movie.adult,
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
        trailer = db.query(Trailer).filter(
            and_(
                Trailer.movie_id == movie_id,
                Trailer.site == 'YouTube'
            )
        ).order_by(Trailer.published_at.desc()).first()

        if not trailer:
            return []

        # ✳️ Chuyển thành dict, ép kiểu nếu cần
        trailer_dict = trailer.__dict__.copy()

        try:
            trailer_dict["type"] = TrailerTypeEnum(trailer_dict["type"])
        except ValueError:
            # Log cảnh báo nếu giá trị không hợp lệ
            print(f"[WARN] Trailer type '{trailer_dict['type']}' is invalid.")
            trailer_dict["type"] = None  # hoặc dùng default Enum

        return [MovieTrailer(**trailer_dict)]




