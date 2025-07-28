from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, SmallInteger, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
from .enums import WatchlistStatusEnum, EventTypeEnum

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(320), unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    watch_history = relationship("WatchHistory", back_populates="user")
    ratings = relationship("Rating", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    watchlist = relationship("Watchlist", back_populates="user")
    sessions = relationship("DimSession", back_populates="user")
    events = relationship("FactUserEvent", back_populates="user")

    # Following relationships
    following = relationship('User',
                           secondary='follows',
                           primaryjoin='User.id==follows.c.following_user_id',
                           secondaryjoin='User.id==follows.c.followed_user_id',
                           backref='followers')

class WatchHistory(Base):
    __tablename__ = 'watch_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    movie_id = Column(Integer, ForeignKey('movies.movie_id', ondelete='CASCADE'))
    watched_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    user = relationship("User", back_populates="watch_history")
    movie = relationship("Movie", back_populates="watch_history")

class Rating(Base):
    __tablename__ = 'ratings'

    rating_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    movie_id = Column(Integer, ForeignKey('movies.movie_id', ondelete='CASCADE'))
    score = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    is_deleted = Column(Boolean, default=False)

    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(UUID, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    movie_id = Column(Integer, ForeignKey('movies.movie_id', ondelete='CASCADE'))
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    user = relationship("User", back_populates="comments")
    movie = relationship("Movie", back_populates="comments")
    votes = relationship("CommentVote", back_populates="comment")

class CommentVote(Base):
    __tablename__ = 'comment_votes'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    comment_id = Column(UUID, ForeignKey('comments.id', ondelete='CASCADE'), primary_key=True)
    vote_type = Column(SmallInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    comment = relationship("Comment", back_populates="votes")

class Follow(Base):
    __tablename__ = 'follows'

    following_user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    followed_user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Watchlist(Base):
    __tablename__ = 'watchlist'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    movie_id = Column(Integer, ForeignKey('movies.movie_id', ondelete='CASCADE'))
    status = Column(Enum(WatchlistStatusEnum), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watchlist")
    movie = relationship("Movie", back_populates="watchlist")
