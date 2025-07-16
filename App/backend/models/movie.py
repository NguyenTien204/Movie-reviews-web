# Database Models
from typing import List, Optional
from datetime import datetime
from fastapi import Depends, HTTPException
from sqlalchemy import (
    create_engine, select, and_, desc, func, Column, Integer, String, Text,
    Float, Boolean, DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import sessionmaker, Session, declarative_base


Base = declarative_base()

class Movie(Base):
    __tablename__ = 'movies'
    movie_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    original_title = Column(String, nullable=False)
    overview = Column(Text)
    tagline = Column(Text)
    runtime = Column(Integer)
    homepage = Column(String)
    poster_path = Column(String)
    popularity = Column(Float)
    adult = Column(Boolean)
    release_date = Column(DateTime)  # ✅ Thêm trường này nếu bạn muốn filter theo năm
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class MovieGenre(Base):
    __tablename__ = 'movie_genres'
    movie_id = Column(Integer, ForeignKey('movies.movie_id'), primary_key=True)
    genre_id = Column(Integer, ForeignKey('genres.genre_id'), primary_key=True)

class GenreModel(Base):
    __tablename__ = 'genres'
    genre_id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

class Trailer(Base):
    __tablename__ = 'trailers'
    id = Column(String, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.movie_id'))
    name = Column(String, nullable=False)
    site = Column(Enum('YouTube', 'Vimeo', name='site_enum'), nullable=False)
    key = Column(String, nullable=False)
    type = Column(Enum('Trailer', 'Teaser', 'Clip', 'Featurette',
                      'Behind the Scenes', 'Bloopers', 'Opening Scene',
                      'Ending Scene', 'Deleted Scene', name='trailer_type_enum'), nullable=False)
    official = Column(Boolean)
    published_at = Column(DateTime)
    size = Column(Integer)