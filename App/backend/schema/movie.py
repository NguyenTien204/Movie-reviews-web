from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Genre(BaseModel):
    genre_id: int
    name: str

class MovieBase(BaseModel):
    title: str
    original_title: str
    overview: Optional[str] = None
    release_date: datetime
    poster_path: Optional[str] = None
    popularity: Optional[float] = None
    adult: Optional[bool] = False

class MovieDetail(MovieBase):
    movie_id: int
    genres: List[Genre]
    runtime: Optional[int] = None
    homepage: Optional[str] = None
    tagline: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy

class MovieShortDetail(BaseModel):
    movie_id: int
    title: str
    poster_path: Optional[str] = None
    popularity: Optional[float] = None
    genres: List[Genre]

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