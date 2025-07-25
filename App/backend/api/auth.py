# routers/auth_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schema.user_schema import UserCreate, UserLogin, Token, UserOut
from service.auth_service import register, login
from dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/register", response_model=Token)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return register(user, db)

@router.post("/login", response_model=Token)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    return login(user, db)

@router.get("/me", response_model=UserOut)
def get_me(current_user=Depends(get_current_user)):
    return current_user
