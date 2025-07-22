from fastapi import APIRouter, Depends
from typing import List
from schema.movie_schema import MovieDetail, MovieShortDetail, MovieFilter, MovieTrailer
from service.movie_service import MovieService
from sqlalchemy.orm import Session


router = APIRouter()
movie_service = MovieService()

@router.get("/movies/filter", response_model=List[MovieShortDetail])
async def filter_movies(filter_params: MovieFilter = Depends(), movie_service: MovieService = Depends()):
    """Filter movies based on various criteria"""
    return await movie_service.filter_movies(filter_params)

@router.get("/movies/trending", response_model=List[MovieShortDetail])
async def trending_movies(db: Session = Depends(movie_service.get_db)):
    return await movie_service.get_trending_movies(db)


@router.get("/movies/{movie_id}/recommendations", response_model=List[MovieShortDetail])
async def get_movie_recommendations(movie_id: int, movie_service: MovieService = Depends()):
    """Get movie recommendations based on a movie"""
    return await movie_service.get_movie_recommendations(movie_id)

@router.get("/movies/{movie_id}", response_model=MovieDetail)
async def get_full_movie(movie_id: int, db: Session = Depends(movie_service.get_db)):
    print("get_full_movie called with movie_id:", movie_id)
    service = MovieService()
    return await service.get_movie_detail(movie_id, db)


@router.get("/shortdetail/{movie_id}", response_model=MovieShortDetail)
async def get_movie_short_detail(movie_id: int, movie_service: MovieService = Depends()):
    """Get short details of a movie for home page display"""
    return await movie_service.get_movie_short_detail(movie_id)

@router.get("/movies/{movie_id}/trailer", response_model=List[MovieTrailer])
async def get_movie_trailers(movie_id: int, movie_service: MovieService = Depends()):
    """Get available trailers for a movie"""
    return await movie_service.get_movie_trailers(movie_id)

