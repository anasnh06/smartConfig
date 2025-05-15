from __future__ import annotations
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserShort(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nom d'utilisateur")
    email: EmailStr = Field(..., description="Adresse e-mail")
    is_active: bool = Field(default=True, description="Utilisateur actif ou non")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Mot de passe de l'utilisateur")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    creator: Optional["UserShort"] = None
    updater: Optional["UserShort"] = None

    class Config:
        from_attributes = True
