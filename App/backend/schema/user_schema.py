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
    action_type: str  # "click", "hover", etc.
    target: str       # e.g., "movie_card"
    movie_id: Optional[int]
    timestamp: datetime
    user_agent: Optional[str]

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
