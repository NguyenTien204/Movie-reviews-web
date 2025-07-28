from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, nulls_last
from typing import List
from models import Movie, Genre, MovieGenre, Rating, CosineSimilarityResult
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
                ],

            )
            for movie in movies
        ]

    @staticmethod
    async def get_trending_movies(db: Session) -> List[MovieShortDetail]:
        # Subquery tính average rating
        avg_rating_subq = (
            db.query(
                Rating.movie_id,
                func.avg(Rating.score).label("average_rating")
            )
            .group_by(Rating.movie_id)
            .subquery()
        )

        # JOIN Movie với subquery và ORDER BY average_rating DESC
        movies = (
            db.query(Movie, avg_rating_subq.c.average_rating)
            .outerjoin(avg_rating_subq, Movie.movie_id == avg_rating_subq.c.movie_id)
            .order_by(nulls_last(desc(avg_rating_subq.c.average_rating)))
            .limit(20)
            .all()
        )

        result = []
        for movie, avg_rating in movies:
            genres = db.query(Genre).join(MovieGenre).filter(MovieGenre.movie_id == movie.movie_id).all()
            result.append(
                MovieShortDetail(
                    movie_id=movie.movie_id,
                    title=movie.title,
                    poster_path=movie.poster_path,
                    popularity=movie.popularity,
                    genres=[
                        GenreSchema(genre_id=g.genre_id, name=g.name)
                        for g in genres
                    ],
                    average_rating=round(avg_rating or 0.0, 1)
                )
            )
        return result


    @staticmethod
    async def get_similar_movies_cosine(movie_id: int, db: Session, top_k: int = 10) -> List[MovieShortDetail]:
        # Lấy các phim tương tự nhất từ bảng cosine similarity
        results = db.query(
            CosineSimilarityResult.movie_id_2,
            CosineSimilarityResult.similarity
        ).filter(
            CosineSimilarityResult.movie_id_1 == movie_id
        ).order_by(desc(CosineSimilarityResult.similarity)).limit(top_k).all()

        if not results:
            return []

        similar_movie_ids = [r.movie_id_2 for r in results]
        similarity_map = {r.movie_id_2: r.similarity for r in results}

        movies = db.query(Movie).filter(Movie.movie_id.in_(similar_movie_ids)).all()

        return [
            MovieShortDetail(
                movie_id=m.movie_id,
                title=m.title,
                poster_path=m.poster_path,
                popularity=m.popularity,
                similarity=round(similarity_map.get(m.movie_id, 0), 4),
                genres=[
                    GenreSchema(
                        genre_id=g.genre_id,
                        name=g.name
                    )
                    for g in db.query(Genre)
                                .join(MovieGenre, Genre.genre_id == MovieGenre.genre_id)
                                .filter(MovieGenre.movie_id == m.movie_id).all()
                ]
            )
            for m in movies
        ]
