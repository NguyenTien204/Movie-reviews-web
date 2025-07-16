from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, 
    DateTime, ForeignKey, Enum, Date, CHAR
)
from sqlalchemy.orm import relationship
from .base import Base
from .enums import SiteEnum, TrailerTypeEnum

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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    genres = relationship("MovieGenre", back_populates="movie")
    watch_history = relationship("WatchHistory", back_populates="movie")
    ratings = relationship("Rating", back_populates="movie")
    comments = relationship("Comment", back_populates="movie")
    watchlist = relationship("Watchlist", back_populates="movie")
    events = relationship("FactUserEvent", back_populates="movie")
    trailers = relationship("Trailer", back_populates="movie")
    production_companies = relationship("MovieProductionCompany", back_populates="movie")
    production_countries = relationship("MovieProductionCountry", back_populates="movie")
    spoken_languages = relationship("MovieSpokenLanguage", back_populates="movie")
    collections = relationship("Collection", back_populates="movie")

class Genre(Base):
    __tablename__ = 'genres'
    
    genre_id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    movies = relationship("MovieGenre", back_populates="genre")

class MovieGenre(Base):
    __tablename__ = 'movie_genres'
    
    movie_id = Column(Integer, ForeignKey('movies.movie_id', ondelete='CASCADE'), primary_key=True)
    genre_id = Column(Integer, ForeignKey('genres.genre_id', ondelete='CASCADE'), primary_key=True)
    
    movie = relationship("Movie", back_populates="genres")
    genre = relationship("Genre", back_populates="movies")

class Trailer(Base):
    __tablename__ = 'trailers'
    
    id = Column(String, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.movie_id', ondelete='CASCADE'))
    name = Column(String, nullable=False)
    site = Column(Enum(SiteEnum), nullable=False)
    key = Column(String, nullable=False)
    type = Column(Enum(TrailerTypeEnum), nullable=False)
    official = Column(Boolean)
    published_at = Column(DateTime)
    size = Column(Integer)

    movie = relationship("Movie", back_populates="trailers")

class ProductionCompany(Base):
    __tablename__ = 'production_companies'
    
    company_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    origin_country = Column(CHAR(2))
    logo_path = Column(String)
    
    movies = relationship("MovieProductionCompany", back_populates="company")

class MovieProductionCompany(Base):
    __tablename__ = 'movie_production_companies'
    
    movie_id = Column(Integer, ForeignKey('movies.movie_id', ondelete='CASCADE'), primary_key=True)
    company_id = Column(Integer, ForeignKey('production_companies.company_id'), primary_key=True)
    
    movie = relationship("Movie", back_populates="production_companies")
    company = relationship("ProductionCompany", back_populates="movies")

class ProductionCountry(Base):
    __tablename__ = 'production_countries'
    
    iso_3166_1 = Column(CHAR(2), primary_key=True)
    name = Column(String, nullable=False)
    movies = relationship("MovieProductionCountry", back_populates="country")

class MovieProductionCountry(Base):
    __tablename__ = 'movie_production_countries'
    
    movie_id = Column(Integer, ForeignKey('movies.movie_id', ondelete='CASCADE'), primary_key=True)
    iso_3166_1 = Column(CHAR(2), ForeignKey('production_countries.iso_3166_1'), primary_key=True)
    
    movie = relationship("Movie", back_populates="production_countries")
    country = relationship("ProductionCountry", back_populates="movies")

class SpokenLanguage(Base):
    __tablename__ = 'spoken_languages'
    
    iso_639_1 = Column(CHAR(2), primary_key=True)
    name = Column(String, nullable=False)
    movies = relationship("MovieSpokenLanguage", back_populates="language")

class MovieSpokenLanguage(Base):
    __tablename__ = 'movie_spoken_languages'
    
    movie_id = Column(Integer, ForeignKey('movies.movie_id', ondelete='CASCADE'), primary_key=True)
    iso_639_1 = Column(CHAR(2), ForeignKey('spoken_languages.iso_639_1'), primary_key=True)
    
    movie = relationship("Movie", back_populates="spoken_languages")
    language = relationship("SpokenLanguage", back_populates="movies")

class Collection(Base):
    __tablename__ = 'collections'
    
    collection_id = Column(String, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.movie_id', ondelete='CASCADE'))
    name = Column(String)
    backdrop_path = Column(Text)
    poster_path = Column(Text)
    
    movie = relationship("Movie", back_populates="collections")
