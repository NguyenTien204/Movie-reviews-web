from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.config import get_db
from typing import List

from schema.review import UserComment, UserRating
from models import Comment, Rating
from service.user_service import RatingService

router = APIRouter()

