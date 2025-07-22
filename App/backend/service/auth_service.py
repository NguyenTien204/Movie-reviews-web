# services/auth_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from schema.user import UserCreate, UserLogin
from models import User
from core.security import hash_password, verify_password, create_access_token
from datetime import timedelta


def register(user_data: UserCreate, db: Session):
    user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": new_user.username}, expires_delta=timedelta(minutes=30))
    return {"access_token": token}

def login(user_data: UserLogin, db: Session):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=30))
    return {"access_token": token}
