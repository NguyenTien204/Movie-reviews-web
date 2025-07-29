# schema/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserLog(BaseModel):
    action_type: str
    movie_id: Optional[int] = None
    search_term: Optional[str] = None
    rating: Optional[float] = None
    dwell_time: Optional[int] = None
    timestamp: Optional[datetime] = None
    user_agent: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: Optional[datetime] = None

#class Comment(BaseModel):
#    id: str
#    user_id: int
#    body: str
#    created_at: datetime
#    is_deleted: bool = False
#
#
#class Rating(BaseModel):
#    rating_id: int
#    user_id: int
#    score: float
#    created_at: datetime
