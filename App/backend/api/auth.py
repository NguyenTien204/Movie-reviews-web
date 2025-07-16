from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from flask_jwt_extended import create_access_token
from pydantic import BaseModel
router = APIRouter()





