import uuid
from typing import List
from fastapi import HTTPException
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from models.user import Comment, CommentVote, Rating
from schema.review import UserComment as CommentSchema, UserRating as RatingSchema

class CommentService:
    @staticmethod
    async def get_movie_comments(movie_id: int, db: Session) -> List[CommentSchema]:
        """Get all comments for a movie with vote counts"""
        comments = db.query(Comment, func.count(CommentVote.comment_id).label('vote_count'))\
            .outerjoin(CommentVote)\
            .filter(
                Comment.movie_id == movie_id,
                Comment.is_deleted.is_(False)
            )\
            .group_by(Comment.id)\
            .order_by(desc(Comment.created_at))\
            .all()

        return [
            CommentSchema(
                id=comment.id,
                user_id=comment.user_id,
                movie_id = comment.movie_id,
                body=comment.body,
                created_at=comment.created_at,
                is_deleted=comment.is_deleted,
                vote_count=vote_count
            ) for comment, vote_count in comments
        ]

    @staticmethod
    async def AddOrUpdateComment(user_id: int,  movie_id: int, body: str, db: Session):
        existing_comment = db.query(Comment).filter_by(user_id = user_id, movie_id = movie_id, is_deleted= False).first()

        if existing_comment:
            return await CommentService.edit_comment(user_id, movie_id, body, db)
        else:
            return await CommentService.add_comment(user_id, movie_id, body, db)

    @staticmethod
    async def add_comment(user_id: int, movie_id: int, body: str, db: Session) -> CommentSchema:
        """Add a new comment to a movie"""
        comment = Comment(
            id=str(uuid.uuid4()),
            movie_id=movie_id,
            user_id=user_id,
            body=body
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return CommentSchema.model_validate(comment, from_attributes=True)

    @staticmethod
    async def edit_comment(user_id: int, movie_id: int, body: str, db: Session):
        comment = db.query(Comment).filter_by(user_id = user_id, movie_id = movie_id, is_deleted = False).first()
        if not comment:
            raise ValueError("Không tìm thấy comment để cập nhật")

        comment.body = body
        db.commit()
        db.refresh(comment)
        return CommentSchema.model_validate(comment, from_attributes=True)

    @staticmethod
    async def delete_comment(comment_id: str, user_id: int, db: Session) -> bool:
        """Soft delete a comment"""
        comment = db.query(Comment)\
            .filter(
                Comment.id == comment_id,
                Comment.user_id == user_id,
                Comment.is_deleted.is_(False)
            )\
            .first()

        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        comment.is_deleted = True
        db.commit()
        return True


class RatingService:
    @staticmethod
    async def AddOrUpdateRating(user_id: int, movie_id: int, score: float, db: Session):
        existing_rating = db.query(Rating).filter_by(user_id=user_id, movie_id=movie_id, is_deleted=False).first()

        if existing_rating:
            return await RatingService.EditRating(user_id, movie_id, score, db)
        else:
            return await RatingService.AddRating(user_id, movie_id, score, db)

    @staticmethod
    async def AddRating(user_id: int, movie_id: int, score: float, db: Session):
        ratings = Rating(
            movie_id = movie_id,
            user_id = user_id,
            score = score
        )
        db.add(ratings)
        db.commit()
        db.refresh(ratings)
        return RatingSchema.model_validate(ratings, from_attributes=True)

    @staticmethod
    async def EditRating(user_id: int, movie_id: int, score: float, db: Session):
        rating = db.query(Rating).filter_by(user_id=user_id, movie_id=movie_id, is_deleted=False).first()

        if not rating:
            raise ValueError("Không tìm thấy đánh giá để cập nhật")

        rating.score = score
        rating.timestamp = datetime.now(timezone.utc)
        db.commit()
        db.refresh(rating)
        return RatingSchema.model_validate(rating, from_attributes=True)
