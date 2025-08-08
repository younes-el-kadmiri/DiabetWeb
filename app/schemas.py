from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    nom: str
    prenom: str
    specialite: str
    email: EmailStr
    telephone: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str
