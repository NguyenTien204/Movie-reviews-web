from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
from .enums import EventTypeEnum

class DimSession(Base):
    __tablename__ = 'dim_session'
    
    session_id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    start_time = Column(DateTime, default=datetime.utcnow)
    browser = Column(String)
    os = Column(String)
    screen_resolution = Column(String)

    user = relationship("User", back_populates="sessions")
    events = relationship("FactUserEvent", back_populates="session")

class FactUserEvent(Base):
    __tablename__ = 'fact_user_event'
    
    event_id = Column(UUID, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    event_type = Column(Enum(EventTypeEnum), nullable=False)
    event_time = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String, ForeignKey('dim_session.session_id', ondelete='SET NULL'))
    movie_id = Column(Integer, ForeignKey('movies.movie_id', ondelete='SET NULL'))
    user_metadata = Column(JSON)
    processed = Column(Boolean, default=False)

    user = relationship("User", back_populates="events")
    session = relationship("DimSession", back_populates="events")
    movie = relationship("Movie", back_populates="events")
