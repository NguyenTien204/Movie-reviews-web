from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.config import get_db
from service.search_service import Movie_Search_service
from schema.movie_schema import MovieShortDetail
from typing import List

router = APIRouter()

@router.get("/movies-search", response_model=List[MovieShortDetail])
async def search_movies(
    keyword: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    return await Movie_Search_service.search_by_name(keyword, db)


