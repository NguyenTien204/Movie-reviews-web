from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schema.movie import MovieDetail, MovieShortDetail, MovieFilter, MovieTrailer
from service.movie_service import MovieService

router = APIRouter()
movie_service = MovieService()

@router.get("/movies/{movie_id}", response_model=MovieDetail)
async def get_full_movie(movie_id: int):
    """Get detailed information about a specific movie"""
    return await movie_service.get_movie_detail(movie_id)

@router.get("/shortdetail/{movie_id}", response_model=MovieShortDetail)
async def get_movie_short_detail(movie_id: int):
    """Get short details of a movie for home page display"""
    return await movie_service.get_movie_short_detail(movie_id)

@router.get("/movies/filter", response_model=List[MovieShortDetail])
async def filter_movies(filter_params: MovieFilter = Depends()):
    """Filter movies based on various criteria"""
    return await movie_service.filter_movies(
        genre=filter_params.genre,
        year=filter_params.year,
        sort_by=filter_params.sort_by,
        page=filter_params.page
    )

@router.get("/movies/trending", response_model=List[MovieShortDetail])
async def get_trending_movies():
    """Get a list of trending movies"""
    return await movie_service.get_trending_movies()

@router.get("/movies/{movie_id}/trailer", response_model=List[MovieTrailer])
async def get_movie_trailers(movie_id: int):
    """Get available trailers for a movie"""
    return await movie_service.get_movie_trailers(movie_id)

@router.get("/movies/{movie_id}/recommendations", response_model=List[MovieShortDetail])
async def get_movie_recommendations(movie_id: int):
    """Get movie recommendations based on a movie"""
    return await movie_service.get_movie_recommendations(movie_id)