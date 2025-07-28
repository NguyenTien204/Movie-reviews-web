from pydantic import BaseModel
from datetime import datetime


class UserRating(BaseModel):
    user_id: int
    movie_id: int
    score: float
    class Config:
        from_attributes = True

class UserComment(BaseModel):
    user_id: int
    movie_id: int
    body: str

    class Config:
        from_attributes = True

class DeleteComment(BaseModel):
    id: str
    user_id: int

    class Config:
        from_attributes = True
