# api/auth_api.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schema.user import UserCreate, UserLogin, Token
from service import auth_service
from db.config import SessionLocal

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register(user_data, db)

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    return auth_service.login(user_data, db)
