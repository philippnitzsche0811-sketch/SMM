"""
User Models für Authentication
"""
from pydantic import BaseModel, Field
from typing import List

class UserRegister(BaseModel):
    """User Registration Request"""
    email: str  # Geändert von EmailStr zu str
    password: str = Field(..., min_length=6, description="Mindestens 6 Zeichen")

class UserLogin(BaseModel):
    """User Login Request"""
    email: str  # Geändert von EmailStr zu str
    password: str

class UserResponse(BaseModel):
    """User Response (ohne Passwort)"""
    user_id: str
    email: str
    created_at: str
    connected_platforms: List[str] = []

class TokenResponse(BaseModel):
    """Token Response nach Login/Register"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserInDB(BaseModel):
    """User in Datenbank"""
    user_id: str
    email: str
    hashed_password: str
    created_at: str
    connected_platforms: List[str] = []
