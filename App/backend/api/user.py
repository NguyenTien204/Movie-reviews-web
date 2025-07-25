from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.config import get_db
from typing import List

from schema.review import ReviewCreate, RatingCreate
from models import Comment, Rating
from service.user_service import CommentService

router = APIRouter()

@router.get("/movies/{movie_id}/comment", response_model= )