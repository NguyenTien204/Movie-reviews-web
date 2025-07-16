from pydantic import BaseModel

class ReviewCreate(BaseModel):
    movie_id: int
    review_text: str
    rating: float