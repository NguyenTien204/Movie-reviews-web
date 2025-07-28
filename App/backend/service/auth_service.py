# services/auth_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta

from schema.user_schema import UserCreate, UserLogin
from models import User
from core.security import hash_password, verify_password, create_access_token


def register(user_data: UserCreate, db: Session):
    user = db.query(User).filter(User.username == user_data.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": new_user.username, "user_id": new_user.id}, expires_delta=timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}


def login(user_data: UserLogin, db: Session):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.username, "user_id": user.id}, expires_delta=timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}


def get_user_by_username(username: str, db: Session):
    return db.query(User).filter(User.username == username).first()
