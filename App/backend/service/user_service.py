import uuid
from typing import List
from fastapi import HTTPException
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from models.user import Comment, CommentVote
from schema.movie_schema import Comment as CommentSchema, CommentVote as CommentVoteSchema

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
                body=comment.body,
                created_at=comment.created_at,
                is_deleted=comment.is_deleted,
                vote_count=vote_count
            ) for comment, vote_count in comments
        ]

    @staticmethod
    async def add_comment(movie_id: int, user_id: int, body: str, db: Session) -> CommentSchema:
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

    @staticmethod
    async def vote_comment(comment_id: str, user_id: int, vote_type: int, db: Session) -> CommentVoteSchema:
        """Add or update a vote on a comment"""
        if vote_type not in [-1, 1]:
            raise HTTPException(status_code=400, detail="Invalid vote type")
            
        # Check if comment exists and is not deleted
        comment = db.query(Comment)\
            .filter(
                Comment.id == comment_id,
                Comment.is_deleted.is_(False)
            ).first()
            
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        # Check existing vote
        vote = db.query(CommentVote)\
            .filter(
                CommentVote.comment_id == comment_id,
                CommentVote.user_id == user_id
            ).first()
            
        if vote:
            if vote.vote_type == vote_type:
                # Remove vote if same type
                db.delete(vote)
                db.commit()
                return None
            # Update vote type if different
            vote.vote_type = vote_type
        else:
            # Create new vote
            vote = CommentVote(
                comment_id=comment_id,
                user_id=user_id,
                vote_type=vote_type
            )
            db.add(vote)
            
        db.commit()
        if vote:
            db.refresh(vote)
            return CommentVoteSchema.model_validate(vote, from_attributes=True)
        return None
