from .base import Base
from .enums import WatchlistStatusEnum, TrailerTypeEnum, SiteEnum, EventTypeEnum
from .user import (
    User, WatchHistory, Rating, Comment, 
    CommentVote, Follow, Watchlist
)
from .movie import (
    Movie, Genre, MovieGenre, Trailer,
    ProductionCompany, MovieProductionCompany,
    ProductionCountry, MovieProductionCountry,
    SpokenLanguage, MovieSpokenLanguage,
    Collection
)
from .event import DimSession, FactUserEvent

# Export all models for easy access
__all__ = [
    'Base',
    # Enums
    'WatchlistStatusEnum', 'TrailerTypeEnum', 'SiteEnum', 'EventTypeEnum',
    # User related
    'User', 'WatchHistory', 'Rating', 'Comment', 'CommentVote', 'Follow', 'Watchlist',
    # Movie related
    'Movie', 'Genre', 'MovieGenre', 'Trailer',
    'ProductionCompany', 'MovieProductionCompany',
    'ProductionCountry', 'MovieProductionCountry',
    'SpokenLanguage', 'MovieSpokenLanguage',
    'Collection',
    # Event related
    'DimSession', 'FactUserEvent'
]
