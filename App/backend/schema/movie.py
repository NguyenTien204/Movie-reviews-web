from pydantic import BaseModel
from typing import List, Optional

class MovieBase(BaseModel):
    title: str
    overview: str
    release_date: str
    poster_path: Optional[str]
    vote_average: float
    vote_count: int

class MovieDetail(MovieBase):
    id: int
    genres: List[str]
    runtime: Optional[int]
    budget: Optional[int]
    revenue: Optional[int]
    tagline: Optional[str]

class MovieShortDetail(BaseModel):
    id: int
    title: str
    poster_path: Optional[str]
    vote_average: float
    release_date: str

class MovieFilter(BaseModel):
    genre: Optional[str] = None
    year: Optional[int] = None
    sort_by: Optional[str] = "popularity.desc"
    page: int = 1

class MovieTrailer(BaseModel):
    id: int
    key: str
    site: str
    type: str
