from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.config import get_db
from typing import List, Dict

from schema.review import UserComment as CommentSchema, UserRating as RatingSchema
from models import Comment, Rating
from service.user_service import RatingService, CommentService


router = APIRouter()

@router.post("/user/rating", response_model= RatingSchema)
async def rate_movie(user_id: int, movie_id: int, score: float, db: Session = Depends(get_db)):
    return await RatingService.AddOrUpdateRating(user_id, movie_id, score, db)

@router.post("/user/comment", response_model= CommentSchema)
async def add_comment(user_id: int, movie_id: int, body: str, db: Session = Depends(get_db)):
    return await CommentService.add_comment(user_id, movie_id, body, db)

@router.post("/user/delete/comment", response_model= bool)
async def delete_comment(id, user_id: int, db: Session = Depends(get_db)):
    return await CommentService.delete_comment(id, user_id, db)
