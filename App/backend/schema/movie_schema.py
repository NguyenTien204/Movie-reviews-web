from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Genre(BaseModel):
    genre_id: int
    name: str
    class Config:
        from_attributes = True


class MovieBase(BaseModel):
    title: str
    original_title: str
    overview: Optional[str] = None
    release_date: datetime
    poster_path: Optional[str] = None
    popularity: Optional[float] = None
    adult: Optional[bool] = False

class ProductionCompany(BaseModel):
    company_id: int
    name: str
    origin_country: Optional[str] = None
    logo_path: Optional[str] = None

class ProductionCountry(BaseModel):
    iso_3166_1: str
    name: str

class SpokenLanguage(BaseModel):
    iso_639_1: str 
    name: str

class Collection(BaseModel):
    collection_id: str
    name: str
    backdrop_path: Optional[str] = None
    poster_path: Optional[str] = None

class CommentVote(BaseModel):
    user_id: int
    comment_id: str
    vote_type: int
    created_at: datetime

    class Config:
        from_attributes = True

class Comment(BaseModel):
    id: str
    user_id: int
    body: str
    created_at: datetime
    is_deleted: bool = False
    votes: List[CommentVote] = []
    vote_count: Optional[int] = 0

class Rating(BaseModel):
    rating_id: int
    user_id: int
    score: float
    created_at: datetime

class MovieDetail(MovieBase):
    movie_id: int
    genres: List[Genre]
    production_companies: List[ProductionCompany]
    production_countries: List[ProductionCountry]
    spoken_languages: List[SpokenLanguage]
    collections: List[Collection]
    average_rating: Optional[float] = None
    
    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy

class MovieShortDetail(BaseModel):
    movie_id: int
    title: str
    poster_path: Optional[str] = None
    popularity: Optional[float] = None
    genres: List[Genre]
    average_rating: Optional[float]

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy

class MovieFilter(BaseModel):
    genre: Optional[List[int]] = None  # List of genre_ids
    year: Optional[int] = None
    sort_by: Optional[str] = "popularity.desc"
    page: int = 1
    limit: int = 20

class TrailerType(str, Enum):
    TRAILER = "Trailer"
    TEASER = "Teaser"
    CLIP = "Clip"
    FEATURETTE = "Featurette"
    BEHIND_THE_SCENES = "Behind the Scenes"
    BLOOPERS = "Bloopers"
    OPENING_SCENE = "Opening Scene"
    ENDING_SCENE = "Ending Scene"
    DELETED_SCENE = "Deleted Scene"

class SiteType(str, Enum):
    YOUTUBE = "YouTube"
    VIMEO = "Vimeo"

class MovieTrailer(BaseModel):
    id: str
    movie_id: int
    name: str
    site: SiteType
    key: str
    type: TrailerType
    official: Optional[bool] = None
    published_at: Optional[datetime] = None
    size: Optional[int] = None

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy